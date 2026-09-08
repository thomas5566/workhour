from datetime import UTC, date, datetime, timedelta
from types import SimpleNamespace

import httpx
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import auth as auth_module
from app.auth import login_manager
from app.core.hashing import Hasher
from app.database import Base, get_db
from app.main import app
from app.models import (
    BranchList,
    CstShop,
    Department,
    Expenditure,
    ExpenTask,
    Task,
    User,
    Workhour,
)
from app.repository import user_crud


@pytest.fixture
def api_engine():
    # StaticPool keeps one in-memory SQLite database visible to FastAPI's
    # worker thread and the test thread without touching a developer database.
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    def override_get_db():
        with Session(engine) as session:
            yield session

    manager = SimpleNamespace(
        id=1,
        department_id=1,
        is_superuser=True,
        checklistAll_permission=1,
    )
    # Overrides apply only inside this fixture. Production requests still use
    # the real token loader and configured database session.
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[login_manager] = lambda: manager

    try:
        yield engine
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


@pytest.fixture
def authenticated_api_engine(monkeypatch):
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)

    def override_get_db():
        with session_factory() as session:
            yield session

    # The token loader opens its own session. Point both it and request
    # dependencies at the same isolated database to exercise real JWT auth.
    monkeypatch.setattr(auth_module, "SessionLocal", session_factory)
    app.dependency_overrides[get_db] = override_get_db

    try:
        yield engine
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


@pytest.mark.anyio
async def test_manager_task_crud_through_fastapi(api_engine) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        create_response = await client.post(
            "/api/task/",
            json={
                "taskname": "api-modernization",
                "fullname": "API modernization integration test",
                "organization": "WorkHour",
            },
        )
        assert create_response.status_code == 200
        task_id = create_response.json()["id"]

        list_response = await client.get("/api/task/")
        assert list_response.status_code == 200
        assert [item["id"] for item in list_response.json()] == [task_id]

        delete_response = await client.delete(f"/api/task/{task_id}")
        assert delete_response.status_code == 204

        missing_response = await client.get(f"/api/task/{task_id}")
        missing_delete_response = await client.delete(f"/api/task/{task_id}")
        assert missing_response.status_code == 404
        assert missing_response.json() == {"detail": "Task not found"}
        assert missing_delete_response.status_code == 404
        assert missing_delete_response.json() == {"detail": "Task not found"}


@pytest.mark.anyio
async def test_authenticated_branch_route_applies_limit(api_engine) -> None:
    with Session(api_engine) as session:
        session.add_all(
            [
                BranchList(branch_name="Taipei", branch_title="Taipei Office"),
                BranchList(branch_name="Taichung", branch_title="Taichung Office"),
            ]
        )
        session.commit()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get("/api/branchlist/", params={"limit": 1})

    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.anyio
async def test_manager_can_create_server_inventory_for_existing_branch(api_engine) -> None:
    with Session(api_engine) as session:
        branch = BranchList(branch_name="A1", branch_title="Taipei")
        session.add(branch)
        session.commit()
        branch_id = branch.id

    payload = {
        "branch_id": branch_id,
        "server_location": "Taipei - A1",
        "server_name": "ERP Server",
        "server_ip": "192.0.2.10",
        "server_acc": "operator",
        "server_pass": "credential",
        "server_remark": "Primary server",
    }
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        create_response = await client.post("/api/serverlist/", json=payload)
        newer_response = await client.post(
            "/api/serverlist/",
            json={**payload, "server_name": "Newest Server"},
        )
        missing_branch_response = await client.post(
            "/api/serverlist/",
            json={**payload, "branch_id": branch_id + 999},
        )
        list_response = await client.get("/api/serverlist/")

    assert create_response.status_code == 201
    assert create_response.json()["server_name"] == "ERP Server"
    assert create_response.json()["branch_id"] == branch_id
    assert newer_response.status_code == 201
    assert [item["server_name"] for item in list_response.json()[:2]] == [
        "Newest Server",
        "ERP Server",
    ]
    assert missing_branch_response.status_code == 422
    assert missing_branch_response.json() == {"detail": "Selected branch does not exist"}

    server_id = create_response.json()["id"]
    newer_server_id = newer_response.json()["id"]
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        delete_response = await client.delete(f"/api/serverlist/{server_id}")
        newer_delete_response = await client.delete(f"/api/serverlist/{newer_server_id}")
        missing_delete_response = await client.delete(f"/api/serverlist/{server_id}")

    assert delete_response.status_code == 204
    assert newer_delete_response.status_code == 204
    assert missing_delete_response.status_code == 404
    assert missing_delete_response.json() == {"detail": "Server device not found"}


