# Changelog

## Unreleased — Day 2 database foundation (2026-09-24)

- Added validated environment settings, safe credential handling, explicit PostgreSQL engines, transaction-scoped sessions, and a health command.
- Added Alembic revision `0001` for the application schema.
- Provisioned isolated application/test databases and non-superuser owner roles in the dedicated container.
- Added 12 unit cases and five live PostgreSQL tests; recorded migration and connectivity evidence.
- Added guarded local credential rotation and concise pytest tracebacks after a stopped-service failure exposed connection arguments.

## Unreleased — Day 1 foundation (2026-09-22)

- Imported canonical requirements, architecture, design, tasks, and project memory.
- Preserved the academic project with checksums and retained the baseline analysis.
- Added an installable `src/bankflow` package and planned component directories.
- Added a verified Python 3.14 development environment, pinned dependencies, local configuration template, and setup instructions.
- Documented the existing Data-Lab connection strategy and pending live checks.

No application release has been tagged. Domain services and the Streamlit UI remain planned.

### Dedicated container follow-up

- Adopted the user-created `bankflow` container and dedicated runtime volume.
- Updated host connection ports and documented all supplied service endpoints without passwords or tokens.
- Distinguished internal HDFS/Spark RPC from host mappings and recorded copied storage-path defaults.
