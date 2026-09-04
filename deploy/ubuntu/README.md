# Ubuntu VM deployment preparation

Target: dedicated Ubuntu 22.04.5 amd64 VM on the trusted LAN.
Branch: `refactor/vue3-fastapi-modernization`.
The LAN bind address and browser origin remain private environment values.
This directory is preparation only; it does not enable CI/CD or migrate data.

## Source database read-only inventory (2026-09-03)

- PostgreSQL 14.9 source, database `workhour`.
- Approximately 40.8 MiB, 15 public tables, Alembic revision `20260821_03`.
- A dedicated device-credential encryption key is configured; preserve it exactly.
- The source includes `sale_details`, which is not created by current Alembic
  migrations. Restore the entire database, not just the ORM's known tables.

## Staged procedure

1. Install Docker Engine and Compose (completed by the operator).
2. Prepare `/opt/workhour` and `/var/backups/workhour`. Keep backups and `.env`
   outside Git. Protect the environment file with root ownership and mode 0600.
3. Transfer a reviewed source snapshot including the current uncommitted monitoring
   changes; do not assume cloning GitHub already includes those changes.
4. Transfer the existing SECRET_KEY, DEVICE_CREDENTIAL_KEY and Zabbix configuration
   privately. Generate separate random hex DB passwords for the new VM only.
5. Check VM connectivity to the source database and Zabbix. Agree a final cutover
   time before pausing any writers to the old database.
6. Create a PostgreSQL custom-format whole-database dump with a compatible client
   (PostgreSQL 16 pg_dump can read PostgreSQL 14). Restore first into a new, empty
   target and validate all 15 tables, sequences, indexes and row counts.
7. Start only `db` initially. Restore with `pg_restore --no-owner --no-privileges
   --exit-on-error --single-transaction --role=workhour`, authenticating as
   `workhour_admin`. The destination database must be empty. Do not use `--clean`
   or restore over a nonempty database. Confirm required extensions and grants.
8. Verify the restored Alembic revision before manually running `migrate` if needed.
   Do not stamp or reset migration history. The current source is already at head.
9. Build/start `app` and `frontend`, test `/api` login, inventory reads, credential
   decryption without exposing passwords, and live Zabbix monitoring.
10. Before final cutover, pause ALL source writers with the owner's approval and
    take a final consistent dump. Rehearsal copies are not automatically current.
    Revalidate before directing users to the new URL. Keep the old DB intact.

Use `sudo docker compose --env-file .env -f compose.yml` from this directory.
Do not run full-stack `up` before completing the restore; a ready DB connection
alone does not establish that application tables/data were migrated.

## Safety and rollback

- Only frontend port 8082 binds to the target's LAN IP. There is no database or
  backend host port. Do not add public NAT or inbound Internet access.
- HTTP is the operator's explicit choice; login and API traffic are unencrypted.
  Limit access at the network firewall to trusted LANs. Docker-published ports
  require Docker-aware filtering; do not assume UFW alone blocks them.
- DB data persists in a Docker named volume. Never run `down -v`, prune volumes,
  or reset the data directory during deployment.
- Role creation runs only on a NEW volume; editing env passwords does not rotate
  existing PostgreSQL role passwords.
- Source code rollback does not roll back database schema. Require a backup and
  migration compatibility review before every schema-changing release.
- Once the new DB accepts writes, switching back to the old DB would lose those
  writes unless reconciled. A cutover rollback must account for that data.
- Keep an off-VM backup; a backup on the same VM alone is insufficient.

## CI/CD next phase (not yet enabled)

Keep pull-request tests on GitHub-hosted runners. The deployment must release the
SAME tested commit on the selected branch, use versioned image digests, serialize
deployments, and verify frontend and backend readiness after each deployment.
Never place production secrets in Git or execute untrusted pull-request jobs on
the production VM. Choose and authorize the private-network deployment mechanism
before installing a runner or granting a registry/deployment token. Initial
delivery should be manually approved; enable unattended deployment only after
the first database migration and restore/rollback rehearsal are verified.

References:
- https://docs.docker.com/engine/install/ubuntu/
- https://www.postgresql.org/docs/16/app-pgdump.html
- https://docs.github.com/en/actions/reference/security/secure-use

## Application CI/CD

`.github/workflows/production-deploy.yml` verifies both applications and builds
their images entirely on GitHub-hosted runners. After the `production`
environment allows the release, images are published to GHCR under immutable
Git commit tags.

The production VM does not run GitHub Actions. Its root-owned systemd timer
executes the locally installed `update-from-ghcr.sh`, which checks the selected
branch SHA, pulls both matching images, verifies their embedded revision label,
and invokes the locally installed `deploy-application.sh`. The deployment
script serializes deployments, checks that the database is already at the
release's Alembic revision, updates only `app` and `frontend`, performs health
checks, and rolls back those images on failure. Neither script runs migrations,
removes volumes, nor modifies `.env`.

Security requirements before enabling the job:

- Do not install a self-hosted GitHub Actions runner on the production VM while
  this repository is public. Fork pull requests are not trusted production
  workloads and Docker access is effectively root-equivalent.
- Create the GitHub `production` environment and restrict its deployment branch
  to `refactor/vue3-fastapi-modernization`. Require an approver when the
  repository visibility and GitHub plan provide that protection rule.
- Protect that branch: require the CI checks and disallow force pushes.
- Keep `/opt/workhour/deploy/ubuntu/.env` only on the VM. No production secret
  is required in GitHub Actions.
- Create `/opt/workhour/runner-state` with mode 0700 for the deployment account and
  grant only that account's group read access to `.env` (root ownership, mode
  0640). Do not grant Docker access to additional accounts.
- Make the two GHCR packages public so the VM needs no registry credential. If
  private images are required later, use a read-only package credential stored
  only on the VM, never a repository secret exposed to production jobs.
