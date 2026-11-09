# Day 21 Validation — Analytics Serving Layer

**Validated:** 2026-11-08  
**Environment:** Dedicated `bankflow` container, Trino, PostgreSQL 14.22, dbt 1.8.7, Streamlit application  
**Result:** Complete

## Delivered behavior

- Creates the separate `bankflow_serving` schema and four typed serving tables through Alembic revision `0004`.
- Exports Gold daily transaction, authentication, account activity, and hourly volume datasets through Trino.
- Mirrors complete source state with a PostgreSQL advisory lock, temporary stages, deterministic upserts, stale-key removal, and one atomic transaction.
- Stores both `source_gold_processed_at` and PostgreSQL `loaded_at` timestamps.
- Reconciles row counts and exact count/money totals before commit and emits structured secret-free results.
- Defines all four serving tables as dbt sources and materializes four `analytics_lakehouse_*` marts.
- Reconciles every mart to its serving source and validates outcome counts, controlled values, unique keys, non-null fields, and rates.
- Serves the V2 marts through Streamlit with lifecycle event, monetary attempt, average value, active account, peak hourly, hourly trend, freshness, and lineage metrics.

## Automated checks

```text
Day 21 focused tests: 16 passed (15 service-free, 1 live PostgreSQL)
Ruff check: passed
Ruff format: 118 files already formatted
Service-free suite: 238 passed, 30 skipped
Service-opt-in suite: 268 passed in 15.07s
dbt build: PASS=146 WARN=0 ERROR=0 SKIP=0 TOTAL=146
```

The migration test upgrades to `0004`, verifies both application and serving schemas, downgrades to base, confirms both schemas are removed, and re-upgrades. The live mirror test proves exact totals, load timestamps, rerun stability, and stale-key pruning.

## Live migration and serving load

The application database advanced from `0003` to `0004 (head)`. The canonical first load returned:

```json
{
  "daily_transactions": {"source_rows": 1, "target_rows": 1, "deleted_rows": 0},
  "authentication_metrics": {"source_rows": 1, "target_rows": 1, "deleted_rows": 0},
  "account_activity": {"source_rows": 7, "target_rows": 7, "deleted_rows": 0},
  "hourly_volume": {"source_rows": 5, "target_rows": 5, "deleted_rows": 0}
}
```

A second complete load retained the same 1/1/7/5 row counts with zero stale deletions. Every dataset passed the loader's source-to-target count and exact-total signature before commit.

## dbt and dashboard reconciliation

The full dbt build discovered ten models, five sources, and 136 data tests. All 146 nodes passed. The four V2 marts materialized 1 daily, 1 authentication, 7 account, and 5 hourly rows, matching their serving sources.

The production application query returned:

```text
transaction lifecycle events: 19
terminal monetary attempts: 12
successful transactions: 10
declined transactions: 2
completed transaction volume: 1105.00
average successful transaction value: 110.50
active accounts: 7
peak hourly events: 19
hourly chart points: 1
serving timestamp present: true
```

These values match the Day 20 Gold evidence. The dashboard date boundary is applied consistently to daily, authentication, account, and hourly marts, and unavailable marts produce a safe actionable message without exposing database details.