@pytest.mark.anyio
async def test_manager_reveals_device_credentials_only_on_explicit_request(
    api_engine,
) -> None:
    with Session(api_engine) as session:
        branch = BranchList(branch_name="A1", branch_title="Taipei")
        session.add(branch)
        session.commit()
        branch_id = branch.id

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        server_response = await client.post(
            "/api/serverlist/",
            json={
                "branch_id": branch_id,
                "server_location": "Taipei - A1",
                "server_name": "ERP Server",
                "server_ip": "192.0.2.10",
                "server_acc": "operator",
                "server_pass": "server-secret",
                "server_remark": "",
            },
        )
        camera_response = await client.post(
            "/api/ipcamlist/",
            json={
                "shop_id": 1,
                "shop_name": "Shop",
                "admin_pass": "admin-secret",
                "user_pass": "viewer-secret",
            },
        )
        server_id = server_response.json()["id"]
        camera_id = camera_response.json()["id"]
        server_reveal = await client.post(
            f"/api/serverlist/{server_id}/reveal-password"
        )
        camera_reveal = await client.post(
            f"/api/ipcamlist/{camera_id}/reveal-passwords"
        )

    assert server_response.json()["server_pass"] == "••••••••"
    assert camera_response.json()["admin_pass"] == "••••••••"
    assert camera_response.json()["user_pass"] == "••••••••"
    assert server_reveal.json() == {"password": "server-secret"}
    assert camera_reveal.json() == {
        "admin_password": "admin-secret",
        "user_password": "viewer-secret",
    }
    assert server_reveal.headers["cache-control"] == "no-store"
    assert camera_reveal.headers["cache-control"] == "no-store"


@pytest.mark.anyio
async def test_empty_collection_routes_return_successful_empty_lists(api_engine) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        for url in (
            "/api/department/",
            "/api/workhour/worklist-userid",
            "/api/workhour/worklist-shopid",
        ):
            response = await client.get(url)
            assert response.status_code == 200
            assert response.json() == []


@pytest.mark.anyio
@pytest.mark.parametrize(
    "params",
    [
        {"skip": -1},
        {"limit": 0},
        {"limit": 1001},
    ],
)
async def test_list_routes_reject_invalid_pagination(
    api_engine,
    params: dict[str, int],
) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get("/api/branchlist/", params=params)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][-1] in params


@pytest.mark.anyio
@pytest.mark.parametrize(
    "url",
    [
        "/api/task/0",
        "/api/serverlist/serverlist-branchid?branch_id=0",
    ],
)
async def test_routes_reject_nonpositive_resource_ids(
    api_engine,
    url: str,
) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get(url)

    assert response.status_code == 422


@pytest.mark.anyio
async def test_workhour_collection_routes_apply_pagination(api_engine) -> None:
    with Session(api_engine) as session:
        session.add_all(
            [
                Workhour(
                    id=index,
                    user_id=1,
                    task_id=1,
                    shop_id=1,
                    start_date=date(2026, 8, 15 + index),
                    end_date=date(2026, 8, 15 + index),
                    hour=8,
                    overtime_hour=0,
                    case_close=False,
                    active=True,
                )
                for index in range(1, 4)
            ]
        )
        session.commit()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        personal_page = await client.get(
            "/api/workhour/workhours",
            params={"skip": 1, "limit": 1},
        )
        manager_page = await client.get(
            "/api/workhour/allworkhours",
            params={"limit": 2},
        )

    assert personal_page.status_code == 200
    assert [item["id"] for item in personal_page.json()] == [2]
    assert manager_page.status_code == 200
    assert [item["id"] for item in manager_page.json()] == [3, 2]


