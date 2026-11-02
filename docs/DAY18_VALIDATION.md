# Day 18 Validation — Silver Transaction Pipeline

**Validated:** 2026-11-02  
**Environment:** Dedicated `bankflow` container, Spark 3.5.1, Iceberg, Hive Metastore, HDFS  
**Result:** Complete

## Delivered behavior

- Creates the HDFS-backed `bankflow.silver` namespace.
- Reads immutable Day 17 Bronze events and selects the five Day 18 transaction event types.
- Cross-validates raw JSON with Bronze metadata and enforces required fields, identifiers, controlled domains, event shapes, exact numeric text, and balance arithmetic.
- Standardizes UUIDs/controlled values, UTC timestamps, and `DECIMAL(18,2)` money.
- Deduplicates by event ID, favoring a valid earliest Kafka position.
- Writes typed rows to `silver_transactions` and pointer-only rejection records to `silver_transaction_rejects`.
- Merges both outputs idempotently and emits structured run-quality metrics.

`account.closed` is intentionally reserved for Day 19's account-event dataset; authentication payloads are also outside this table.

## Automated checks

```text
Focused Day 18 contracts: 23 passed
Ruff check: passed
Ruff format: 103 files already formatted
Service-free suite: 159 passed, 29 skipped
Service opt-in suite: 188 passed in 8.37s
```

The focused suite verifies lazy PySpark imports, catalog/source/target defaults, event ownership, string-before-decimal parsing, normalized and reject schemas, Iceberg v2 DDL, valid/reject merge keys, CLI isolation, and unsafe configuration rejection.

## Canonical live transformation

The create-only run connected to Hive Metastore, created the Silver namespace and both Iceberg v2 tables, and validated their exact schemas. Processing the 25-row Day 17 Bronze table selected 19 transaction events:

```json
{"source_transaction_rows":19,"valid_rows":19,"rejected_rows":0,"duplicates_removed":0,"rows_inserted":19,"target_rows":19}
```

A second identical run reported `rows_inserted: 0` and retained 19 target rows. The table read confirmed:

```text
rows:                19
distinct event IDs:  19
null numeric fields: 0
null event times:    0
```

Event-shape reconciliation returned:

```text
balance.viewed        balance_inquiry completed  4
deposit.completed     deposit         completed  5
withdrawal.completed  withdrawal      completed  5
withdrawal.declined   withdrawal      declined   2
withdrawal.requested  withdrawal      pending    3
```

## Invalid and duplicate validation

An isolated Iceberg Bronze fixture contained one valid deposit, a second Kafka position carrying the same event ID, and one row whose Bronze event type disagreed with its raw payload. The pipeline reported:

```json
{"source_transaction_rows":3,"valid_rows":1,"rejected_rows":2,"duplicates_removed":1,"rows_inserted":1,"target_rows":1,"rejection_reasons":{"bronze_metadata_mismatch":1,"duplicate_event_id":1}}
```

The reject-table query returned exactly one record for each reason and no raw-payload column. The isolated validation namespaces and their HDFS data were removed through the Iceberg catalog after evidence was collected; the canonical Silver tables remain.

