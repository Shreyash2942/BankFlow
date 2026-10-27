# BankFlow v1.0.0 — Application Platform

Release date: 2026-10-26

BankFlow v1.0.0 completes the first production-shaped portfolio milestone: a fictional ATM application connected to an event-driven operational analytics platform.

## Highlights

- Exact `Decimal` balance inquiries, withdrawals, deposits, declines, histories, and configurable zero-balance closure.
- PostgreSQL system of record with Alembic migrations, constrained models, repository boundaries, and isolated application/test roles.
- Salted PIN verification, three-attempt durable card lockout, expiring Redis counters, and tokenized sessions.
- Streamlit ATM, analytics, and live platform-status experiences aligned with the supplied visual references.
- Closed version-1 event envelopes and acknowledged Kafka publication after successful business commits.
- Validating Kafka consumer with structured logs, manual offset commits, event/position deduplication, and PostgreSQL event storage.
- Six dbt models with 67 source, schema, financial, grain, and reconciliation tests.
- A five-stage daily Airflow DAG for health, freshness, dbt transformations, tests, and documentation.
- GitHub Actions jobs for Python quality, live PostgreSQL/Redis/Kafka integration tests, and dbt builds.

## Validation summary

- 92 service-free application tests passed.
- 121 tests passed with PostgreSQL, Redis, Streamlit, and Kafka integrations enabled.
- Ruff lint and format checks passed across application, DAG, migrations, scripts, and tests.
- Package dependency and Python 3.14 environment checks passed for `bankflow-atm==1.0.0`.
- dbt completed 6 models and 67 data tests: `PASS=73`, `WARN=0`, `ERROR=0`, `SKIP=0`.
- Airflow reported zero DAG import errors and completed all five `bankflow_daily_analytics` tasks successfully for logical date 2026-10-26.

Detailed evidence is in [DAY14_VALIDATION.md](DAY14_VALIDATION.md), and visual evidence is in [V1_PORTFOLIO.md](V1_PORTFOLIO.md).

## Upgrade and operation

Fresh environments should follow the repository [README](../README.md) and [environment guide](ENVIRONMENT.md), provision isolated credentials, run `alembic upgrade head`, seed the fictional demo, and start Streamlit plus the operational consumer. Existing Day 13 environments require no schema migration for this release.

## Known reliability boundary

TD-001 remains open: events are published after the owning database commit without a transactional outbox. A broker outage does not roll back a successful banking operation, but it can create an analytics gap for an event that was never published. Consumer deduplication protects replayed events; it cannot recover an event absent from Kafka.

## Next milestone

Phase 3 begins with Day 15's deterministic synthetic event generator, followed by Spark Structured Streaming and Iceberg lakehouse work. Those features are not included in v1.0.0.