def test_openapi_marks_every_resource_path_id_as_positive() -> None:
    resource_parameters = []

    for path_item in app.openapi()["paths"].values():
        for operation in path_item.values():
            for parameter in operation.get("parameters", []):
                if parameter["in"] == "path" and parameter["name"].endswith("_id"):
                    resource_parameters.append(parameter)

    # This guards every current ID-bearing operation, not only one sample route.
    # CRUD routes for managed resources contribute positive ID path parameters.
    assert len(resource_parameters) == 30
    assert all(
        parameter["schema"]["exclusiveMinimum"] == 0
        for parameter in resource_parameters
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "invalid_fields",
    [
        {"hour": 100},
        {"end_date": "2026-08-16"},
    ],
)
async def test_workhour_rejects_invalid_payload_before_database(
    api_engine,
    invalid_fields: dict[str, object],
) -> None:
    payload = {
        "task_id": 1,
        "shop_id": 1,
        "start_date": "2026-08-17",
        "end_date": "2026-08-17",
        "hour": 8,
        "overtime_hour": 0,
        "case_close": False,
        **invalid_fields,
    }

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post("/api/workhour/", json=payload)

    # Validation errors stay client-facing and never become database 500s.
    assert response.status_code == 422


def test_retired_features_are_not_exposed_in_openapi() -> None:
    paths = app.openapi()["paths"]

    # The legacy tables remain for data retention, but no application route
    # may expose the retired leave or Dudo transaction features.
    assert not any(path.startswith("/api/daysoff") for path in paths)
    assert not any(path.startswith("/api/transactionslist") for path in paths)


def test_message_updates_publish_typed_response_contract() -> None:
    schema = app.openapi()
    message_response = {"$ref": "#/components/schemas/MessageResponse"}

    for path in (
        "/api/workhour/{workhour_id}",
        "/api/serverlist/{serverlist_id}",
        "/api/fetnetlist/{fetnetlist_id}",
        "/api/ipcamlist/{ipcamlist_id}",
    ):
        response_schema = schema["paths"][path]["put"]["responses"]["200"][
            "content"
        ]["application/json"]["schema"]
        assert response_schema == message_response


@pytest.mark.anyio
async def test_inventory_update_rejects_overlong_field_before_database(
    api_engine,
) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.put(
            "/api/serverlist/1",
            json={
                "server_name": "x" * 256,
                "server_ip": "192.0.2.10",
                "server_location": "Taipei",
                "server_acc": "operator",
                "server_pass": "credential",
                "server_remark": "Primary",
            },
        )

    # Body validation runs before the endpoint can look up or mutate the row.
    assert response.status_code == 422


@pytest.mark.anyio
async def test_expense_task_crud_and_permissions(api_engine) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        create_response = await client.post(
            "/api/expentask/",
            json={"expentask_name": "Travel"},
        )
        assert create_response.status_code == 200
        expense_task_id = create_response.json()["id"]

        duplicate_response = await client.post(
            "/api/expentask/",
            json={"expentask_name": "Travel"},
        )
        list_response = await client.get("/api/expentask/")
        update_response = await client.put(
            f"/api/expentask/{expense_task_id}",
            json={"expentask_name": "Business travel"},
        )

        regular_user = SimpleNamespace(
            id=2,
            department_id=1,
            is_superuser=False,
            checklistAll_permission=0,
        )
        app.dependency_overrides[login_manager] = lambda: regular_user
        regular_read = await client.get(f"/api/expentask/{expense_task_id}")
        regular_create = await client.post(
            "/api/expentask/",
            json={"expentask_name": "Unapproved category"},
        )

    assert duplicate_response.status_code == 409
    assert [item["expentask_name"] for item in list_response.json()] == ["Travel"]
    assert update_response.status_code == 200
    assert update_response.json()["expentask_name"] == "Business travel"
    assert regular_read.status_code == 200
    assert regular_create.status_code == 403


