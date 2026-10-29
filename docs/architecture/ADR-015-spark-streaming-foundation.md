# ADR-015: Spark Structured Streaming foundation

Date: 2026-10-28. Status: accepted for the local Version 2 platform.

## Context

BankFlow needs a distributed streaming boundary between its version-1 Kafka events and the planned Iceberg Bronze layer. The dedicated container runs Spark 3.5.1 with Scala 2.12, but its base Spark distribution does not bundle the Structured Streaming Kafka data source. The standalone driver and worker also run as different operating-system users when `docker exec` defaults to root, which makes local-file checkpoints unsafe.

## Decisions

- Run `streaming/bankflow_stream.py` through the standalone master at `spark://localhost:7077` as the container's `datalab` user.
- Supply `org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1` through `spark-submit --packages`; fail early with an actionable message when the connector is absent or mismatched.
- Subscribe to one configured topic, keep `failOnDataLoss=true`, default new checkpoints to `latest`, and bound each trigger with `maxOffsetsPerTrigger`.
- Parse values using a code-defined schema for the complete version-1 envelope and both payload variants. Preserve Kafka topic, partition, offset, key, and timestamp alongside parsed fields.
- Classify malformed JSON, missing envelope fields, unsupported schema versions, unknown event types, invalid ATM IDs, and inconsistent transaction/authentication payloads before downstream storage.
- Store checkpoints and invalid-record metadata in HDFS, not the container-local filesystem. Checkpoints use `/bankflow/checkpoints`; rejected metadata uses `/bankflow/quarantine`.
- Never persist or log a rejected raw value. Quarantine only Kafka position, timestamp, reason, and a SHA-256 value fingerprint.
- Emit one structured metric record per micro-batch and enable Spark's native streaming metrics.
- Defer Bronze/Iceberg persistence to Day 17 so the streaming source/validation boundary remains independently testable.

## Consequences

The same checkpoint resumes without reprocessing committed offsets, and both driver and executor can access its state. A new checkpoint is required for intentional replay or an incompatible query-plan change. HDFS and the Kafka connector are runtime requirements. Quarantine output inside `foreachBatch` is at-least-once if a process fails after its file write but before the batch checkpoint commits; Kafka coordinates and fingerprints allow later deduplication. The first connector run requires Maven access unless the package is already cached.

Runbook: [`streaming/README.md`](../../streaming/README.md). Evidence: [`docs/DAY16_VALIDATION.md`](../DAY16_VALIDATION.md).
