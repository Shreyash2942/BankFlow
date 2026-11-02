# Day 19 Validation — Silver Authentication and Account Events

**Validated:** 2026-11-02  
**Environment:** Dedicated `bankflow` container, Spark 3.5.1, Iceberg, Hive Metastore, HDFS  
**Result:** Complete

## Delivered behavior

- Creates `silver_authentication_events` and `silver_account_events` plus independent pointer-only reject tables.
- Normalizes authentication and account event names while retaining their canonical source names.
- Enforces complete-or-absent authentication subjects and validates account/customer/card UUIDs.
- Classifies valid `card.locked` events as lockouts caused by the PIN attempt limit.
- Validates authentication outcomes/remaining attempts and zero-balance account-closure arithmetic.
- Deduplicates event IDs, favors valid earliest positions, and uses idempotent Iceberg merges.
- Emits structured source, valid, reject, duplicate, lockout, inserted, and target counts.

## Focused contracts

```text
Day 19 focused tests: 30 passed
Ruff check: passed
Ruff format: 107 files already formatted
Service-free suite: 189 passed, 29 skipped
Service opt-in suite: 218 passed in 10.25s
```

Coverage includes lazy PySpark imports, table/config defaults, event-name normalization, lockout fields, account-closure classification, raw schemas, Iceberg v2 DDL, pointer-only rejects, valid/reject merge keys, isolated CLI targets, and unsafe runtime boundaries.

## Canonical authentication validation

The canonical 25-row Bronze sample contains six authentication events. The first run produced:

```json
{"source_rows":6,"valid_rows":6,"rejected_rows":0,"duplicates_removed":0,"lockout_rows":1,"rows_inserted":6,"target_rows":6}
```

A second run inserted zero rows and retained six unique event IDs. Table reconciliation returned:

```text
authentication_failure  failure  card_unavailable     1
authentication_failure  failure  invalid_credentials  1
authentication_success  success  authenticated        2
card_lockout             lockout  card_locked          1
session_end              session  session_ended        1
```

The lockout row had `is_lockout=true` and `lockout_classification=pin_attempt_limit`. All six event timestamps were non-null.

## Canonical account validation

The canonical Day 15 generator deliberately covers every event type except `account.closed`, so the canonical account job completed successfully with zero source, valid, rejected, inserted, and target rows. This is the expected empty-input contract.

## Isolated quality validation

An isolated Bronze fixture supplied a valid lockout, a repeated Kafka copy of that event, an invalid lockout with a malformed account ID, a valid zero-balance account closure, and an invalid closure with a malformed account ID.

Authentication result:

```json
{"source_rows":3,"valid_rows":1,"rejected_rows":2,"duplicates_removed":1,"lockout_rows":1,"rows_inserted":1,"target_rows":1,"rejection_reasons":{"duplicate_event_id":1,"invalid_subject_identifier":1}}
```

Account result:

```json
{"source_rows":2,"valid_rows":1,"rejected_rows":1,"duplicates_removed":0,"rows_inserted":1,"target_rows":1,"rejection_reasons":{"invalid_account_identifier":1}}
```

The accepted account row was `account_closed`, classified as `zero_balance_withdrawal`, with closed status, amount `100.00`, and ending balance `0.00`. The validation namespaces and their HDFS data were removed through Iceberg after evidence was collected; canonical Silver tables remain.

