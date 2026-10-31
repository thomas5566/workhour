from cryptography.fernet import Fernet
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.credentials import ENCRYPTED_PREFIX
from app.db.base import Base
from app.models import IpCamList, ServerList
from app.scripts.rotate_device_credential_key import rotate


def _encrypted(value: str, key: bytes) -> str:
    token = Fernet(key).encrypt(value.encode("utf-8")).decode("ascii")
    return f"{ENCRYPTED_PREFIX}{token}"


def _decrypt(value: str, key: bytes) -> str:
    token = value[len(ENCRYPTED_PREFIX) :].encode("ascii")
    return Fernet(key).decrypt(token).decode("utf-8")


def _database() -> tuple[object, bytes, bytes]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    current_key = Fernet.generate_key()
    new_key = Fernet.generate_key()
    with Session(engine) as db:
        db.add(
            ServerList(
                id=1,
                server_pass=_encrypted("server credential", current_key),
            )
        )
        db.add(
            IpCamList(
                id=1,
                admin_pass=_encrypted("admin credential", current_key),
                user_pass=_encrypted("viewer credential", current_key),
            )
        )
        db.commit()
    return engine, current_key, new_key


def test_rotation_dry_run_validates_without_writing() -> None:
    engine, current_key, new_key = _database()
    with Session(engine) as db:
        original = db.scalar(select(ServerList.server_pass))
        assert original is not None
        scanned, changed = rotate(
            db,
            current_key=current_key.decode("ascii"),
            new_key=new_key.decode("ascii"),
            apply_changes=False,
        )
        assert (scanned, changed) == (3, 3)
        assert db.scalar(select(ServerList.server_pass)) == original
        assert _decrypt(original, current_key) == "server credential"


def test_rotation_reencrypts_all_credentials_with_new_key() -> None:
    engine, current_key, new_key = _database()
    with Session(engine) as db:
        scanned, changed = rotate(
            db,
            current_key=current_key.decode("ascii"),
            new_key=new_key.decode("ascii"),
            apply_changes=True,
        )
        assert (scanned, changed) == (3, 3)

    with Session(engine) as db:
        server = db.get(ServerList, 1)
        camera = db.get(IpCamList, 1)
        assert server is not None
        assert camera is not None
        assert server.server_pass is not None
        assert camera.admin_pass is not None
        assert camera.user_pass is not None
        assert _decrypt(server.server_pass, new_key) == "server credential"
        assert _decrypt(camera.admin_pass, new_key) == "admin credential"
        assert _decrypt(camera.user_pass, new_key) == "viewer credential"


def test_rotation_rolls_back_everything_when_one_value_is_invalid() -> None:
    engine, current_key, new_key = _database()
    with Session(engine) as db:
        camera = db.get(IpCamList, 1)
        assert camera is not None
        camera.user_pass = "legacy plaintext"
        db.commit()

    with Session(engine) as db:
        try:
            rotate(
                db,
                current_key=current_key.decode("ascii"),
                new_key=new_key.decode("ascii"),
                apply_changes=True,
            )
        except RuntimeError as error:
            assert "requires all values to be encrypted" in str(error)
        else:
            raise AssertionError("rotation must reject plaintext credentials")

    with Session(engine) as db:
        server_password = db.scalar(select(ServerList.server_pass))
        assert server_password is not None
        assert _decrypt(server_password, current_key) == "server credential"


def test_rotation_rejects_same_key() -> None:
    engine, current_key, _ = _database()
    with Session(engine) as db:
        try:
            rotate(
                db,
                current_key=current_key.decode("ascii"),
                new_key=current_key.decode("ascii"),
                apply_changes=False,
            )
        except RuntimeError as error:
            assert "must differ" in str(error)
        else:
            raise AssertionError("rotation must reject identical keys")
