# Day 11 dbt Analytics Validation

Validated on 2026-10-12 with dbt Core 1.8.7 and dbt-postgres 1.8.2 in the
dedicated `bankflow` container against PostgreSQL 14.22.

## Delivered behavior

- The environment-only dbt profile connects to either BankFlow database
  without storing credentials in the repository.
- PostgreSQL source tests validate the Day 10 `consumed_events` contract before
  downstream models run.
- Transaction and authentication staging snapshots cast version-1 JSON payloads
  into typed columns and retain envelope and Kafka lineage without blocking
  Alembic event-store rollback.
- `int_transaction_metrics` emits one terminal fact per transaction.
- Daily transaction, authentication, and account-activity marts have explicit
  grains and deterministic keys.
- Exact monetary values remain PostgreSQL `numeric(18, 2)` through every layer.
- Generic and singular tests enforce source integrity, model keys, controlled
  values, nonnegative metrics, bounded rates, and source-to-mart reconciliation.

## Automated checks

`dbt debug` passed against the isolated test database. `dbt build
--full-refresh` completed successfully against both the test and application
databases with 6 models, 67 data tests, and 1 source.

A controlled nine-event dataset exercised five authentication outcomes and four
terminal transactions. The verified results were:

```text
daily transactions: events=4 successful=3 declined=1 requested=115.25 completed=35.25
authentication: events=5 known-card=4 unknown-card=1
account activity: transactions=4 withdrawals=2 deposits=1 latest-balance=85.25 auth-events=4
```

The fixture rows were removed afterward and the test target was rebuilt, leaving
the source and marts clean. `dbt docs generate` produced `manifest.json`,
`catalog.json`, and the static documentation site under ignored `dbt/target/`.
The complete application suite also passes with all PostgreSQL, Redis, Kafka,
and Streamlit opt-ins enabled: 112 tests passed. This includes Alembic downgrade
and re-upgrade coverage, confirming that materialized staging snapshots do not
block migration rollback.

The incremental Graphify refresh covers 143 source files and produces 1,107
nodes, 1,845 edges, and 70 communities. The Day 11 analytics layer forms its own
32-node community, and graph-assisted queries use an estimated 96.3x fewer
tokens than loading the full corpus.

## Runbook

See `dbt/README.md` for model semantics and container commands. The profile
requires `BANKFLOW_DBT_DATABASE`, `BANKFLOW_DBT_USER`, and
`BANKFLOW_DBT_PASSWORD`; it defaults to the container-local PostgreSQL endpoint
and the `bankflow_analytics` target schema.

## Reliability boundary

These marts reflect events successfully persisted by the Day 10 consumer. They
cannot reconstruct operations lost in ADR-010's accepted database-commit to
Kafka-publication gap, and freshness depends on the consumer and scheduled dbt
execution.
