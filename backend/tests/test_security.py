from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import httpx
import jwt
import pytest
from fastapi import HTTPException

from app.api import user as user_api
from app.auth import ensure_owner_or_manager, login_manager, require_manager
from app.core.config import settings
from app.core.hashing import DUMMY_PASSWORD_HASH, Hasher
from app.database import get_db
from app.main import app
from app.schemas.users import User


def test_password_hash_round_trip() -> None:
    hashed_password = Hasher.get_password_hash("correct horse battery staple")

    assert hashed_password != "correct horse battery staple"
    assert Hasher.verify_password(
        "correct horse battery staple",
        hashed_password,
    )
    assert not Hasher.verify_password("wrong password", hashed_password)
    assert not Hasher.verify_password("correct horse battery staple", "invalid-hash")
    assert not Hasher.verify_password("correct horse battery staple", None)


def test_password_hash_rejects_values_over_bcrypt_byte_limit() -> None:
    with pytest.raises(ValueError, match="72 UTF-8 bytes"):
        Hasher.get_password_hash("密" * 25)

    assert not Hasher.verify_password("密" * 25, DUMMY_PASSWORD_HASH)


def test_login_manager_uses_configured_algorithm() -> None:
    assert login_manager.algorithm == settings.ALGORITHM


def test_public_user_schema_never_serializes_password() -> None:
    database_user = SimpleNamespace(
        id=1,
        username="thomas",
        fullname="Thomas",
        password="$2b$12$sensitive-password-hash",
        is_superuser=False,
        is_active=True,
        checklistAll_permission=0,
        department_id=1,
        department=None,
    )

    response = User.model_validate(database_user).model_dump()

    assert "password" not in response


def test_manager_dependency_accepts_manager_and_superuser() -> None:
    manager = SimpleNamespace(is_superuser=False, checklistAll_permission=1)
    superuser = SimpleNamespace(is_superuser=True, checklistAll_permission=0)

    assert require_manager(manager) is manager
    assert require_manager(superuser) is superuser


def test_manager_dependency_rejects_regular_user() -> None:
    regular_user = SimpleNamespace(
        is_superuser=False,
        checklistAll_permission=0,
    )

    with pytest.raises(HTTPException) as error:
        require_manager(regular_user)

    assert error.value.status_code == 403


def test_owner_or_manager_access_control() -> None:
    owner = SimpleNamespace(
        id=3,
        is_superuser=False,
        checklistAll_permission=0,
    )
    manager = SimpleNamespace(
        id=4,
        is_superuser=False,
        checklistAll_permission=1,
    )

    ensure_owner_or_manager(owner, owner_id=3)
    ensure_owner_or_manager(manager, owner_id=3)

    with pytest.raises(HTTPException) as error:
        ensure_owner_or_manager(owner, owner_id=99)
    assert error.value.status_code == 403


def test_openapi_requires_authentication_for_business_routes() -> None:
    schema = app.openapi()
    public_operations = {
        ("/api/user/login", "post"),
        # Self-registration exposes only department labels and creates
        # regular accounts; role-bearing account management stays protected.
        ("/api/user/registration-departments", "get"),
        ("/api/user/register", "post"),
        ("/health", "get"),
        ("/ready", "get"),
    }
    http_methods = {"get", "post", "put", "patch", "delete"}

    # Treat the public API surface as an explicit allowlist. A future endpoint
    # without authentication must be reviewed and intentionally added here.
    for path, path_item in schema["paths"].items():
        for method, operation in path_item.items():
            if method not in http_methods or (path, method) in public_operations:
                continue
            assert operation.get("security"), (
                f"{method.upper()} {path} is missing an authentication requirement"
            )

    password_flow = schema["components"]["securitySchemes"]["LoginManager"][
        "flows"
    ]["password"]
    assert password_flow["tokenUrl"] == "/api/user/login"


@pytest.mark.anyio
async def test_login_returns_bearer_token_without_password(monkeypatch) -> None:
    database_user = SimpleNamespace(
        id=7,
        username="thomas",
        fullname="Thomas",
        password=Hasher.get_password_hash("correct horse battery staple"),
        is_superuser=False,
        is_active=True,
        checklistAll_permission=0,
        department_id=1,
        department=None,
    )
    monkeypatch.setattr(
        user_api.user_crud,
        "get_user_by_username",
        lambda _db, username: database_user if username == "thomas" else None,
    )
    app.dependency_overrides[get_db] = lambda: None

    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.post(
                "/api/user/login",
                data={
                    "username": "thomas",
                    "password": "correct horse battery staple",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["pragma"] == "no-cache"
    payload = response.json()
    assert "password" not in payload
    assert payload["token"]
    claims = jwt.decode(
        payload["token"],
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    assert claims["sub"] == "7"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "password",
    [
        "wrong-password",
        "x" * 73,
        "密" * 25,
    ],
)
async def test_login_uses_generic_unauthorized_response(
    monkeypatch,
    password: str,
) -> None:
    monkeypatch.setattr(
        user_api.user_crud,
        "get_user_by_username",
        lambda _db, username: None,
    )
    app.dependency_overrides[get_db] = lambda: None

    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.post(
                "/api/user/login",
                data={"username": "missing", "password": password},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.anyio
async def test_login_rejects_inactive_user(monkeypatch) -> None:
    inactive_user = SimpleNamespace(
        id=8,
        username="disabled",
        password=Hasher.get_password_hash("correct horse battery staple"),
        is_active=False,
    )
    monkeypatch.setattr(
        user_api.user_crud,
        "get_user_by_username",
        lambda _db, username: inactive_user,
    )
    app.dependency_overrides[get_db] = lambda: None

    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.post(
                "/api/user/login",
                data={
                    "username": "disabled",
                    "password": "correct horse battery staple",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "token",
    [
        "not-a-jwt",
        jwt.encode(
            {
                "sub": "not-a-numeric-user-id",
                "exp": datetime.now(UTC) + timedelta(minutes=5),
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        ),
        jwt.encode(
            {
                "sub": "1",
                "exp": datetime.now(UTC) - timedelta(minutes=5),
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        ),
    ],
)
async def test_protected_route_rejects_invalid_bearer_tokens(token: str) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/api/branchlist/",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "path",
    [
        "/api/branchlist/",
        "/api/cstshop/",
        "/api/department/",
        "/api/expen/expens",
        "/api/expentask/",
        "/api/task/",
        "/api/serverlist/",
        "/api/fetnetlist/",
        "/api/ipcamlist/",
    ],
)
async def test_inventory_routes_reject_anonymous_requests(path: str) -> None:
    # These endpoints expose internal location, credential, or transaction data.
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get(path)

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}
    assert response.headers["www-authenticate"] == "Bearer"