@pytest.mark.anyio
async def test_user_creation_requires_administrator_token(
    authenticated_api_engine,
) -> None:
    with Session(authenticated_api_engine) as session:
        session.add_all(
            [
                Department(id=1, department_name="Management"),
                Department(id=2, department_name="Staff"),
                User(
                    id=1,
                    username="manager",
                    fullname="Manager",
                    password=Hasher.get_password_hash("manager-password"),
                    is_active=True,
                    is_superuser=True,
                    checklistAll_permission=1,
                    department_id=1,
                ),
                User(
                    id=2,
                    username="staff",
                    fullname="Staff",
                    password=Hasher.get_password_hash("staff-password"),
                    is_active=True,
                    checklistAll_permission=0,
                    department_id=2,
                ),
                User(
                    id=3,
                    username="report-manager",
                    fullname="Report Manager",
                    password=Hasher.get_password_hash("report-password"),
                    is_active=True,
                    is_superuser=False,
                    checklistAll_permission=1,
                    department_id=1,
                ),
            ]
        )
        session.commit()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        manager_login = await client.post(
            "/api/user/login",
            data={"username": "manager", "password": "manager-password"},
        )
        staff_login = await client.post(
            "/api/user/login",
            data={"username": "staff", "password": "staff-password"},
        )
        report_login = await client.post(
            "/api/user/login",
            data={"username": "report-manager", "password": "report-password"},
        )
        assert manager_login.status_code == 200
        assert staff_login.status_code == 200
        assert report_login.status_code == 200

        account = {
            "username": "new-user",
            "fullname": "New User",
            "password": "new-user-password",
            "department_id": 2,
        }
        manager_response = await client.post(
            "/api/user/",
            json=account,
            headers={"Authorization": f"Bearer {manager_login.json()['token']}"},
        )
        duplicate_response = await client.post(
            "/api/user/",
            json=account,
            headers={"Authorization": f"Bearer {manager_login.json()['token']}"},
        )
        staff_response = await client.post(
            "/api/user/",
            json={**account, "username": "staff-created-user"},
            headers={"Authorization": f"Bearer {staff_login.json()['token']}"},
        )
        report_response = await client.post(
            "/api/user/",
            json={**account, "username": "report-created-user"},
            headers={"Authorization": f"Bearer {report_login.json()['token']}"},
        )
        anonymous_response = await client.post(
            "/api/user/",
            json={**account, "username": "anonymous-created-user"},
        )

    assert manager_response.status_code == 200
    assert manager_response.json()["username"] == "new-user"
    assert "password" not in manager_response.json()
    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {"detail": "Username already registered"}
    assert staff_response.status_code == 403
    assert report_response.status_code == 403
    assert anonymous_response.status_code == 401


@pytest.mark.anyio
async def test_login_lockout_handles_naive_database_timestamps(
    authenticated_api_engine,
) -> None:
    password = "correct-password"
    with Session(authenticated_api_engine) as session:
        session.add(
            User(
                username="lockout-user",
                password=Hasher.get_password_hash(password),
                is_active=True,
                department_id=1,
            )
        )
        session.commit()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        for _ in range(5):
            response = await client.post(
                "/api/user/login",
                data={"username": "lockout-user", "password": "wrong-password"},
            )
            assert response.status_code == 401

        locked_response = await client.post(
            "/api/user/login",
            data={"username": "lockout-user", "password": password},
        )
        assert locked_response.status_code == 401

        # SQLite returns a naive datetime even for DateTime(timezone=True).
        with Session(authenticated_api_engine) as session:
            user = user_crud.get_user_by_username(session, "lockout-user")
            user.locked_until = datetime.now(UTC).replace(tzinfo=None) - timedelta(
                seconds=1
            )
            session.commit()

        unlocked_response = await client.post(
            "/api/user/login",
            data={"username": "lockout-user", "password": password},
        )

    assert unlocked_response.status_code == 200
    with Session(authenticated_api_engine) as session:
        user = user_crud.get_user_by_username(session, "lockout-user")
        assert user.failed_login_attempts == 0
        assert user.locked_until is None


@pytest.mark.anyio
async def test_login_treats_sql_injection_payloads_as_bound_values(
    authenticated_api_engine,
) -> None:
    with Session(authenticated_api_engine) as session:
        session.add(
            User(
                username="manager",
                fullname="Manager",
                password=Hasher.get_password_hash("manager-password"),
                is_active=True,
                checklistAll_permission=1,
            )
        )
        session.commit()

    statements: list[str] = []
    parameters: list[object] = []

    def capture_sql(_connection, _cursor, statement, params, _context, _many):
        statements.append(statement)
        parameters.append(params)

    event.listen(authenticated_api_engine, "before_cursor_execute", capture_sql)
    username_payload = "manager' OR '1'='1' --"
    password_payload = "' OR '1'='1' --"
    transport = httpx.ASGITransport(app=app)
    try:
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            username_response = await client.post(
                "/api/user/login",
                data={"username": username_payload, "password": "anything"},
            )
            password_response = await client.post(
                "/api/user/login",
                data={"username": "manager", "password": password_payload},
            )
    finally:
        event.remove(authenticated_api_engine, "before_cursor_execute", capture_sql)

    assert username_response.status_code == 401
    assert password_response.status_code == 401
    # Payloads may occur only in DB-driver parameters, never in SQL syntax.
    assert all(username_payload not in statement for statement in statements)
    assert any(username_payload in values for values in parameters)


