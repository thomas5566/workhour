# WorkHour Backend

## Local development

Requires Python 3.12.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

`win-requirements.txt` remains available as a backwards-compatible Windows
alias for `requirements-dev.txt`.

Update `.env` with a secure `SECRET_KEY` and the correct database connection,
then start the API:

```powershell
uvicorn app.main:app --reload --port 5566
```

The example `SECRET_KEY` is intentionally rejected at startup. CORS entries
must be explicit `http://` or `https://` origins without wildcards, paths, or
embedded credentials; provide production origins through
`BACKEND_CORS_ORIGINS` as a JSON list.

JWT signing uses the shared `SECRET_KEY` and permits only `HS256`, `HS384`, or
`HS512`; the default and example configuration remain `HS256`. Unsupported,
asymmetric, or unsigned algorithms fail settings validation during startup.

The liveness endpoint is available at `http://localhost:5566/health`, database
readiness at `http://localhost:5566/ready`, and the OpenAPI document at
`http://localhost:5566/api/openapi.json`.

API documentation is enabled by default for development. Set
`ENABLE_API_DOCS=false` in production to disable `/docs`, `/redoc`, and
`/api/openapi.json` together; business routes and health endpoints remain
available. Compose forwards this toggle and the JWT algorithm/expiry settings.

The application uses a single `fastapi-login` authentication flow. Startup
does not create default users or data; provision the first administrator using
an explicit deployment or administration workflow.

Passwords must contain at least 8 characters and must not exceed bcrypt's
72-byte UTF-8 input limit. Oversized login attempts use the same generic 401
response as other invalid credentials.

Successful login responses include `Cache-Control: no-store` and
`Pragma: no-cache`, preventing bearer tokens from being retained by browser or
intermediary caches. The response body remains compatible with the Vue client.

All API responses disable MIME sniffing, framing, referrer disclosure, camera,
microphone, and geolocation access. HTTP Strict Transport Security remains the
responsibility of the production HTTPS reverse proxy so local HTTP development
is not accidentally pinned or redirected.

Every response includes a server-generated UUIDv4 `X-Request-ID`. Database
conflict and availability logs include the same ID without logging SQL or input
values. CORS exposes this response header to the configured Vue origins; client-
supplied request IDs are intentionally ignored.

Unexpected application exceptions return the documented, sanitized
`500 {"detail":"Internal server error"}` envelope with the same security headers
and request ID. Logs retain only safe request metadata and the exception class,
not the exception message or request values.

During Phase 1, create endpoints keep the legacy `200 OK` response contract.
The current Vue client refreshes several forms only when the status is exactly
`200`; these endpoints can move to `201 Created` after the frontend accepts any
successful 2xx response.

Workhour collection endpoints accept validated `skip` and `limit` query
parameters. Their no-parameter defaults remain 100 records for a user's list
and 1000 records for the manager list, preserving current Vue behavior.
The repository also preloads the complete `WorkhourFull` relationship graph in
a fixed set of queries, avoiding per-row lazy-loading overhead.

Database uniqueness and foreign-key conflicts return a sanitized `409 Conflict`
response. SQL statements and request values are intentionally excluded from the
response and constraint-conflict log message.

Temporary database connection or availability failures return a sanitized
`503 Service Unavailable` response with `Retry-After: 5`. This also makes
`/ready` report an actionable service status while `/health` remains independent
of database availability. Both database error envelopes are documented in the
OpenAPI schema as `ErrorResponse`; duplicate-resource pre-checks also use 409.

## Tests

```powershell
python -m pytest -q
python -m ruff check .
```

Pytest treats warnings as errors, including SQLAlchemy relationship warnings
and framework deprecations, so the pinned dependency stack remains upgrade-ready.

GitHub Actions runs the same checks with Python 3.12 on both Windows and
Linux whenever backend or backend-workflow files change. A separate Linux job
also validates Compose, builds the backend image, and polls `/ready` in a
temporary container.

## Database migrations

For a new database, apply every migration before starting the API:

```powershell
python -m alembic upgrade head
python -m alembic current
```

For an existing WorkHour database, take a database backup first. If its
tables already match the legacy schema, mark the initial schema as present,
then apply the timestamp conversion migration:

```powershell
python -m alembic stamp 20260817_01
python -m alembic upgrade head
```

Do not run `stamp` on an empty database: stamping records a revision without
creating any tables. The commands use `DATABASE_URL` from `.env`.

The Days Off and Dudo Transactions application features are retired. Their
legacy `daysoff` and `transactions` tables remain in the migration history and
ORM metadata for data retention; removing those tables requires a separately
approved migration and backup plan.

## Docker Compose

Set `POSTGRES_PASSWORD` and `SECRET_KEY` in the shell or an untracked `.env`
file before running:

```powershell
docker compose up --build
```

Compose first waits for PostgreSQL, runs `alembic upgrade head` in a one-shot
migration container, and starts the non-root API container only after the
migration succeeds. The production-style Compose service intentionally omits
source bind mounts and Uvicorn reload mode; use the local-development command
above when hot reload is needed.
