import logging
from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, Response
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError

from app.api import (
    branchlist,
    cstshop,
    department,
    expen,
    expentask,
    fetnetlist,
    ipcamlist,
    serverlist,
    task,
    user,
    workhour,
)
from app.api.dependencies import DatabaseSession
from app.core.config import settings
from app.schemas.common import ErrorResponse

logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    status: str
    version: str


def apply_standard_response_headers(
    response: Response,
    request_id: str,
) -> Response:
    """Attach browser defenses and the server-generated correlation ID."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = (
        "camera=(), geolocation=(), microphone=()"
    )
    response.headers["X-Request-ID"] = request_id
    return response


# Schema changes and bootstrap users are intentionally managed outside app
# startup. Alembic migrations keep startup deterministic and prevent a default
# password from being recreated in production.
def create_app() -> FastAPI:
    # Production can hide route metadata without changing any business endpoint.
    openapi_url = (
        f"{settings.API_V1_STR}/openapi.json" if settings.ENABLE_API_DOCS else None
    )
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        openapi_url=openapi_url,
        docs_url="/docs" if settings.ENABLE_API_DOCS else None,
        redoc_url="/redoc" if settings.ENABLE_API_DOCS else None,
        # Global database handlers use this shared, sanitized response shape.
        responses={
            status.HTTP_409_CONFLICT: {
                "model": ErrorResponse,
                "description": "Database constraint conflict",
            },
            status.HTTP_500_INTERNAL_SERVER_ERROR: {
                "model": ErrorResponse,
                "description": "Internal server error",
            },
            status.HTTP_503_SERVICE_UNAVAILABLE: {
                "model": ErrorResponse,
                "description": "Database temporarily unavailable",
            },
        },
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    @application.middleware("http")
    async def add_security_headers(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        # Generate internally so untrusted client values cannot enter logs.
        request.state.request_id = str(uuid4())
        response = await call_next(request)
        return apply_standard_response_headers(response, request.state.request_id)

    @application.exception_handler(IntegrityError)
    async def database_integrity_error_handler(
        request: Request,
        error: IntegrityError,
    ) -> JSONResponse:
        # Do not log the exception text: SQL parameters can contain credentials.
        logger.warning(
            "Database constraint conflict during %s %s (%s) request_id=%s",
            request.method,
            request.url.path,
            type(error).__name__,
            request.state.request_id,
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Database constraint conflict"},
        )

    @application.exception_handler(OperationalError)
    async def database_operational_error_handler(
        request: Request,
        error: OperationalError,
    ) -> JSONResponse:
        # Connection details and SQL parameters must stay out of logs/responses.
        logger.error(
            "Database temporarily unavailable during %s %s (%s) request_id=%s",
            request.method,
            request.url.path,
            type(error).__name__,
            request.state.request_id,
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Database temporarily unavailable"},
            # Clients and health orchestrators receive an explicit retry hint.
            headers={"Retry-After": "5"},
        )

    @application.exception_handler(Exception)
    async def unexpected_error_handler(
        request: Request,
        error: Exception,
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", str(uuid4()))
        # Exception messages can contain input values; log only safe metadata.
        logger.error(
            "Unhandled application error during %s %s (%s) request_id=%s",
            request.method,
            request.url.path,
            type(error).__name__,
            request_id,
        )
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
        return apply_standard_response_headers(response, request_id)

    routers = (
        user.router,
        department.router,
        task.router,
        workhour.router,
        expentask.router,
        expen.router,
        cstshop.router,
        branchlist.router,
        serverlist.router,
        fetnetlist.router,
        ipcamlist.router,
    )
    for router in routers:
        application.include_router(router, prefix=settings.API_V1_STR)

    @application.get("/health", response_model=HealthResponse, tags=["Health"])
    def health_check() -> HealthResponse:
        return HealthResponse(
            status="ok",
            version=settings.PROJECT_VERSION,
        )

    @application.get("/ready", response_model=HealthResponse, tags=["Health"])
    def readiness_check(db: DatabaseSession) -> HealthResponse:
        # Readiness must fail when the database cannot serve application work.
        db.execute(text("SELECT 1"))
        return HealthResponse(
            status="ok",
            version=settings.PROJECT_VERSION,
        )

    @application.get("/api", include_in_schema=False)
    def root() -> RedirectResponse:
        return RedirectResponse(url=f"{settings.API_V1_STR}/user")

    return application


app = create_app()
