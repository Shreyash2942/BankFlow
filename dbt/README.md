# BankFlow dbt Analytics

This project supports two explicit analytics paths. Version 1 transforms validated
events from `bankflow.consumed_events`. Version 2 transforms the idempotent
`bankflow_serving` mirror of Iceberg Gold. Keeping source schemas separate prevents
the event-store and lakehouse paths from overwriting or double-counting each other.

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
- `analytics_lakehouse_daily_transactions` preserves Gold daily transaction
  outcomes, exact amounts, and rates.
- `analytics_lakehouse_authentication_metrics` preserves Gold attempts, failures,
  lockouts, sessions, and rates.
- `analytics_lakehouse_account_activity` exposes account-day activity, balances,
  and closure state.
- `analytics_lakehouse_hourly_volume` exposes operational event volume by hour,
  transaction type, and lifecycle status.

The lakehouse marts retain `source_gold_processed_at` and `serving_loaded_at`.
Singular tests reconcile row counts and exact totals from every serving source to
its mart, while rate tests preserve attempt and outcome invariants.

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