@pytest.mark.anyio
async def test_sql_metacharacters_are_data_and_path_ids_remain_typed(api_engine) -> None:
    task_name = "'; DROP TABLE task; --"
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        create_response = await client.post(
            "/api/task/",
            json={
                "taskname": task_name,
                "fullname": "Injection regression test",
                "organization": "WorkHour",
            },
        )
        invalid_id_response = await client.get("/api/task/1%20OR%201=1")
        list_response = await client.get("/api/task/")

    assert create_response.status_code == 200
    assert invalid_id_response.status_code == 422
    assert list_response.status_code == 200
    assert [task["taskname"] for task in list_response.json()] == [task_name]


@pytest.mark.anyio
async def test_database_constraint_conflict_returns_sanitized_409(
    api_engine,
    monkeypatch,
) -> None:
    with Session(api_engine) as session:
        session.add(
            User(
                username="duplicate-user",
                fullname="Existing User",
                password="existing-secret-hash",
                is_active=True,
            )
        )
        session.commit()

    # Simulate a uniqueness race: another request inserts after the pre-check.
    monkeypatch.setattr(user_crud, "get_user_by_username", lambda *args, **kwargs: None)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/user/",
            json={
                "username": "duplicate-user",
                "fullname": "Conflicting User",
                "password": "request-secret-password",
                "department_id": 1,
            },
        )

    assert response.status_code == 409
    assert response.json() == {"detail": "Database constraint conflict"}
    assert "INSERT" not in response.text
    assert "request-secret-password" not in response.text

    with Session(api_engine) as session:
        assert len(user_crud.get_users(session)) == 1


@pytest.mark.anyio
async def test_inactive_account_revokes_existing_bearer_token(
    authenticated_api_engine,
) -> None:
    with Session(authenticated_api_engine) as session:
        session.add(
            User(
                id=9,
                username="revoked-user",
                fullname="Revoked User",
                password=Hasher.get_password_hash("revoked-password"),
                is_active=False,
                checklistAll_permission=0,
            )
        )
        session.commit()

    # This represents a token issued before an administrator disabled the user.
    token = login_manager.create_access_token(data={"sub": "9"})
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
async def test_workhour_routes_enforce_authenticated_owner(
    authenticated_api_engine,
) -> None:
    with Session(authenticated_api_engine) as session:
        session.add_all(
            [
                Department(id=1, department_name="Owner Department"),
                Department(id=2, department_name="Other Department"),
                User(
                    id=1,
                    username="owner",
                    fullname="Owner",
                    password=Hasher.get_password_hash("owner-password"),
                    is_active=True,
                    checklistAll_permission=0,
                    department_id=1,
                ),
                User(
                    id=2,
                    username="other-user",
                    fullname="Other User",
                    password=Hasher.get_password_hash("other-password"),
                    is_active=True,
                    checklistAll_permission=0,
                    department_id=2,
                ),
                Task(
                    id=1,
                    taskname="support",
                    fullname="Support",
                    organization="WorkHour",
                ),
                CstShop(
                    id=1,
                    main_department_id=1,
                    shop_name="Taipei Shop",
                    shop_number="TPE-01",
                ),
                Workhour(
                    id=1,
                    user_id=1,
                    task_id=1,
                    shop_id=1,
                    start_date=date(2026, 8, 17),
                    end_date=date(2026, 8, 17),
                    hour=8,
                    overtime_hour=0,
                    case_close=False,
                    active=True,
                ),
            ]
        )
        session.commit()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        owner_login = await client.post(
            "/api/user/login",
            data={"username": "owner", "password": "owner-password"},
        )
        other_login = await client.post(
            "/api/user/login",
            data={"username": "other-user", "password": "other-password"},
        )
        assert owner_login.status_code == 200
        assert other_login.status_code == 200
        owner_headers = {
            "Authorization": f"Bearer {owner_login.json()['token']}"
        }
        other_headers = {
            "Authorization": f"Bearer {other_login.json()['token']}"
        }

        owner_read = await client.get("/api/workhour/1", headers=owner_headers)
        other_read = await client.get("/api/workhour/1", headers=other_headers)

        workhour_payload = {
            "user_id": 1,
            "task_id": 1,
            "shop_id": 1,
            "start_date": "2026-08-18",
            "end_date": "2026-08-18",
            "hour": 7.5,
            "overtime_hour": 0.5,
            "case_close": False,
        }
        other_update = await client.put(
            "/api/workhour/1",
            json=workhour_payload,
            headers=other_headers,
        )
        other_delete = await client.delete(
            "/api/workhour/1",
            headers=other_headers,
        )
        spoofed_create = await client.post(
            "/api/workhour/",
            json=workhour_payload,
            headers=other_headers,
        )

    assert owner_read.status_code == 200
    assert other_read.status_code == 403
    assert other_update.status_code == 403
    assert other_delete.status_code == 403
    assert spoofed_create.status_code == 200
    assert spoofed_create.json()["user_id"] == 2

    with Session(authenticated_api_engine) as session:
        original_workhour = session.get(Workhour, 1)
        created_workhour = session.get(Workhour, spoofed_create.json()["id"])
        assert original_workhour is not None
        assert original_workhour.start_date == date(2026, 8, 17)
        assert created_workhour is not None
        assert created_workhour.user_id == 2


