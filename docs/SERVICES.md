# BankFlow service endpoint reference

Recorded from the user-provided connection guide and updated through 2026-10-09. Target container: `bankflow`. Credentials and token-bearing URLs are not stored in this document.

## Service endpoints

| Service | Windows host | Inside bankflow | Status |
|---|---|---|---|
| PostgreSQL | `localhost:5433` | `localhost:5432` | Application health query verified on 2026-09-24 |
| Redis | `localhost:6380` | `localhost:6379` | Authenticated application and isolated test access verified |
| Kafka bootstrap | `localhost:9093` | `localhost:9092` | Kafka 3.7.1 producer, Python consumer, and Spark Structured Streaming consumption verified |
| HiveServer2 JDBC | `jdbc:hive2://localhost:10002` | `localhost:10000` | Mapping inspected, query untested |
| HiveServer2 Thrift | `thrift://localhost:10002` | `localhost:10000` | Mapping inspected, request untested |
| Hive Metastore | `thrift://localhost:9084` | `localhost:9083` | Day 17 Iceberg catalog namespace/table creation and reads verified |
| MongoDB | `localhost:27018` | `localhost:27017` | Mapping inspected; outside BankFlow scope |
| HDFS filesystem | Port 9000 not published | `hdfs://localhost:9000` | Day 17 Iceberg data/metadata, checkpoint, and quarantine writes verified under `/bankflow` |
| Spark RPC | Port 7077 not published | `spark://localhost:7077` | Spark 3.5.1 standalone submission and Kafka streaming verified |

Kafka clients use `host:port` without the helper's `kafka://` display prefix. The dedicated broker advertises `host.docker.internal:9093`, which is reachable from both Windows and container-side clients through Docker Desktop. The primary topic is `bankflow.transaction.events`; its local development configuration has one partition and replication factor one.

The operational consumer uses group `bankflow-operational-v1`. Run `python consumers/transaction_consumer.py` from the repository root after `alembic upgrade head`; SIGINT/SIGTERM stops it after the current bounded poll.

The Spark consumer runs inside the container as `datalab` and resolves `spark-sql-kafka-0-10_2.12:3.5.1` at submission. See `streaming/README.md` for the exact command, HDFS checkpoint paths, metrics, and replay rules.

The Day 17 Bronze writer reuses the installed Iceberg Spark runtime, connects to the internal Hive Metastore, and stores `bankflow.bronze.bronze_bankflow_events` beneath `/bankflow/bronze`. See `spark/bronze/README.md` for startup, query, checkpoint, and replay guidance.

The Day 18–19 Silver batch jobs use the same catalog and store typed transactions, authentication facts, account events, and pointer-only rejects beneath `/bankflow/silver`. They require Spark, Hive Metastore, HDFS, and the installed Iceberg runtime but no live Kafka connection. See `spark/silver/README.md`.

The reported PostgreSQL lab database/user are `datalab` / `admin`, distinct from the provisioned application resources `bankflow` / `bankflow_user` and isolated test resources `bankflow_test` / `bankflow_test_user`. Redis uses the reported ACL user `default`. Do not assume UI login passwords authenticate database services.

## HTTP interfaces

All entries use `http://localhost` on Windows. These are inspected mappings, not verified login or health results.

| Service | Host port / path | Type |
|---|---|---|
| Airflow | `8081/` | Web UI |
| Spark Master | `9091/` | Web UI |
| Spark History | `18081/` | Web UI |
| Spark application | `4041/` | UI only while an app exposes it |
| HDFS NameNode | `9871/` | Web UI, not filesystem RPC |
| YARN ResourceManager | `8089/` | Web UI |
| Kafka UI | `9003/` | Web UI |
| Schema Registry | `8093/apis/registry/v3` | HTTP API |
| Kafka Connect | `8094/connectors` | HTTP API |
| JupyterLab | `8889/lab` | Web UI; token omitted |
| Great Expectations | `8892/` | Generated Data Docs |
| Marquez | `5001/api/v1/namespaces` | HTTP API |
| Marquez | `3002/` | Web UI |
| Prometheus | `9096/` | Web UI |
| Grafana | `3003/` | Web UI; dashboard UID bankflow-overview |
| Mongo Express | `8087/` | Web UI |
| Redis Commander | `8092/` | Web UI |
| pgAdmin | `8182/` | Web UI |
| Trino | `8096/` | Gold queries and Day 21 serving export verified |
| Superset | `8095/` | Web UI |
| MinIO | `9006/` | Object storage API |
| MinIO Console | `9007/` | Web UI |

Trino JDBC: `jdbc:trino://localhost:8096/hive/default`, user `trino`, catalog/schema `hive.default`. Day 20 verified reads from `hive.gold`; Day 21 uses the bounded HTTP statement API at `http://localhost:8096/v1/statement` to mirror selected Gold tables into PostgreSQL. Hive defaults remain authentication NONE, user `datalab`, database `default`.

## Storage and runtime boundaries

- Runtime volume: `datalab-runtime-bankflow` at `/home/datalab/runtime`. No other container currently mounts it; copied contents are not assumed empty.
- Repository mount: `/home/datalab/bankflow`. Edits there change the host repository.
- Reported Hive config: `/opt/hive/conf/hive-site.xml`.
- Reported Hive warehouse: `hdfs://localhost:9000/hive/warehouse`, from inside the container.
- The copied helper lists `/medilake/bronze` and `/medilake/silver`; BankFlow does not adopt or modify them. Days 17–18 created separate `/bankflow/bronze` and `/bankflow/silver` namespaces.
- Use in-container jobs for later HDFS/Spark work unless host RPC connectivity is deliberately configured and validated.

Recheck with `docker port bankflow` after recreation. A published port, browser UI, or TCP connection alone does not prove backend readiness.
