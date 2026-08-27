"""Encrypt legacy plaintext device credentials without printing secret values."""
from __future__ import annotations

import argparse

from sqlalchemy import select

from ..core.config import settings
from ..core.credentials import decrypt_credential, encrypt_credential, is_encrypted
from ..database import SessionLocal
from ..models import IpCamList, ServerList


def migrate(*, apply_changes: bool) -> tuple[int, int]:
    if apply_changes and not settings.DEVICE_CREDENTIAL_KEY.strip():
        message = "Set and back up DEVICE_CREDENTIAL_KEY before applying migration"
        raise RuntimeError(message)
    scanned = 0
    changed = 0
    with SessionLocal() as db:
        records_and_fields = [
            (db.scalars(select(ServerList)).all(), ("server_pass",)),
            (db.scalars(select(IpCamList)).all(), ("admin_pass", "user_pass")),
        ]
        for records, fields in records_and_fields:
            for record in records:
                for field in fields:
                    scanned += 1
                    value = getattr(record, field)
                    if not value or is_encrypted(value):
                        continue
                    encrypted = encrypt_credential(value)
                    # Refuse to write data that cannot be decrypted with this key.
                    if decrypt_credential(encrypted) != value:
                        raise RuntimeError("Credential encryption round-trip failed")
                    changed += 1
                    if apply_changes:
                        setattr(record, field, encrypted)
        if apply_changes:
            db.commit()
        else:
            db.rollback()
    return scanned, changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="write encrypted values; without this flag the command is a dry run",
    )
    args = parser.parse_args()
    scanned, changed = migrate(apply_changes=args.apply)
    mode = "applied" if args.apply else "dry-run"
    print(f"Device credential migration {mode}: scanned={scanned}, changed={changed}")


if __name__ == "__main__":
    main()
