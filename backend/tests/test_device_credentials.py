from pydantic import SecretStr
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.credentials import (
    ENCRYPTED_PREFIX,
    MASKED_CREDENTIAL,
    decrypt_credential,
    encrypt_credential,
)
from app.db.base import Base
from app.models import IpCamList, ServerList
from app.repository import ipcamlist_crud, serverlist_crud
from app.schemas.ipcamlist import IpCamList as IpCamListResponse
from app.schemas.ipcamlist import IpCamListCreate, IpCamListUpdate
from app.schemas.serverlist import ServerList as ServerListResponse
from app.schemas.serverlist import ServerListCreate, ServerListUpdate


def test_credential_encryption_is_stable_and_reversible() -> None:
    encrypted = encrypt_credential("plain-secret")
    assert encrypted is not None
    assert encrypted.startswith(ENCRYPTED_PREFIX)
    assert encrypted != "plain-secret"
    assert encrypt_credential(encrypted) == encrypted
    assert decrypt_credential(encrypted) == "plain-secret"


def test_response_schemas_mask_credentials() -> None:
    server = ServerListResponse.model_validate(
        ServerList(id=1, server_pass=encrypt_credential("server-secret"))
    )
    camera = IpCamListResponse.model_validate(
        IpCamList(
            id=1,
            admin_pass=encrypt_credential("admin-secret"),
            user_pass=encrypt_credential("viewer-secret"),
        )
    )
    assert server.model_dump()["server_pass"] == MASKED_CREDENTIAL
    assert camera.model_dump()["admin_pass"] == MASKED_CREDENTIAL
    assert camera.model_dump()["user_pass"] == MASKED_CREDENTIAL


def test_repository_encrypts_and_blank_update_preserves_credentials() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        server = serverlist_crud.create_serverlist(
            db,
            ServerListCreate(
                branch_id=1,
                server_name="server",
                server_ip="192.0.2.1",
                server_location="branch",
                server_acc="admin",
                server_pass=SecretStr("server-secret"),
            ),
        )
        original_server_password = server.server_pass
        assert original_server_password != "server-secret"

        serverlist_crud.update_serverlist_by_id(
            server.id,
            ServerListUpdate(
                branch_id=1,
                server_name="renamed",
                server_ip="192.0.2.1",
                server_location="branch",
                server_acc="admin",
                server_remark="",
            ),
            db,
        )
        assert server.server_pass == original_server_password

        camera = ipcamlist_crud.create_ipcamlist(
            db,
            IpCamListCreate(
                shop_id=1,
                shop_name="shop",
                admin_pass=SecretStr("admin-secret"),
                user_pass=SecretStr("viewer-secret"),
            ),
        )
        original_admin_password = camera.admin_pass
        original_user_password = camera.user_pass
        ipcamlist_crud.update_ipcamlist_by_id(
            camera.id,
            IpCamListUpdate(shop_id=1, shop_name="updated"),
            db,
        )
        assert camera.admin_pass == original_admin_password
        assert camera.user_pass == original_user_password
