#!/usr/bin/env bash
# Deploy tested application images without modifying PostgreSQL or its volume.
set -Eeuo pipefail

if [[ $# -ne 1 || ! "$1" =~ ^[0-9a-f]{40}$ ]]; then
  echo "Usage: $0 <40-character-git-sha>" >&2
  exit 2
fi

readonly release_sha="$1"
readonly deploy_dir="${WORKHOUR_DEPLOY_DIR:-/opt/workhour/deploy/ubuntu}"
readonly compose_file="$deploy_dir/compose.yml"
readonly env_file="$deploy_dir/.env"
readonly lock_file="${WORKHOUR_DEPLOY_LOCK:-/opt/workhour/runner-state/deploy.lock}"
readonly backend_image="workhour-backend:$release_sha"
readonly frontend_image="workhour-frontend:$release_sha"

for required in docker curl flock; do
  command -v "$required" >/dev/null || {
    echo "Required command is missing: $required" >&2
    exit 1
  }
done
[[ -r "$compose_file" && -r "$env_file" ]] || {
  echo "Production Compose or environment file is missing." >&2
  exit 1
}

mkdir -p "$(dirname "$lock_file")"
exec 9>"$lock_file"
flock -n 9 || {
  echo "Another WorkHour deployment is already running." >&2
  exit 1
}

compose() {
  BACKEND_IMAGE="${BACKEND_IMAGE:-$backend_image}" \
  FRONTEND_IMAGE="${FRONTEND_IMAGE:-$frontend_image}" \
    docker compose --env-file "$env_file" --file "$compose_file" "$@"
}

compose config --quiet
db_container="$(compose ps --quiet db)"
app_container="$(compose ps --quiet app)"
frontend_container="$(compose ps --quiet frontend)"
[[ -n "$db_container" && -n "$app_container" && -n "$frontend_container" ]] || {
  echo "The existing db, app, and frontend containers must be running." >&2
  exit 1
}

# Schema changes remain an explicit maintenance operation. A code deployment
# stops if its Alembic head has not already been applied to the database.
db_revision="$(docker exec "$db_container" psql -X -A -t \
  -U workhour_admin -d workhour \
  -c 'SELECT version_num FROM public.alembic_version' | tr -d '[:space:]')"
image_revision="$(docker run --rm "$backend_image" \
  python -m alembic heads | awk 'NR == 1 {print $1}')"
[[ -n "$db_revision" && "$db_revision" == "$image_revision" ]] || {
  echo "Database migration revision does not match the release; deployment stopped." >&2
  exit 1
}

old_backend_image="$(docker inspect --format '{{.Config.Image}}' "$app_container")"
old_frontend_image="$(docker inspect --format '{{.Config.Image}}' "$frontend_container")"

rollback() {
  local status=$?
  trap - ERR
  if (( status != 0 )); then
    echo "Deployment failed; restoring the previous application images." >&2
    BACKEND_IMAGE="$old_backend_image" FRONTEND_IMAGE="$old_frontend_image" \
      compose up --detach --no-deps --no-build --wait --wait-timeout 180 app frontend
  fi
  exit "$status"
}
trap rollback ERR

compose up --detach --no-deps --no-build --wait --wait-timeout 180 app frontend
frontend_endpoint="$(compose port frontend 8080)"
[[ -n "$frontend_endpoint" ]] || {
  echo "The frontend does not have a published endpoint." >&2
  false
}
curl --fail --silent --show-error --max-time 10 \
  "http://$frontend_endpoint/healthz" >/dev/null
compose exec -T app python -c \
  "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5566/ready', timeout=10)" \
  </dev/null

trap - ERR
printf 'Deployed WorkHour release %s successfully.\n' "$release_sha"
compose ps
