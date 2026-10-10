# Changelog

## Unreleased — Day 10 Kafka consumer and event store (2026-10-09)

- Added a manual-commit, `read_committed` Kafka consumer with canonical envelope validation, structured secret-free logs, and graceful signal shutdown.
- Added Alembic revision `0003` and the append-only `consumed_events` store for exact payloads and Kafka metadata.
- Added atomic duplicate protection by event ID and topic/partition/offset; database failures leave offsets uncommitted, while replay after offset failure is safe.
- Added deterministic consumer tests, PostgreSQL event-store tests, and a live Kafka-to-PostgreSQL test covering persistence, replay, and invalid messages.
- Isolated the Day 9 Kafka smoke test to a unique topic; 83 service-free tests and all 112 tests with service opt-ins pass.

## Unreleased — Day 9 Kafka producer integration (2026-10-06)

- Added an idempotent, all-acknowledgement Kafka producer with bounded delivery callbacks, aggregate partition keys, safe headers, and stable unavailable-broker errors.
- Published authentication, card-lock, balance, withdrawal lifecycle, deposit, account-close, and session-end events only after owning PostgreSQL commits.
- Kept committed banking operations authoritative when Kafka is unavailable and documented the remaining database-to-broker delivery gap.
- Corrected the dedicated broker's advertised listener for host clients and verified Kafka 3.7.1 metadata plus an acknowledged produce/consume round trip.
- Added six producer unit tests, three live post-commit runtime tests, and one live Kafka test; 74 service-free tests and all 100 tests with service opt-ins pass.

## Unreleased — Day 8 Kafka event design (2026-10-05)

- Added a closed, versioned event envelope with UUID4 identity, typed event names, UTC timestamps, and a fixed source.
- Added discriminated transaction and authentication payloads plus factories for the ten initial BankFlow event types.
- Preserved exact decimal money during JSON serialization and excluded credentials, PIN material, card/session tokens, and other secrets from the contract.
- Added 17 schema/factory tests; 68 service-free tests and all 90 tests with live PostgreSQL/Redis/Streamlit opt-in now pass.

## Unreleased — Day 7 Streamlit ATM interface (2026-10-01)

- Added the themed Streamlit shell, fictional demo-card selection, masked PIN authentication, and Redis-backed session navigation.
- Added authenticated dashboard, withdrawal, deposit, and transaction-history pages using the existing exact-money service boundary.
- Added explicit success, warning, error, demo-mode, reset, and end-session states.
- Added an atomic fixed-demo reset and a live Streamlit acceptance path; 51 fast tests and 22 live PostgreSQL/Redis/UI tests now pass.

## Unreleased — Day 6 transaction engine (2026-09-30)

- Added authenticated account balance inquiry, withdrawal, deposit, and transaction-history services.
- Added strict finite `Decimal` cent validation, insufficient-funds persistence, exact balance snapshots, UUID transactions, and balance overflow protection.
- Added caller-transaction audit records, configurable zero-balance closure, subject authorization, and rollback verification.
- Expanded validation to 51 fast tests and 20 live PostgreSQL/Redis tests; all 71 pass with service opt-in.

## Unreleased — Day 5 authentication and Redis (2026-09-29)

- Added shared salted scrypt PIN hashing and verification with secret-safe request/result schemas.
- Added authenticated Redis connectivity, expiring failed-attempt counters, hashed session-token keys, and expiring sessions.
- Added caller-transaction authentication orchestration, card-row locking, permanent PostgreSQL lockout on the third failure, and secret-free audit events.
- Isolated live Redis tests on database 1 with unique prefixes and expanded validation to 30 fast tests and 14 live PostgreSQL/Redis tests; all 44 pass with service opt-in.

## Unreleased — Day 4 repository layer (2026-09-28)

- Added customer, account, card, and transaction repositories using caller-owned SQLAlchemy sessions.
- Added typed lookups, deterministic transaction history, guarded pagination, transaction creation, and versioned balance updates.
- Added repository exceptions for missing, invalid, conflicting, and database-rejected operations.
- Expanded validation to 15 fast tests and 11 live PostgreSQL tests; all 26 pass with database opt-in.

## Unreleased — Day 3 core domain model (2026-09-27)

- Added customer, account, card, transaction, and audit-event SQLAlchemy models with typed relationships.
- Added checked status/type enums, UUID identifiers, timezone-aware timestamps, restrictive history relationships, and account versioning.
- Added exact `NUMERIC(18,2)` balances and transaction snapshots with database constraints for invalid money states.
- Added Alembic revision `0002` and applied it to isolated test and application databases.
- Added an idempotent fictional demo seed with a salted PIN hash and $500.00 starting balance.
- Expanded validation to 15 unit and eight live PostgreSQL tests.

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

No application release has been tagged. The planned v0.5.0 Streamlit milestone is implemented locally.

### Dedicated container follow-up

- Adopted the user-created `bankflow` container and dedicated runtime volume.
- Updated host connection ports and documented all supplied service endpoints without passwords or tokens.
- Distinguished internal HDFS/Spark RPC from host mappings and recorded copied storage-path defaults.
