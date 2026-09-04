"""Build a private rehearsal transfer; never stop writers or change the source DB.

Run with the project's development Python after restricting the output directory
ACL. Includes current working-tree code, preserved encryption keys, a consistent
whole-database dump, and row-count evidence from the SAME PostgreSQL snapshot.
"""

import argparse
import hashlib
import json
import os
import secrets
import subprocess
import tarfile
from datetime import UTC, datetime
from pathlib import Path

import psycopg2
from cryptography.fernet import Fernet
from dotenv import dotenv_values
from psycopg2 import sql
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[2]
CLIENT_IMAGE = "postgres:16-alpine"
# Deliberate allowlist: no .git, .env.production, node_modules, or unrelated files.
SOURCE_PATHS = [
    "backend/app", "backend/migrations", "backend/alembic.ini",
    "backend/requirements.txt", "backend/Dockerfile", "backend/.dockerignore",
    "frontend/src", "frontend/public", "frontend/package.json", "frontend/pnpm-lock.yaml",
    "frontend/pnpm-workspace.yaml", "frontend/.npmrc", "frontend/vite.config.js",
    "frontend/index.html", "frontend/Dockerfile", "frontend/nginx.conf",
    "frontend/.dockerignore", "deploy/ubuntu/compose.yml",
    "deploy/ubuntu/init-app-role.sh", "deploy/ubuntu/.env.example",
    "deploy/ubuntu/README.md",
]


def run_checked(command, **kwargs):
    result = subprocess.run(command, capture_output=True, check=False, **kwargs)
    if result.returncode:
        # Never echo subprocess output: a tool may include connection details.
        raise RuntimeError(f"{command[0]} operation failed (exit {result.returncode})")
    return result.stdout


def archive_filter(info):
    parts = Path(info.name).parts
    if info.issym() or info.islnk():
        raise ValueError("Symlinks are not allowed in a deployment source archive")
    if "__pycache__" in parts or info.name.endswith((".pyc", ".pyo")):
        return None
    if any(p.startswith(".env") and p != ".env.example" for p in parts):
        raise ValueError("Unexpected environment file in source allowlist")
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    info.mode = 0o755 if info.isdir() else 0o644
    return info


def dotenv_line(key, value):
    if any(char in value for char in ("\n", "\r", "\0")):
        raise ValueError("Environment value contains unsupported control characters")
    return f"{key}='{value.replace(chr(39), chr(92) + chr(39))}'\n"


