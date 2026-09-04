#!/bin/sh
# Runs only when PostgreSQL initializes an EMPTY data volume.
# The API receives a separate, non-superuser role. Read the password from the
# container environment, not process arguments; psql quotes it as a SQL literal.
set -eu
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  --set=ON_ERROR_STOP=1 <<'SQL'
\getenv app_password WORKHOUR_APP_PASSWORD
CREATE ROLE workhour LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD :'app_password';
ALTER DATABASE workhour OWNER TO workhour;
GRANT USAGE, CREATE ON SCHEMA public TO workhour;
SQL
