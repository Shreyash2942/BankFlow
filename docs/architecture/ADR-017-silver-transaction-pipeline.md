# ADR-017: Silver transaction pipeline

Date: 2026-11-02. Status: accepted for the local Version 2 platform.

## Context

Iceberg Bronze preserves validated raw version-1 events and Kafka provenance. Analytics should not repeatedly parse JSON or infer financial types, and downstream jobs need a stable transaction dataset with explicit quality boundaries. Silver must remain reproducible from Bronze without mutating its immutable source.

## Decisions

- Implement Day 18 as a rerunnable Spark batch transformation from `bankflow.bronze.bronze_bankflow_events` to `bankflow.silver.silver_transactions`.
- Include balance, withdrawal lifecycle, decline, and deposit events. Leave authentication events and `account.closed` to Day 19 so account lifecycle facts are not double-counted as financial transaction outcomes.
- Parse the exact Bronze raw payload, cross-check it against Bronze envelope metadata, normalize controlled strings/UUIDs, standardize timestamps in UTC, and cast money to `DECIMAL(18,2)` only after strict cent-precision text validation.
- Validate required fields, identifiers, event shape, controlled domains, and financial balance arithmetic.
- Prefer the earliest valid row for an event ID. Classify additional copies as `duplicate_event_id` and merge valid output by event ID.
- Write invalid/duplicate source pointers to `silver_transaction_rejects`, merging by Kafka position. Do not duplicate the raw JSON into the reject table; retain only safe identifiers, reason, coordinates, fingerprint, and timestamps.
- Emit structured per-run quality metrics. Persistent quality history remains a later observability task.
- Store both tables as Iceberg v2 under the HDFS `silver` namespace, partitioned by business/ingestion day respectively.

## Consequences

Downstream Gold jobs receive exact typed money, normalized dimensions, UTC event time, and source lineage without re-reading JSON. Reruns insert neither duplicate valid rows nor duplicate rejects. The pipeline is a full current-state Bronze scan; incremental snapshot processing can be introduced when scale justifies additional state. Reject investigation follows the stored Kafka position and Bronze fingerprint back to the immutable source.

Runbook: [`spark/silver/README.md`](../../spark/silver/README.md). Evidence: [`docs/DAY18_VALIDATION.md`](../DAY18_VALIDATION.md).

