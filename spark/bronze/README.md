# BankFlow Iceberg Bronze ingestion

Day 17 persists validated version-1 Kafka events as immutable raw records in an Apache Iceberg v2 table. Spark uses the existing Hive Metastore catalog and HDFS storage in the dedicated `bankflow` container.

## Runtime contract

| Setting | Default |
|---|---|
| Iceberg catalog | `bankflow` (`SparkCatalog`, type `hive`) |
| Hive Metastore | `thrift://localhost:9083` |
| Warehouse | `hdfs://localhost:9000/bankflow/lakehouse` |
| Namespace / location | `bronze` / `hdfs://localhost:9000/bankflow/bronze` |
| Table | `bankflow.bronze.bronze_bankflow_events` |
| Checkpoint | `hdfs://localhost:9000/bankflow/checkpoints/day17-bronze` |
| Invalid metadata | `hdfs://localhost:9000/bankflow/quarantine/day17-bronze` |

The container already supplies the Iceberg Spark runtime. The Kafka connector must still be supplied to `spark-submit` and must match Spark 3.5.1/Scala 2.12.

## Create and inspect the table

From Windows PowerShell at the repository root:

```powershell
docker exec --user datalab bankflow bash -lc "cd /home/datalab/bankflow && /opt/spark/bin/spark-submit --master spark://localhost:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 spark/bronze/ingest_events.py --create-only"
```

This creates the namespace and Iceberg v2 table if absent, then verifies the complete schema. It does not replace or migrate a table whose schema differs from the Day 17 contract.

## Start continuous ingestion

```powershell
docker exec --user datalab bankflow bash -lc "cd /home/datalab/bankflow && /opt/spark/bin/spark-submit --master spark://localhost:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 spark/bronze/ingest_events.py --bootstrap-servers localhost:9092 --topic bankflow.transaction.events"
```

Use `--available-now` for a bounded backlog run. For a new checkpoint, `--starting-offsets earliest` intentionally reads retained history; the default is `latest`. Starting offsets are ignored after a checkpoint exists.

Each valid row preserves the exact Kafka JSON value in `raw_payload`, its SHA-256 fingerprint, parsed envelope fields, Kafka coordinates/key/timestamp, payload kind, and an ingestion timestamp. Rows are partitioned by the day of `ingested_at`. A `MERGE` keyed by topic, partition, and offset makes an intentional replay idempotent.

Malformed or schema-invalid values are excluded from Bronze. Their quarantine records contain only Kafka coordinates, timestamp, validation reason, and a SHA-256 fingerprint; rejected raw values are never persisted or logged.

## Read and operate the table

Use a Spark session configured with the same catalog:

```sql
SELECT event_type, count(*)
FROM bankflow.bronze.bronze_bankflow_events
GROUP BY event_type
ORDER BY event_type;

SELECT *
FROM bankflow.bronze.bronze_bankflow_events.snapshots
ORDER BY committed_at DESC;
```

Inspect HDFS state inside the container:

```bash
hdfs dfs -ls -R /bankflow/bronze
hdfs dfs -ls -R /bankflow/checkpoints/day17-bronze
hdfs dfs -ls -R /bankflow/quarantine/day17-bronze
```

Restart continuous ingestion with the same table, query name, and checkpoint. Never delete an operational checkpoint to force replay. For an intentional replay, choose a new checkpoint and quarantine path; the Iceberg merge prevents duplicate Kafka positions.

