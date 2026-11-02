# ADR-016: Iceberg Bronze layer

Date: 2026-11-02. Status: accepted for the local Version 2 platform.

## Context

Day 16 established validated Kafka-to-Spark ingestion with durable HDFS checkpoints. Day 17 needs an immutable lakehouse landing table that preserves the source value and transport provenance, supports restart recovery and replay, and uses the services already running in the dedicated container.

## Decisions

- Use the existing Iceberg Spark runtime, Hive Metastore at `thrift://localhost:9083`, and HDFS warehouse at `hdfs://localhost:9000/bankflow/lakehouse`.
- Create catalog `bankflow`, namespace `bronze` at `/bankflow/bronze`, and Iceberg v2 table `bankflow.bronze.bronze_bankflow_events` with Zstandard Parquet compression.
- Preserve the exact valid Kafka JSON as `raw_payload`, a SHA-256 fingerprint, parsed envelope identity/type/version/time/source, payload kind, Kafka topic/partition/offset/key/timestamp, and `ingested_at`.
- Partition by ingestion day. Do not derive business dimensions or mutate payload content in Bronze; Silver owns normalization.
- Reuse Day 16 validation. Invalid values do not enter Bronze and retain only safe transport metadata, reason, and fingerprint in quarantine.
- Checkpoint the stream in HDFS. Within each micro-batch, use an Iceberg `MERGE` keyed by Kafka topic, partition, and offset so checkpoint recovery and intentional full replays cannot duplicate a source position.
- Validate an existing table's exact schema at startup and fail instead of silently changing it.

## Consequences

The table is queryable through Spark and other engines sharing the Hive Metastore. Valid raw source values remain replayable for downstream Silver transformations, while malformed or contract-invalid values remain secret-safe. The local single-node Hive/HDFS services are runtime dependencies. Kafka-coordinate idempotence assumes a topic's retained records are not rewritten at the same partition and offset. Schema evolution must be an explicit later decision.

Runbook: [`spark/bronze/README.md`](../../spark/bronze/README.md). Evidence: [`docs/DAY17_VALIDATION.md`](../DAY17_VALIDATION.md).

