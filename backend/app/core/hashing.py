import bcrypt

BCRYPT_MAX_PASSWORD_BYTES = 72


class Hasher:
    """Password hashing helpers kept compatible with existing bcrypt hashes."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str | None) -> bool:
        password_bytes = plain_password.encode("utf-8")
        if len(password_bytes) > BCRYPT_MAX_PASSWORD_BYTES or not hashed_password:
            # Untrusted login input and legacy null hashes must fail closed.
            return False

        try:
            return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))
        except ValueError:
            # A malformed stored hash is not a reason to expose an API 500.
            return False

    @staticmethod
    def get_password_hash(plain_password: str) -> str:
        password_bytes = plain_password.encode("utf-8")
        if len(password_bytes) > BCRYPT_MAX_PASSWORD_BYTES:
            raise ValueError("password must not exceed 72 UTF-8 bytes")

        return bcrypt.hashpw(
            password_bytes,
            bcrypt.gensalt(),
        ).decode("utf-8")


DUMMY_PASSWORD_HASH = Hasher.get_password_hash("not-a-real-user-password")