@pytest.mark.anyio
async def test_expenditure_routes_enforce_authenticated_owner(
    authenticated_api_engine,
) -> None:
    with Session(authenticated_api_engine) as session:
        session.add_all(
            [
                Department(id=1, department_name="Expense Owner Department"),
                Department(id=2, department_name="Expense Other Department"),
                User(
                    id=1,
                    username="expense-owner",
                    fullname="Expense Owner",
                    password=Hasher.get_password_hash("owner-password"),
                    is_active=True,
                    checklistAll_permission=0,
                    department_id=1,
                ),
                User(
                    id=2,
                    username="expense-other",
                    fullname="Expense Other",
                    password=Hasher.get_password_hash("other-password"),
                    is_active=True,
                    checklistAll_permission=0,
                    department_id=2,
                ),
                ExpenTask(id=1, expentask_name="Travel"),
                Expenditure(
                    id=1,
                    user_id=1,
                    expentask_id=1,
                    date=date(2026, 8, 17),
                    price=500,
                    description="Owner train ticket",
                    active=True,
                ),
            ]
        )
        session.commit()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        owner_login = await client.post(
            "/api/user/login",
            data={"username": "expense-owner", "password": "owner-password"},
        )
        other_login = await client.post(
            "/api/user/login",
            data={"username": "expense-other", "password": "other-password"},
        )
        assert owner_login.status_code == 200
        assert other_login.status_code == 200
        owner_headers = {
            "Authorization": f"Bearer {owner_login.json()['token']}"
        }
        other_headers = {
            "Authorization": f"Bearer {other_login.json()['token']}"
        }

        owner_read = await client.get("/api/expen/1", headers=owner_headers)
        other_read = await client.get("/api/expen/1", headers=other_headers)

        expenditure_payload = {
            "user_id": 1,
            "expentask_id": 1,
            "date": "2026-08-18",
            "price": 250,
            "description": "Other taxi fare",
        }
        other_update = await client.put(
            "/api/expen/1",
            json=expenditure_payload,
            headers=other_headers,
        )
        other_delete = await client.delete(
            "/api/expen/1",
            headers=other_headers,
        )
        other_owner_total = await client.get(
            "/api/expen/totalexpen/1",
            headers=other_headers,
        )
        spoofed_create = await client.post(
            "/api/expen/",
            json=expenditure_payload,
            headers=other_headers,
        )
        other_list = await client.get(
            "/api/expen/expens",
            headers=other_headers,
        )

    assert owner_read.status_code == 200
    assert other_read.status_code == 403
    assert other_update.status_code == 403
    assert other_delete.status_code == 403
    assert other_owner_total.status_code == 403
    assert spoofed_create.status_code == 200
    assert spoofed_create.json()["user_id"] == 2
    assert [item["id"] for item in other_list.json()] == [
        spoofed_create.json()["id"]
    ]

    with Session(authenticated_api_engine) as session:
        original_expenditure = session.get(Expenditure, 1)
        created_expenditure = session.get(
            Expenditure,
            spoofed_create.json()["id"],
        )
        assert original_expenditure is not None
        assert original_expenditure.price == 500
        assert created_expenditure is not None
        assert created_expenditure.user_id == 2
