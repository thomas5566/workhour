# Full-stack Docker development

The root Compose project starts PostgreSQL, applies Alembic migrations, starts
FastAPI, and serves the Vue production build through an unprivileged Nginx
container.

## Windows PowerShell

```powershell
Copy-Item .env.example .env
# Replace POSTGRES_PASSWORD and SECRET_KEY in .env before continuing.
docker compose config --quiet
docker compose up --build
```

Open `http://127.0.0.1:8080`. Nginx forwards browser requests under `/api` to
the backend container. Swagger remains available directly at
`http://127.0.0.1:5566/docs` when API documentation is enabled.

Useful commands:

```powershell
docker compose ps
docker compose logs -f frontend app migrate db
docker compose down
```

`docker compose down` preserves the PostgreSQL volume. To deliberately delete
all local container database data, use `docker compose down --volumes`.

## External/production database smoke test

The external-database Compose file starts only FastAPI and the frontend. It
intentionally has no database or migration service, so an existing database is
not automatically changed during startup.

```powershell
Copy-Item .env.production.example .env.production
# Set EXTERNAL_DATABASE_URL and SECRET_KEY before continuing.
docker compose --env-file .env.production `
  -f docker-compose.production-db.yml config --quiet
docker compose --env-file .env.production `
  -f docker-compose.production-db.yml up --build -d
```
