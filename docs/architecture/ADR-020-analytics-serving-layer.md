# ADR-020: Analytics serving layer

Date: 2026-11-08. Status: accepted for the local Version 2 platform.

## Context

Iceberg Gold is the analytical source of truth, but the Streamlit application and dbt already use PostgreSQL. Day 21 needs a deterministic serving boundary without allowing the Version 1 event-store marts and Version 2 lakehouse metrics to overwrite or double-count one another.

## Decisions

- Own four selected Gold mirrors in a separate `bankflow_serving` PostgreSQL schema: daily transactions, authentication metrics, account activity, and hourly volume.
- Preserve the Gold business grains as PostgreSQL primary keys and retain exact numeric precision, UTC timestamps, `source_gold_processed_at`, and `loaded_at`.
- Read Gold through Trino's statement API with bounded requests and no new runtime dependency. Never place credentials in the endpoint or error output.
- Treat each execution as a transactional full-state mirror. Acquire one advisory transaction lock, load temporary staging tables, update or insert every current key, delete target keys absent from Gold, and reconcile row counts plus selected exact totals before commit.
- Keep Version 1 marts unchanged. Define `bankflow_serving` as a second dbt source and materialize four `analytics_lakehouse_*` marts with unique keys, source tests, reconciliation tests, and rate/count invariants.
- Make the Streamlit analytics module read the V2 marts. Report terminal monetary attempts separately from transaction lifecycle events and expose average value, active accounts, peak hourly volume, hourly trends, serving freshness, and the Gold-to-serving-to-dbt lineage.

## Consequences

Reruns are idempotent and late Gold changes refresh existing PostgreSQL rows. Stale serving keys cannot survive a successful full-state load. The application remains independent of Trino and Iceberg availability after serving and dbt complete. Full-state loads are appropriate for the current portfolio scale; partitioned incremental synchronization can replace them later without changing the serving grains.

Implementation: [`scripts/load_gold_serving.py`](../../scripts/load_gold_serving.py). Evidence: [`docs/DAY21_VALIDATION.md`](../DAY21_VALIDATION.md).
