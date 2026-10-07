# Day 9 Kafka Producer Validation

Validated on 2026-10-06 from Windows Python 3.14 against the dedicated `bankflow` container.

## Delivered behavior

- `KafkaEventProducer` uses the canonical Day 8 serializer, all acknowledgements, idempotence, gzip compression, bounded delivery waits, callbacks, and delivery receipts.
- The producer attaches only event type, schema version, and source headers. Transaction UUIDs and known card UUIDs provide aggregate partition keys.
- `BankFlowRuntime` publishes authentication success/failure, card lock, balance view, withdrawal request/completion/decline, deposit completion, account closure, and session end.
- Database-backed events are constructed and published only after the caller-owned SQLAlchemy transaction commits.
- Kafka queue, timeout, and callback failures use stable transport exceptions. Runtime handling logs the failure and preserves the committed banking result.

## Broker evidence

The first Windows metadata request exposed an invalid broker advertisement: bootstrap used `127.0.0.1:9093`, while broker metadata redirected the client to `127.0.0.1:9092`. The dedicated copied container now advertises `host.docker.internal:9093`; its original runtime properties file is retained as a backup.

Verified state:

```text
Kafka version:       3.7.1
Broker ID:           1
Advertised endpoint: host.docker.internal:9093
Topic:               bankflow.transaction.events
Partitions:          1
Replication factor:  1
In-sync replicas:    1
Kafka heap:          -Xms384M -Xmx384M
```

The live test received a broker acknowledgement, consumed the same event through a unique consumer group, validated it through `BankFlowEvent`, and preserved exact decimal money.

## Automated checks

```powershell
# Service-free suite
.\.venv\Scripts\python.exe -m pytest -q
# 74 passed, 26 skipped

# Complete PostgreSQL, Redis, Streamlit, and Kafka suite
$env:BANKFLOW_RUN_DB_TESTS='1'
$env:BANKFLOW_RUN_KAFKA_TESTS='1'
.\.venv\Scripts\python.exe -m pytest -q
# 100 passed
```

Producer tests cover configuration, JSON serialization, aggregate keys, safe headers, callback receipts, callback errors, queue exhaustion, acknowledgement timeout, and constructor validation. Live runtime tests prove transaction rows are visible from a separate database session during publication and prove a simulated broker outage does not reverse a committed withdrawal.

Ruff, format checks, dependency checks, and Alembic current/check pass. The incremental Graphify refresh covers 131 source files and produces 1,000 nodes, 1,646 edges, and 63 communities. Relative to the prior graph it adds 153 nodes and 280 edges, removes 40 stale nodes and 66 stale edges, and reduces the estimated per-query context by 112.8x.

## Reliability boundary

PostgreSQL remains the system of record. Direct post-commit publication has a crash gap between commit and broker acknowledgement. No outbox or automatic replay is claimed in Day 9; ADR-010 records that deliberate V1 limitation.
