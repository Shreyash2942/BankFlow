# Day 20 Validation — Gold Analytics Layer

**Validated:** 2026-11-03  
**Environment:** Dedicated `bankflow` container, Spark 3.5.1, Iceberg, Hive Metastore, HDFS, Trino  
**Result:** Complete

## Delivered behavior

- Creates the `bankflow.gold` namespace and all five planned Iceberg v2 business tables.
- Builds daily and hourly transaction, account activity, authentication, and decline metrics only from typed Silver sources.
- Separates operational lifecycle event volume from terminal monetary attempts so requests and inquiries do not inflate rates.
- Calculates exact deposit, withdrawal, decline, average transaction, success-rate, and decline-rate measures.
- Upserts complete-state aggregates by deterministic business grain and remains row-count stable on rerun.
- Fails before merge on null/empty grains, negative values, reconciliation failures, invalid rates, closure mismatches, or invalid time ranges.
- Emits structured source, output, rule-violation, and target counts.

## Automated checks

```text
Day 20 focused tests: 37 passed
Ruff check: passed
Ruff format: 113 files already formatted
Service-free suite: 226 passed, 29 skipped
Service opt-in suite: 255 passed in 13.18s
```

Coverage includes lazy PySpark imports, canonical source/target defaults, the HDFS namespace, exact decimal/rate contracts, Iceberg v2 DDL and partitions, update-or-insert merge keys, terminal-event semantics, authentication lockout semantics, decline filtering, quality-rule coverage, isolated CLI targets, unsafe runtime boundaries, and source/target collision rejection.

## Live canonical runs

Each job was submitted through `spark://localhost:7077` in the dedicated container. All quality rules returned zero violations.

```json
{"event":"bankflow_gold_daily_quality","source_transaction_rows":19,"source_authentication_rows":6,"output_rows":{"daily":1,"authentication":1,"declines":1},"target_rows":{"daily":1,"authentication":1,"declines":1}}
{"event":"bankflow_gold_hourly_quality","source_rows":19,"output_rows":5,"target_rows":5}
{"event":"bankflow_gold_account_quality","source_transaction_rows":19,"source_account_rows":0,"output_rows":7,"target_rows":7}
```

The empty account lifecycle source is expected for the canonical generator sample; transaction facts still produce seven account-day groups.

## Business result validation

Trino read all five Gold tables through the shared Hive Metastore. The canonical daily row was:

```text
metric_date  currency  events  attempts  success  declined  deposits  withdrawals  avg_value  success_rate  decline_rate
2026-01-01   USD       19      12        10       2         445.00    660.00       110.50     0.833333      0.166667
```

The authentication row was:

```text
metric_date  events  attempts  success  failed  lockouts  sessions  success_rate  failure_rate
2026-01-01   6       5         2        2       1         1         0.400000      0.600000
```

Source-to-Gold reconciliation returned:

```text
Silver transaction rows = summed Gold daily event rows = 19
Silver authentication rows = summed Gold authentication event rows = 6
Silver declined rows = summed Gold decline rows = 2
```

Running all three drivers again retained exactly 1 daily, 1 authentication, 1 decline, 5 hourly, and 7 account rows, confirming stable aggregate upserts.
