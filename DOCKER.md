# Full-stack Docker development

The root Compose project starts PostgreSQL, applies Alembic migrations, starts
FastAPI, and serves the Vue production build through an unprivileged Nginx
container.

## Windows PowerShell

```powershell
Copy-Item .env.example .env
# Replace POSTGRES_PASSWORD, SECRET_KEY, and DEVICE_CREDENTIAL_KEY before continuing.
docker compose config --quiet
docker compose up --build
```

## Optional infrastructure monitoring

The manager-only `/#/monitoring` page uses Zabbix as the single monitoring
source. It shows Zabbix availability, active problems, and the supported
FortiGate metrics already collected by Zabbix. Set these values in the ignored
local `.env` or `.env.production` file:

```dotenv
ZABBIX_URL=http://zabbix.example.com/api_jsonrpc.php
ZABBIX_TOKEN=replace-with-a-read-only-api-token
MONITORING_TIMEOUT_SECONDS=5
```

No FortiGate REST API token is required when Zabbix already monitors the
firewalls through SNMP. Use a dedicated read-only Zabbix service account. The
backend validates URLs, keeps the token server-side, applies a short timeout,
and returns only sanitized health fields to the browser.

Open `http://127.0.0.1:8080`. Nginx forwards browser requests under `/api` to
the backend container. Swagger remains available directly at
`http://127.0.0.1:5566/docs` when API documentation is enabled.

Useful commands:

```powershell
docker compose ps
docker compose logs -f frontend app migrate db
docker compose down
```

## Device credential encryption

Server and IP camera passwords are encrypted before they are stored. API
responses and inventory screens only report whether a password is configured;
they never return the secret itself.

Generate a dedicated key once and store it in `.env` or `.env.production`:

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy that output to `DEVICE_CREDENTIAL_KEY`. Keep a protected backup: losing or
changing this key makes existing encrypted passwords unreadable. Do not commit
the real key to Git.

After backing up the database, update the column types and inspect how many
legacy plaintext values require migration:

```powershell
docker compose run --rm migrate
docker compose run --rm app python -m app.scripts.encrypt_device_credentials
```

The second command is read-only. Apply the conversion only after checking its
counts and confirming the key backup:

```powershell
docker compose run --rm app python -m app.scripts.encrypt_device_credentials --apply
```

`docker compose down` preserves the PostgreSQL volume. To deliberately delete
all local container database data, use `docker compose down --volumes`.

## External/production database smoke test

The external-database Compose file starts only FastAPI and the frontend. It
intentionally has no database or migration service, so an existing database is
not automatically changed during startup.

```powershell
Copy-Item .env.production.example .env.production
# Set EXTERNAL_DATABASE_URL, SECRET_KEY, and DEVICE_CREDENTIAL_KEY before continuing.
docker compose --env-file .env.production `
  -f docker-compose.production-db.yml config --quiet
docker compose --env-file .env.production `
  -f docker-compose.production-db.yml up --build -d
```
