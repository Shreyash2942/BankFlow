# Changelog

## Unreleased — Phase 3 Streaming Platform

### Day 16 — Spark streaming foundation (2026-10-28)

- Added a Spark 3.5.1 Structured Streaming consumer with a pinned Scala 2.12 Kafka connector, bounded Kafka batches, and explicit fail-on-data-loss behavior.
- Added the full version-1 Spark schema, envelope/payload validation, exact decimal parsing, and retained Kafka replay metadata.
- Added HDFS checkpoints, restart-safe offset progress, structured batch metrics, and secret-safe invalid-record quarantine metadata.
- Verified three live batches through the standalone Spark master: 50 valid events, one malformed JSON record, and two structurally invalid records, including checkpoint resume without replay.

### Day 15 — Synthetic event generator (2026-10-27)

- Added lazy, deterministic generation of fictional transaction, authentication, decline, lock, and session events with exact evolving balances.
- Added configurable event count, maximum publication rate, customer/ATM population, seed, dry-run validation, and acknowledged Kafka publication.
- Added optional validated ATM provenance to both version-1 payload variants without invalidating existing events.
- Added generator, schema-compatibility, rate-pacing, identity, balance, CLI, and 10,000-event stress coverage; all 105 service-free and 134 opt-in tests pass.
- Verified an isolated 40-event live Kafka publish/consume round trip with matching counts, unique event IDs, and complete ATM attribution.

## v1.0.0 — BankFlow Application Platform (2026-10-26)

- Completed 92 service-free and 121 full application tests, plus all 67 dbt data tests and a successful five-task Airflow DAG run.
- Added isolated Kafka integration fixtures and a service-free Airflow release-contract test.
- Added a three-job GitHub Actions quality pipeline for Python checks, live PostgreSQL/Redis/Kafka integrations, and dbt analytics.
- Published the Version 1 architecture, four live application screenshots, validation evidence, and release notes.
- Promoted package and application metadata to `v1.0.0`.

### Day 12 — Airflow analytics orchestration (2026-10-14)

- Added the daily `bankflow_daily_analytics` DAG with PostgreSQL availability and configurable consumed-event freshness gates.
- Orchestrated dbt staging, intermediate/mart, test, and documentation stages with explicit dependencies, bounded execution, retries, and secret-free failure logging.
- Deployed and parsed the DAG in Airflow 2.9.3, then completed a five-task test run with all 67 dbt tests passing.
- Documented deployment, Airflow UI and CLI triggers, container-local database settings, and first-run empty-source behavior.

### Day 13 — Analytics and platform status (2026-10-14)

- Added an authenticated Streamlit analytics dashboard backed exclusively by the Version 1 dbt marts, with shared date filtering, exact transaction amounts, authentication outcomes, and two focused charts.
- Added a session-independent platform-status page with concurrent bounded probes for PostgreSQL, Redis, Kafka, and Airflow plus local dbt artifact summaries.
- Reported the Airflow scheduler separately from DAG availability; the status page now recognizes the completed Day 12 DAG definition.
- Aligned both pages with the supplied UI references and expanded validation to 91 service-free tests and all 120 tests with service opt-ins.

### Day 11 — dbt analytics (2026-10-12)

- Added PostgreSQL event sources, materialized transaction/authentication staging snapshots, terminal transaction metrics, and three Version 1 analytics marts.
- Added 67 source, schema, controlled-value, key, financial, and reconciliation tests plus generated dbt documentation.
- Verified exact-money aggregation with a controlled nine-event fixture and preserved Alembic rollback through migration-safe staging materialization.

### Day 10 — Kafka consumer and event store (2026-10-09)

- Added a manual-commit, `read_committed` Kafka consumer with canonical envelope validation, structured secret-free logs, and graceful signal shutdown.
- Added Alembic revision `0003` and the append-only `consumed_events` store for exact payloads and Kafka metadata.
- Added atomic duplicate protection by event ID and topic/partition/offset; database failures leave offsets uncommitted, while replay after offset failure is safe.
- Added deterministic consumer tests, PostgreSQL event-store tests, and a live Kafka-to-PostgreSQL test covering persistence, replay, and invalid messages.
- Isolated the Day 9 Kafka smoke test to a unique topic; 83 service-free tests and all 112 tests with service opt-ins pass.

### Day 9 — Kafka producer integration (2026-10-06)

