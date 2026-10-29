# BankFlow Spark Structured Streaming

Day 16 connects the released BankFlow version-1 Kafka contract to the Spark 3.5.1 standalone cluster in the dedicated `bankflow` container. The query parses an explicit schema, validates envelope/payload shape, emits structured batch metrics, stores checkpoints in HDFS, and quarantines only safe metadata for rejected records.

## Runtime boundary

Run Spark as the container's `datalab` user. The driver and worker then share the same HDFS identity and do not create root-owned runtime state.

| Setting | Default |
|---|---|
| Spark master | supplied to `spark-submit` as `spark://localhost:7077` |
| Kafka bootstrap | `localhost:9092` inside the container |
| Topic | `bankflow.transaction.events` |
| Kafka connector | `org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1` |
| Checkpoint | `hdfs://localhost:9000/bankflow/checkpoints/day16` |
| Invalid metadata | `hdfs://localhost:9000/bankflow/quarantine/day16` |
| Starting offsets | `latest` for a new checkpoint |
| Trigger | every 10 seconds |
| Maximum offsets per trigger | 10,000 |

The Kafka connector is not bundled with base Spark. `--packages` is required and must remain aligned with Spark 3.5.1 and Scala 2.12. The first run resolves the package and its dependencies from Maven Central; later runs use the `datalab` Ivy cache.

## Start the continuous stream

From Windows PowerShell at the repository root:

```powershell
docker exec --user datalab bankflow bash -lc "cd /home/datalab/bankflow && /opt/spark/bin/spark-submit --master spark://localhost:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 streaming/bankflow_stream.py --bootstrap-servers localhost:9092 --topic bankflow.transaction.events --checkpoint-location hdfs://localhost:9000/bankflow/checkpoints/day16 --invalid-record-path hdfs://localhost:9000/bankflow/quarantine/day16 --starting-offsets latest"
```

Stop the foreground query with Ctrl+C. The checkpoint retains Kafka offsets; restarting with the same query and checkpoint resumes from the next uncommitted offset.

Use `--available-now` to consume the current backlog and stop cleanly:

```powershell
docker exec --user datalab bankflow bash -lc "cd /home/datalab/bankflow && /opt/spark/bin/spark-submit --master spark://localhost:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 streaming/bankflow_stream.py --available-now"
```

`startingOffsets` applies only when a checkpoint is first created. Do not delete a production checkpoint to replay data. Use a new query name and a new checkpoint path for an intentional replay. Keep `failOnDataLoss` enabled; `--allow-data-loss` is an explicit recovery override.

## Metrics and malformed events

Each completed micro-batch prints one JSON metric record containing the batch ID, total/valid/invalid rows, event-type counts, and validation-reason counts. Spark's native streaming metrics are also enabled.

Malformed, unsupported, or structurally inconsistent records do not enter the valid count. The quarantine path stores only:

- Kafka topic, partition, offset, and timestamp
- validation reason
- SHA-256 fingerprint of the Kafka value

It never stores or logs the rejected raw value. A failure to write quarantine metadata fails the batch, so its Kafka offsets are not checkpointed as successfully handled.

Inspect runtime state inside the container:

```bash
hdfs dfs -ls -R /bankflow/checkpoints/day16
hdfs dfs -ls -R /bankflow/quarantine/day16
```

Useful host UIs while a query is active:

- Spark master: `http://localhost:9091/`
- Spark application: `http://localhost:4041/`
- Spark history: `http://localhost:18081/`
- HDFS NameNode: `http://localhost:9871/`

The Day 16 query intentionally does not write Bronze business data. Day 17 owns the Iceberg Bronze sink and its table/catalog decisions.
