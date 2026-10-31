"""Rotate encrypted device credentials without printing key or credential values.

The current ``DEVICE_CREDENTIAL_KEY`` is the source key. The destination key
must be supplied through ``NEW_DEVICE_CREDENTIAL_KEY``. The command is a dry
run unless ``--apply`` is explicitly provided.
"""

from __future__ import annotations

import argparse
import os
from collections.abc import Iterable

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.credentials import ENCRYPTED_PREFIX, is_encrypted
from ..database import SessionLocal
from ..models import IpCamList, ServerList

NEW_KEY_ENVIRONMENT_VARIABLE = "NEW_DEVICE_CREDENTIAL_KEY"


def _fernet_from_key(value: str, *, variable_name: str) -> Fernet:
    if not value.strip():
        raise RuntimeError(f"{variable_name} must be set")
    try:
        return Fernet(value.strip().encode("ascii"))
    except (UnicodeEncodeError, ValueError, TypeError) as error:
        raise RuntimeError(f"{variable_name} must be a valid Fernet key") from error


def _records_and_fields(db: Session) -> Iterable[tuple[list[object], tuple[str, ...]]]:
    yield (
        list(db.scalars(select(ServerList).with_for_update()).all()),
        ("server_pass",),
    )
    yield (
        list(db.scalars(select(IpCamList).with_for_update()).all()),
        ("admin_pass", "user_pass"),
    )


def rotate(
    db: Session,
    *,
    current_key: str,
    new_key: str,
    apply_changes: bool,
) -> tuple[int, int]:
    """Validate and optionally re-encrypt every stored device credential."""
    current_fernet = _fernet_from_key(
        current_key,
        variable_name="DEVICE_CREDENTIAL_KEY",
    )
    new_fernet = _fernet_from_key(
        new_key,
        variable_name=NEW_KEY_ENVIRONMENT_VARIABLE,
    )
    if current_key.strip() == new_key.strip():
        raise RuntimeError("The current and new device credential keys must differ")

    scanned = 0
    changed = 0
    try:
        for records, fields in _records_and_fields(db):
            for record in records:
                for field in fields:
                    scanned += 1
                    value = getattr(record, field)
                    if not value:
                        continue
                    if not is_encrypted(value):
                        raise RuntimeError(
                            "Device credential rotation requires all values to be encrypted"
                        )

                    token = value[len(ENCRYPTED_PREFIX) :].encode("ascii")
                    try:
                        plaintext = current_fernet.decrypt(token)
                    except (InvalidToken, UnicodeEncodeError) as error:
                        raise RuntimeError(
                            "A device credential cannot be decrypted with the current key"
                        ) from error

                    rotated_token = new_fernet.encrypt(plaintext)
                    if new_fernet.decrypt(rotated_token) != plaintext:
                        raise RuntimeError("Device credential rotation round-trip failed")

                    changed += 1
                    if apply_changes:
                        setattr(
                            record,
                            field,
                            f"{ENCRYPTED_PREFIX}{rotated_token.decode('ascii')}",
                        )

        if apply_changes:
            db.commit()
        else:
            db.rollback()
    except Exception:
        db.rollback()
        raise
    return scanned, changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="write rotated values; without this flag the command is a dry run",
    )
    args = parser.parse_args()
    new_key = os.environ.get(NEW_KEY_ENVIRONMENT_VARIABLE, "")
    with SessionLocal() as db:
        scanned, changed = rotate(
            db,
            current_key=settings.DEVICE_CREDENTIAL_KEY,
            new_key=new_key,
            apply_changes=args.apply,
        )
    mode = "applied" if args.apply else "dry-run"
    print(f"Device credential key rotation {mode}: scanned={scanned}, changed={changed}")


if __name__ == "__main__":
    main()
