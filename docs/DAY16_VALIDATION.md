# Day 16 Validation — Spark Streaming Foundation

**Validated:** 2026-10-28  
**Environment:** Dedicated `bankflow` container, Spark 3.5.1/Scala 2.12, Kafka 3.7.1, HDFS  
**Result:** Complete

## Delivered behavior

- Pins the official Spark Kafka connector matching the container runtime.
- Starts a UTC Spark Structured Streaming session on the standalone master.
- Subscribes to a configurable BankFlow topic with bounded trigger size and fail-on-data-loss behavior.
- Parses the version-1 envelope and transaction/authentication payloads with an explicit Spark schema and exact decimal types.
- Retains Kafka topic, partition, offset, key, and timestamp for replay and future Bronze ingestion.
- Classifies malformed JSON and structurally invalid envelopes/payloads without logging raw values.
- Stores durable offsets in HDFS and safe invalid-record metadata in a separate HDFS quarantine path.
- Emits structured per-batch totals, validity counts, event-type counts, and invalid-reason counts.
- Supports continuous processing and an `--available-now` validation/backlog mode.

## Service-free checks

The unit contract verifies lazy PySpark imports, complete schema fields, prohibited-field absence, all ten released event types, the Spark/Scala connector coordinate, HDFS runtime defaults, CLI construction, and invalid configuration handling.

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_bankflow_stream.py -q
```

Result: 12 passed.

The repository-wide quality gates also passed:

```text
Ruff check: passed
Ruff format: 97 files already formatted
Service-free suite: 117 passed, 29 skipped
PostgreSQL/Redis/Streamlit/Kafka opt-in suite: 146 passed in 11.22s
```

## Live Docker validation

Validation used the isolated topic `bankflow.day16.validation.20261028`, the Spark master at `spark://localhost:7077`, Kafka at `localhost:9092` inside the container, and these HDFS locations:

```text
hdfs://localhost:9000/bankflow/checkpoints/day16-validation-20261028
hdfs://localhost:9000/bankflow/quarantine/day16-validation-20261028
```

The first successful available-now batch consumed 41 records:

```json
{"batch_id":0,"input_rows":41,"valid_rows":40,"invalid_rows":1,"invalid_reasons":{"malformed_json":1}}
```

All nine event types emitted by the Day 15 generator appeared with the expected counts. The malformed record was written only as Kafka metadata, reason, and SHA-256 fingerprint.

Five more valid events were then published and the same checkpoint restarted. Batch 1 consumed exactly those five new offsets, proving checkpoint resume rather than replay:

```json
{"batch_id":1,"input_rows":5,"valid_rows":5,"invalid_rows":0}
```

After strengthening three-valued/null validation, the final batch used the same checkpoint and current code. It consumed five valid events plus two well-formed but invalid envelopes:

```json
{"batch_id":2,"input_rows":7,"valid_rows":5,"invalid_rows":2,"invalid_reasons":{"invalid_transaction_payload":1,"missing_envelope_field":1}}
```

HDFS contained commits `0`, `1`, and `2`. The quarantine contained exactly three records at Kafka offsets 40, 51, and 52, covering malformed JSON, a missing payload kind, and an invalid zero-amount deposit. Every quarantine record had only these fields:

```text
kafka_topic
kafka_partition
kafka_offset
kafka_timestamp
validation_error
value_sha256
```

The script was also launched without `--packages`; it stopped before subscription with a structured error naming the exact required connector coordinate.

## Issues found and resolved

1. Setting `spark.jars.packages` inside `SparkSession.builder` occurs too late for Kafka data-source discovery. Connector resolution was moved to the documented `spark-submit --packages` boundary and an explicit preflight was added.
2. A root driver and `datalab` executor could not safely share local `file:///` output. The command now runs as `datalab`, and both checkpoint/quarantine locations use HDFS. Failed local validation artifacts were removed after the HDFS run succeeded; they were disposable runtime state and are not recoverable.
3. Spark SQL's three-valued boolean logic could allow null required payload fields to bypass a naive negated predicate. Validity expressions now coalesce null to false, and the structural-invalid cases are included in the live proof.