def prepare(output):
    output = output.resolve(strict=True)
    private_root = (ROOT / "deploy/ubuntu/private").resolve()
    if not output.is_relative_to(private_root) or output == private_root:
        raise ValueError("Output must be a new restricted subdirectory under private/")
    if any(output.iterdir()):
        raise ValueError("Output must be empty; existing transfer packages are never overwritten")
    # This reviewed checkout can be owned by the Windows sandbox account.
    # Trust only this path for these read-only calls, never a global wildcard.
    git = ["git", "-c", f"safe.directory={ROOT.as_posix()}"]
    commit = run_checked([*git, "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
    branch = run_checked([*git, "branch", "--show-current"], cwd=ROOT).decode().strip()
    if branch != "refactor/vue3-fastapi-modernization":
        raise ValueError("The working tree is not on the authorized deployment branch")
    config = dotenv_values(ROOT / ".env.production")
    for key in ("EXTERNAL_DATABASE_URL", "SECRET_KEY", "DEVICE_CREDENTIAL_KEY",
                "ZABBIX_URL", "ZABBIX_TOKEN", "DEPLOY_EXPECTED_SOURCE_HOST",
                "DEPLOY_BIND_IP", "DEPLOY_PUBLIC_ORIGIN"):
        if not config.get(key):
            raise ValueError(f"Required configuration missing: {key}")
    Fernet(config["DEVICE_CREDENTIAL_KEY"].encode())  # Validate; do not replace it.
    url = make_url(config["EXTERNAL_DATABASE_URL"])
    if url.get_backend_name() != "postgresql":
        raise ValueError("Only PostgreSQL source databases are supported")
    # Fail closed if this rehearsal is accidentally aimed at a different source.
    if url.host != config["DEPLOY_EXPECTED_SOURCE_HOST"] or url.database != "workhour":
        raise ValueError("Source database differs from the verified migration source")

    with tarfile.open(output / "workhour-source.tar.gz", "x:gz") as archive:
        for relative in SOURCE_PATHS:
            archive.add(ROOT / relative, arcname=relative, filter=archive_filter)

    target = {
        "DB_ADMIN_PASSWORD": secrets.token_hex(32),
        "DB_APP_PASSWORD": secrets.token_hex(32),
        **{k: config[k] for k in ("SECRET_KEY", "DEVICE_CREDENTIAL_KEY",
                                  "ZABBIX_URL", "ZABBIX_TOKEN")},
        "ALGORITHM": config.get("ALGORITHM") or "HS256",
        "WEB_PORT": "8082", "BIND_IP": config["DEPLOY_BIND_IP"],
        "BACKEND_CORS_ORIGINS": json.dumps([config["DEPLOY_PUBLIC_ORIGIN"]]),
        "MONITORING_TIMEOUT_SECONDS": config.get("MONITORING_TIMEOUT_SECONDS") or "5",
        "BACKEND_IMAGE": "workhour-backend:local",
        "FRONTEND_IMAGE": "workhour-frontend:local",
    }
    with (output / "workhour.env").open("x", encoding="utf-8", newline="\n") as stream:
        stream.writelines(dotenv_line(key, value) for key, value in target.items())

    pg_environment = {
        "PGHOST": url.host, "PGPORT": str(url.port or 5432),
        "PGUSER": url.username, "PGPASSWORD": url.password or "", "PGDATABASE": url.database,
        "PGSSLMODE": str(url.query.get("sslmode", "prefer")), "PGCONNECT_TIMEOUT": "10",
    }
    connection = psycopg2.connect(
        host=url.host, port=url.port or 5432, user=url.username, password=url.password,
        dbname=url.database, connect_timeout=10, sslmode=pg_environment["PGSSLMODE"],
    )
    try:
        connection.set_session(isolation_level="REPEATABLE READ", readonly=True)
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL lock_timeout = '10s'")
            cursor.execute("SET LOCAL statement_timeout = '60s'")
            cursor.execute("SELECT pg_export_snapshot(), current_setting('server_version')")
            snapshot, version = cursor.fetchone()
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public' "
                           "ORDER BY tablename")
            tables = [row[0] for row in cursor.fetchall()]
            counts = {}
            for table in tables:
                cursor.execute(sql.SQL("SELECT count(*) FROM {}").format(
                    sql.Identifier("public", table)))
                counts[table] = cursor.fetchone()[0]
            cursor.execute("SELECT version_num FROM public.alembic_version")
            revisions = [row[0] for row in cursor.fetchall()]
            command = ["docker", "run", "--rm"]
            for key in pg_environment:
                command.extend(["--env", key])
            command.extend([
                "--mount", f"type=bind,source={output},target=/backup", CLIENT_IMAGE,
                "pg_dump", "--format=custom", "--no-owner", "--no-privileges",
                "--lock-wait-timeout=10s", f"--snapshot={snapshot}",
                "--file=/backup/workhour.dump",
            ])
            run_checked(command, env={**os.environ, **pg_environment})
    finally:
        connection.rollback()
        connection.close()

    run_checked([
        "docker", "run", "--rm", "--network", "none", "--mount",
        f"type=bind,source={output},target=/backup,readonly", CLIENT_IMAGE,
        "pg_restore", "--list", "/backup/workhour.dump",
    ])
    manifest = {
        "purpose": "rehearsal only; source writers were NOT stopped",
        "created_at": datetime.now(UTC).isoformat(), "postgres_source_version": version,
        "source_host": url.host, "database": url.database,
        "git_commit": commit,
        "git_branch": branch,
        "includes_working_tree_changes": True,
        "table_counts": counts, "alembic_revisions": revisions,
        "files": {},
    }
    for filename in ("workhour-source.tar.gz", "workhour.dump", "workhour.env"):
        path = output / filename
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        manifest["files"][filename] = {
            "bytes": path.stat().st_size, "sha256": digest,
        }
    with (output / "manifest.json").open("x", encoding="utf-8") as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
    with (output / "SHA256SUMS").open("x", encoding="ascii", newline="\n") as stream:
        for filename, entry in manifest["files"].items():
            stream.write(f"{entry['sha256']}  {filename}\n")
    # A minimal public summary only; keys, URLs with passwords and data stay private.
    print(json.dumps({"output": str(output), "tables": len(counts),
                      "files": {name: row["bytes"] for name, row in manifest["files"].items()}}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        prepare(args.output)
    except Exception as error:  # noqa: BLE001 - redact all failures at the CLI boundary
        # Avoid tracebacks containing URLs, credentials or database row contents.
        raise SystemExit(
            f"Preparation failed ({type(error).__name__}); keep the package private."
        ) from None
