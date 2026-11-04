# ADR-019: Gold analytics layer

Date: 2026-11-03. Status: accepted for the local Version 2 platform.

## Context

Days 18–19 provide typed transaction, authentication, and account lifecycle facts. Business users need stable daily, hourly, account, authentication, and decline datasets without reinterpreting raw JSON or double counting transaction lifecycle events.

## Decisions

- Build five Iceberg v2 Gold tables in `bankflow.gold`, stored under `hdfs://localhost:9000/bankflow/gold`, using only validated Silver sources.
- Treat completed deposits and withdrawals as successful monetary transactions and declined transactions as failed monetary attempts. Exclude withdrawal requests and balance inquiries from attempt, success, decline, rate, and average-value calculations.
- Preserve all transaction event states in the hourly volume grain so operational lifecycle volume remains observable.
- Define authentication attempts as success, ordinary failure, or card lockout. Keep session ends visible but outside the denominator; include lockouts in the authentication failure rate.
- Build account-day metrics from transaction facts plus account lifecycle facts. Count `account.closed` as activity but not as a second monetary outcome.
- Use exact `DECIMAL(38,2)` aggregate money, `DECIMAL(18,2)` balances, UTC timestamps, and six-place decimal rates.
- Recompute aggregates from complete current Silver state and upsert by deterministic business grain. Matched rows update and new rows insert, allowing later facts to refresh prior groups without duplicate Gold rows.
- Fail before merge when grain, nonnegative value, event/attempt reconciliation, rate, account closure, or time-range invariants are violated. Emit structured per-run quality metrics.

## Consequences

Gold metrics reconcile directly to Silver and can be queried through Spark or Trino. Lifecycle events remain available for operations while business success and decline rates use terminal facts only. Full-state aggregation is simple and deterministic for the current portfolio scale; incremental watermarking and late-data windows remain future scale optimizations.

Runbook: [`spark/gold/README.md`](../../spark/gold/README.md). Evidence: [`docs/DAY20_VALIDATION.md`](../DAY20_VALIDATION.md).