- Added an idempotent, all-acknowledgement Kafka producer with bounded delivery callbacks, aggregate partition keys, safe headers, and stable unavailable-broker errors.
- Published authentication, card-lock, balance, withdrawal lifecycle, deposit, account-close, and session-end events only after owning PostgreSQL commits.
- Kept committed banking operations authoritative when Kafka is unavailable and documented the remaining database-to-broker delivery gap.
- Corrected the dedicated broker's advertised listener for host clients and verified Kafka 3.7.1 metadata plus an acknowledged produce/consume round trip.
- Added six producer unit tests, three live post-commit runtime tests, and one live Kafka test; 74 service-free tests and all 100 tests with service opt-ins pass.

### Day 8 — Kafka event design (2026-10-05)

- Added a closed, versioned event envelope with UUID4 identity, typed event names, UTC timestamps, and a fixed source.
- Added discriminated transaction and authentication payloads plus factories for the ten initial BankFlow event types.
- Preserved exact decimal money during JSON serialization and excluded credentials, PIN material, card/session tokens, and other secrets from the contract.
- Added 17 schema/factory tests; 68 service-free tests and all 90 tests with live PostgreSQL/Redis/Streamlit opt-in now pass.

### Day 7 — Streamlit ATM interface (2026-10-01)

- Added the themed Streamlit shell, fictional demo-card selection, masked PIN authentication, and Redis-backed session navigation.
- Added authenticated dashboard, withdrawal, deposit, and transaction-history pages using the existing exact-money service boundary.
- Added explicit success, warning, error, demo-mode, reset, and end-session states.
- Added an atomic fixed-demo reset and a live Streamlit acceptance path; 51 fast tests and 22 live PostgreSQL/Redis/UI tests now pass.

### Day 6 — Transaction engine (2026-09-30)

- Added authenticated account balance inquiry, withdrawal, deposit, and transaction-history services.
- Added strict finite `Decimal` cent validation, insufficient-funds persistence, exact balance snapshots, UUID transactions, and balance overflow protection.
- Added caller-transaction audit records, configurable zero-balance closure, subject authorization, and rollback verification.
- Expanded validation to 51 fast tests and 20 live PostgreSQL/Redis tests; all 71 pass with service opt-in.

### Day 5 — Authentication and Redis (2026-09-29)

- Added shared salted scrypt PIN hashing and verification with secret-safe request/result schemas.
- Added authenticated Redis connectivity, expiring failed-attempt counters, hashed session-token keys, and expiring sessions.
- Added caller-transaction authentication orchestration, card-row locking, permanent PostgreSQL lockout on the third failure, and secret-free audit events.
- Isolated live Redis tests on database 1 with unique prefixes and expanded validation to 30 fast tests and 14 live PostgreSQL/Redis tests; all 44 pass with service opt-in.

### Day 4 — Repository layer (2026-09-28)

- Added customer, account, card, and transaction repositories using caller-owned SQLAlchemy sessions.
- Added typed lookups, deterministic transaction history, guarded pagination, transaction creation, and versioned balance updates.
- Added repository exceptions for missing, invalid, conflicting, and database-rejected operations.
- Expanded validation to 15 fast tests and 11 live PostgreSQL tests; all 26 pass with database opt-in.

### Day 3 — Core domain model (2026-09-27)

- Added customer, account, card, transaction, and audit-event SQLAlchemy models with typed relationships.
- Added checked status/type enums, UUID identifiers, timezone-aware timestamps, restrictive history relationships, and account versioning.
- Added exact `NUMERIC(18,2)` balances and transaction snapshots with database constraints for invalid money states.
- Added Alembic revision `0002` and applied it to isolated test and application databases.
- Added an idempotent fictional demo seed with a salted PIN hash and $500.00 starting balance.
- Expanded validation to 15 unit and eight live PostgreSQL tests.

### Day 2 — Database foundation (2026-09-24)

- Added validated environment settings, safe credential handling, explicit PostgreSQL engines, transaction-scoped sessions, and a health command.
- Added Alembic revision `0001` for the application schema.
- Provisioned isolated application/test databases and non-superuser owner roles in the dedicated container.
- Added 12 unit cases and five live PostgreSQL tests; recorded migration and connectivity evidence.
- Added guarded local credential rotation and concise pytest tracebacks after a stopped-service failure exposed connection arguments.

### Day 1 — Foundation (2026-09-22)

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
