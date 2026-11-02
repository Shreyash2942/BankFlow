# Day 17 Validation — Iceberg Bronze Layer

**Validated:** 2026-11-02  
**Environment:** Dedicated `bankflow` container, Spark 3.5.1, Kafka 3.7.1, Iceberg, Hive Metastore, HDFS  
**Result:** Complete

## Delivered behavior

- Configures a Hive-backed Iceberg Spark catalog and shared HDFS warehouse.
- Creates the `bronze` namespace and `bankflow.bronze.bronze_bankflow_events` Iceberg v2 table.
- Persists exact valid raw JSON with its hash, envelope fields, payload kind, Kafka provenance, and ingestion timestamp.
- Partitions Bronze by ingestion day and uses Zstandard Parquet compression.
- Uses HDFS streaming checkpoints and a Kafka-position `MERGE` for restart and replay idempotence.
- Reuses the Day 16 schema validation and stores only safe metadata for rejected values.
- Supports create-only, continuous, and available-now execution.

## Automated checks

```text
Focused Day 17 tests: 19 passed
Ruff check: passed
Ruff format: 34 Spark/test files already formatted
Service-free suite: 136 passed, 29 skipped
Service opt-in suite: 165 passed in 9.50s
```

An earlier run had one existing Streamlit startup timeout while the container was under Spark/HDFS load. The isolated scenario passed in 1.66 seconds, and the complete rerun then passed all 165 tests.

## Live container validation

The create-only command successfully connected to the metastore and HDFS and created:

```text
Catalog: bankflow
Namespace: bronze
Table: bankflow.bronze.bronze_bankflow_events
Location: hdfs://localhost:9000/bankflow/bronze
```

Validation used isolated topic `bankflow.day17.validation.20261102`. The first available-now run read 20 schema-valid generated events and one malformed value:

```json
{"batch_id":0,"input_rows":21,"invalid_reasons":{"malformed_json":1},"invalid_rows":1,"valid_rows_merged":20}
```

The table read returned 20 rows, 20 unique Kafka positions, 20 exact raw-payload matches, 20 matching SHA-256 fingerprints, and non-null ingestion timestamps. HDFS contained Iceberg metadata and Parquet data under an `ingested_at_day=2026-11-02` partition.

Five more valid events were published and the same checkpoint restarted. HDFS checkpoint commits advanced from `0` to `1`, and the table reached exactly 25 rows and 25 unique positions, proving resume from committed offsets.

A separate checkpoint then replayed the complete topic from earliest. Spark attempted 25 valid records plus the malformed record, while the Iceberg `MERGE` left the table at exactly 25 rows and 25 unique Kafka positions. This validates duplicate protection independently of checkpoint recovery.

The malformed value was absent from Bronze. Quarantine retained only its Kafka metadata, validation reason, and value fingerprint.

## Operational boundaries

- Run the driver as container user `datalab`.
- The installed Iceberg runtime is reused; the Kafka connector remains a submission-time package.
- Use a stable checkpoint for normal restarts and a new checkpoint only for deliberate replay.
- Bronze preserves valid raw payloads. Invalid raw values are intentionally excluded by the Day 16 privacy policy.

