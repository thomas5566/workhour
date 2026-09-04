"""Restore a prepared dump into isolated, disposable PostgreSQL 16 for rehearsal.

No published ports, external network, persistent volumes, or production passwords.
The source database is never contacted. Only the container created here is removed.
"""

import argparse
import hashlib
import json
import os
import secrets
import subprocess
import time
from pathlib import Path

from prepare_transfer import CLIENT_IMAGE, ROOT, run_checked


def verify(output):
    output = output.resolve(strict=True)
    if not output.is_relative_to((ROOT / "deploy/ubuntu/private").resolve()):
        raise ValueError("Expected a private transfer directory")
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    for name in ("workhour.dump", "workhour-source.tar.gz", "workhour.env"):
        with (output / name).open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if digest != manifest["files"][name]["sha256"]:
            raise ValueError("Transfer checksum mismatch")
    name = "workhour-restore-check-" + secrets.token_hex(6)
    created = False
    try:
        environment = {**os.environ, "POSTGRES_PASSWORD": secrets.token_hex(32),
                       "WORKHOUR_APP_PASSWORD": secrets.token_hex(32)}
        run_checked([
            "docker", "run", "--detach", "--name", name, "--network", "none",
            "--tmpfs", "/var/lib/postgresql/data:rw,size=512m",
            "--env", "POSTGRES_USER=workhour_admin", "--env", "POSTGRES_DB=workhour",
            "--env", "POSTGRES_PASSWORD", "--env", "WORKHOUR_APP_PASSWORD",
            "--mount", (f"type=bind,source={ROOT / 'deploy/ubuntu/init-app-role.sh'},"
                        "target=/docker-entrypoint-initdb.d/10-app-role.sh,readonly"),
            CLIENT_IMAGE,
        ], env=environment)
        created = True
        for _ in range(45):
            ready = subprocess.run([
                "docker", "exec", name, "pg_isready", "-h", "127.0.0.1",
                "-U", "workhour_admin", "-d", "workhour",
            ], capture_output=True, check=False)
            if ready.returncode == 0:
                break
            time.sleep(1)
        else:
            raise RuntimeError("Isolated PostgreSQL did not start")
        with (output / "workhour.dump").open("rb") as stream:
            run_checked([
                "docker", "exec", "--interactive", name, "pg_restore",
                "-U", "workhour_admin", "-d", "workhour", "--role=workhour",
                "--no-owner", "--no-privileges", "--single-transaction", "--exit-on-error",
            ], stdin=stream)

        def query(statement):
            return run_checked([
                "docker", "exec", name, "psql", "-X", "-A", "-t",
                "-v", "ON_ERROR_STOP=1", "-U", "workhour_admin", "-d", "workhour",
                "-c", statement,
            ]).decode().strip()

        restored = query("SELECT tablename FROM pg_tables WHERE schemaname='public' "
                         "ORDER BY tablename").splitlines()
        if set(restored) != set(manifest["table_counts"]):
            raise ValueError("Restored table set differs from source snapshot")
        for table, expected in manifest["table_counts"].items():
            identifier = '"' + table.replace('"', '""') + '"'
            actual = int(query(f'SELECT count(*) FROM "public".{identifier}'))
            if actual != expected:
                raise ValueError("Restored row count differs from source snapshot")
        revisions = query("SELECT version_num FROM public.alembic_version").splitlines()
        if set(revisions) != set(manifest["alembic_revisions"]):
            raise ValueError("Restored migration revision mismatch")
        if query("SELECT rolsuper,rolcreatedb,rolcreaterole FROM pg_roles "
                 "WHERE rolname='workhour'") != "f|f|f":
            raise ValueError("Application DB role has unexpected privileges")
        report = {"restore": "passed", "postgres_target_version": query("SHOW server_version"),
                  "matched_tables": len(restored), "all_snapshot_row_counts_match": True,
                  "alembic_revisions": revisions, "application_role_superuser": False,
                  "production_cutover": False}
        with (output / "restore-check.json").open("x", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2)
        print(json.dumps(report))
    finally:
        if created:
            # Unique container created above; its tmpfs holds disposable test data only.
            run_checked(["docker", "rm", "--force", name])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    try:
        verify(parser.parse_args().output)
    except Exception as error:  # noqa: BLE001 - redact secrets/data from all CLI failures
        raise SystemExit(
            f"Restore verification failed ({type(error).__name__})."
        ) from None
