# ADR-012: Version 1 Analytics from the Validated Event Store

- **Status:** Accepted
- **Date:** 2026-10-12

## Context

BankFlow needs operational transaction and authentication analytics without
coupling reporting queries to mutable banking tables. The Day 10 consumer
already validates versioned event envelopes and stores them idempotently in
PostgreSQL with exact decimal values serialized as strings.

## Decision

dbt reads only `bankflow.consumed_events` for Version 1 analytics. Staging
snapshot tables cast the two payload families into typed columns and retain
their envelope and Kafka provenance. Tables avoid persistent PostgreSQL view
dependencies that would block Alembic rollback of the event-store migration.
An intermediate view selects the latest terminal event for
each transaction identifier, excluding pending withdrawal requests and the
account-close lifecycle notification that can repeat a completed withdrawal.

Three table marts expose explicit grains:

- one row per date, currency, and transaction type for daily transactions;
- one row per date, event type, and outcome for authentication metrics;
- one row per date and known account for combined account activity.

Money remains `numeric(18, 2)`. Unknown-card authentication failures remain in
the authentication mart but cannot appear in the account mart because they do
not contain an account identifier. Generic tests enforce keys, required values,
and controlled enums; singular tests reconcile mart counts and constrain
financial metrics.

## Consequences

Analytics inherit the consumer's validated schema, duplicate protection, and
known producer publication gap. Staging snapshots and table marts require a dbt
rebuild to reflect new events. Every layer remains inspectable for audit and
future orchestration by the Day 12 Airflow DAG.
