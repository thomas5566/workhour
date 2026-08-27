import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from .config import Settings, settings

ENCRYPTED_PREFIX = "enc:v1:"
MASKED_CREDENTIAL = "••••••••"


def _fernet(settings_value: Settings = settings) -> Fernet:
    try:
        configured_key = settings_value.DEVICE_CREDENTIAL_KEY.strip().encode("ascii")
    except UnicodeEncodeError as error:
        raise RuntimeError("DEVICE_CREDENTIAL_KEY must be a valid Fernet key") from error
    if configured_key:
        try:
            return Fernet(configured_key)
        except (ValueError, TypeError) as error:
            raise RuntimeError("DEVICE_CREDENTIAL_KEY must be a valid Fernet key") from error

    # Domain separation prevents the derived encryption key from being equal to
    # the JWT signing secret even when both originate from SECRET_KEY.
    derived = hashlib.sha256(
        b"workhour-device-credentials-v1\0" + settings_value.SECRET_KEY.encode("utf-8")
    ).digest()
    return Fernet(base64.urlsafe_b64encode(derived))


def is_encrypted(value: str | None) -> bool:
    return bool(value and value.startswith(ENCRYPTED_PREFIX))


def encrypt_credential(value: str | None) -> str | None:
    """Encrypt a credential once; empty and already encrypted values are stable."""
    if value is None or value == "" or is_encrypted(value):
        return value
    token = _fernet().encrypt(value.encode("utf-8")).decode("ascii")
    return f"{ENCRYPTED_PREFIX}{token}"


def decrypt_credential(value: str | None) -> str | None:
    """Decrypt migrated values while temporarily accepting legacy plaintext."""
    if value is None or value == "" or not is_encrypted(value):
        return value
    try:
        token = value[len(ENCRYPTED_PREFIX):].encode("ascii")
        return _fernet().decrypt(token).decode("utf-8")
    except InvalidToken as error:
        message = "Device credential cannot be decrypted with the configured key"
        raise RuntimeError(message) from error


def mask_credential(value: str | None) -> str | None:
    return MASKED_CREDENTIAL if value else None
