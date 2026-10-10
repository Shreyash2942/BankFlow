# Day 10 Kafka Consumer and Event Store Validation

Validated on 2026-10-09 from Windows Python 3.14 against PostgreSQL and Kafka 3.7.1 in the dedicated `bankflow` container.

## Delivered behavior

- `KafkaEventConsumer` joins `bankflow-operational-v1` with manual offsets and `read_committed` isolation.
- Every message is deserialized through the closed version-1 `BankFlowEvent` schema before storage.
- Migration `0003` adds append-only `bankflow.consumed_events` records with exact JSON payloads and Kafka metadata.
- Primary-key `event_id` and unique topic/partition/offset constraints provide atomic duplicate protection.
- PostgreSQL commits before Kafka offsets. Database failure leaves the offset available for retry; offset failure after persistence replays safely as a duplicate.
- Invalid messages are logged with structured Kafka positions but without payload values, then committed so one poison message cannot block its partition.
- SIGINT/SIGTERM set a shutdown flag, the bounded poll returns, and the consumer closes in `finally`.

Run the operational consumer after applying migrations:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe consumers\transaction_consumer.py
```

## Automated checks

```powershell
# Service-free suite
.\.venv\Scripts\python.exe -m pytest -q
# 83 passed, 29 skipped

# Complete PostgreSQL, Redis, Streamlit, producer, and consumer suite
$env:BANKFLOW_RUN_DB_TESTS='1'
$env:BANKFLOW_RUN_KAFKA_TESTS='1'
.\.venv\Scripts\python.exe -m pytest -q
# 112 passed
```

Unit coverage verifies configuration, subscription, schema rejection, secret-free structured logging, manual commit ordering, persistence failure, broker failures, duplicates, and graceful shutdown. PostgreSQL tests verify exact payload storage plus both uniqueness guards. The live test creates an isolated Kafka topic, persists an acknowledged event, detects a replay, commits an invalid message, and verifies the stored row.

Alembic reports `0003 (head)` for application and test databases, and autogeneration reports no pending operations.

The incremental Graphify refresh covers 140 source files and produces 1,082 nodes, 1,817 edges, and 69 communities. Relative to Day 9 it adds 132 nodes and 269 edges, removes 50 stale nodes and 98 stale edges, and reduces the estimated per-query context by 96.1x.

## Reliability boundary

The consumer event store is idempotent, but it cannot recover an application event that was never published during ADR-010's commit-to-publish gap. No dead-letter topic or raw invalid-payload archive is claimed in Day 10.
