# BankFlow dbt Analytics

This project transforms validated version-1 events from
`bankflow.consumed_events` into operational analytics. Staging snapshots and the
three business-facing marts are tables; the intermediate model is a view in the
configured target schema. Materialized staging avoids database dependencies that
would block Alembic from rolling back the event-store migration.

## Models

- `stg_transaction_events` and `stg_authentication_events` type the JSON event
  payloads while retaining envelope and Kafka metadata.
- `int_transaction_metrics` selects one terminal event per transaction and
  excludes pending withdrawal requests and duplicate account-close lifecycle
  notifications.
- `analytics_daily_transactions` reports daily counts, exact monetary totals,
  and success/decline rates by currency and transaction type.
- `analytics_authentication_metrics` reports authentication outcomes, including
  unknown-card failures.
- `analytics_account_activity` combines daily transaction and authentication
  activity for known accounts.

## Run in the `bankflow` container

The checked-in profile reads credentials from environment variables. Set
`BANKFLOW_DBT_DATABASE`, `BANKFLOW_DBT_USER`, and `BANKFLOW_DBT_PASSWORD`; the
container-local host and port default to `localhost:5432`.

```bash
dbt build \
  --project-dir /home/datalab/bankflow/dbt \
  --profiles-dir /home/datalab/bankflow/dbt \
  --full-refresh

dbt docs generate \
  --project-dir /home/datalab/bankflow/dbt \
  --profiles-dir /home/datalab/bankflow/dbt
```

The generated catalog and documentation site are written to `dbt/target/`.
That directory is intentionally ignored because it is reproducible build
output.
