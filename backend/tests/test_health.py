from types import SimpleNamespace
from uuid import UUID

import httpx
import pytest
from sqlalchemy.exc import OperationalError

import app.main as main_module
from app.database import get_db
from app.main import app
from app.schemas.branch_list import BranchList


@pytest.mark.anyio
async def test_health_check() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "1.0.0"}


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("path", "expected_status"),
    [
        ("/health", 200),
        ("/api/branchlist/", 401),
    ],
)
async def test_security_headers_cover_success_and_error_responses(
    path: str,
    expected_status: int,
) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get(path)

    assert response.status_code == expected_status
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["permissions-policy"] == (
        "camera=(), geolocation=(), microphone=()"
    )
    assert UUID(response.headers["x-request-id"]).version == 4


@pytest.mark.anyio
async def test_request_ids_are_server_generated_unique_and_cors_visible() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        first = await client.get(
            "/health",
            headers={
                "Origin": "http://localhost:8080",
                "X-Request-ID": "untrusted-client-value",
            },
        )
        second = await client.get("/health")

    first_request_id = first.headers["x-request-id"]
    second_request_id = second.headers["x-request-id"]
    assert UUID(first_request_id).version == 4
    assert UUID(second_request_id).version == 4
    assert first_request_id != second_request_id
    assert first_request_id != "untrusted-client-value"
    assert first.headers["access-control-expose-headers"] == "X-Request-ID"


@pytest.mark.anyio
async def test_readiness_check_queries_database() -> None:
    statements: list[str] = []
    app.dependency_overrides[get_db] = lambda: SimpleNamespace(
        execute=lambda statement: statements.append(str(statement))
    )

    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.get("/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "1.0.0"}
    assert statements == ["SELECT 1"]


@pytest.mark.anyio
async def test_readiness_check_fails_when_database_is_unavailable(caplog) -> None:
    caplog.set_level("ERROR", logger="app.main")

    def raise_database_error(_statement) -> None:
        raise OperationalError(
            "SELECT sensitive_connection_value",
            {},
            Exception("database unavailable"),
        )

    app.dependency_overrides[get_db] = lambda: SimpleNamespace(
        execute=raise_database_error
    )

    try:
        transport = httpx.ASGITransport(
            app=app,
            raise_app_exceptions=False,
        )
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.get("/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {"detail": "Database temporarily unavailable"}
    assert response.headers["Retry-After"] == "5"
    assert response.headers["x-request-id"] in caplog.text
    assert "sensitive_connection_value" not in response.text
    assert "Database temporarily unavailable" in caplog.text
    assert "sensitive_connection_value" not in caplog.text


@pytest.mark.anyio
async def test_unexpected_error_returns_sanitized_traceable_500(caplog) -> None:
    caplog.set_level("ERROR", logger="app.main")

    def raise_unexpected_error(_statement) -> None:
        raise RuntimeError("sensitive-runtime-value")

    app.dependency_overrides[get_db] = lambda: SimpleNamespace(
        execute=raise_unexpected_error
    )

    try:
        transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.get("/ready")
    finally:
        app.dependency_overrides.clear()

    request_id = response.headers["x-request-id"]
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert UUID(request_id).version == 4
    assert response.headers["x-content-type-options"] == "nosniff"
    assert request_id in caplog.text
    assert "RuntimeError" in caplog.text
    assert "sensitive-runtime-value" not in response.text
    assert "sensitive-runtime-value" not in caplog.text


@pytest.mark.anyio
async def test_openapi_document_is_available() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get("/api/openapi.json")

    assert response.status_code == 200
    document = response.json()
    assert document["info"]["title"] == "WorkHour API"
    assert "password" not in document["components"]["schemas"]["User"]["properties"]
    assert "password" in document["components"]["schemas"]["UserCreate"]["properties"]

    user_create_responses = document["paths"]["/api/user/"]["post"]["responses"]
    error_schema = {"$ref": "#/components/schemas/ErrorResponse"}
    assert user_create_responses["409"]["content"]["application/json"]["schema"] == (
        error_schema
    )
    assert user_create_responses["500"]["content"]["application/json"]["schema"] == (
        error_schema
    )
    assert user_create_responses["503"]["content"]["application/json"]["schema"] == (
        error_schema
    )


@pytest.mark.anyio
async def test_create_app_can_disable_api_documentation(monkeypatch) -> None:
    monkeypatch.setattr(main_module.settings, "ENABLE_API_DOCS", False)
    private_app = main_module.create_app()

    transport = httpx.ASGITransport(app=private_app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        health_response = await client.get("/health")
        documentation_responses = [
            await client.get("/api/openapi.json"),
            await client.get("/docs"),
            await client.get("/redoc"),
        ]

    assert health_response.status_code == 200
    assert all(response.status_code == 404 for response in documentation_responses)


def test_schema_can_serialize_orm_attributes() -> None:
    record = SimpleNamespace(
        id=1,
        branch_name="Taipei",
        branch_title="Taipei Office",
    )

    assert BranchList.model_validate(record).model_dump() == {
        "id": 1,
        "branch_name": "Taipei",
        "branch_title": "Taipei Office",
    }
