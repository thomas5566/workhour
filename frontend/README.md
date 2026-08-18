# WorkHour Frontend

Vue 3 frontend for the FastAPI backend in `../backend`.

## Windows development

Requirements: Node.js 20.19 or newer and pnpm 11.

```powershell
pnpm install --frozen-lockfile
pnpm dev
```

Vite listens on `http://127.0.0.1:8080` and proxies `/api` to
`http://127.0.0.1:5566`. Copy `.env.example` to `.env.local` when the backend
uses another address. Keep `VITE_API_BASE_URL=/api` for same-origin production
deployments.

## Verification

```powershell
pnpm lint -- --max-warnings=0
pnpm test
pnpm build
```

The application uses Vue's compatibility build temporarily so existing Options
API business views continue to run while they are migrated incrementally. New
code should use Vue 3 APIs and must not introduce additional compatibility
warnings.

## Docker

For the complete PostgreSQL, FastAPI, migration, and frontend container stack,
run `docker compose up --build` from the repository root. See `../DOCKER.md`.
