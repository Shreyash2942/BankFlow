# BankFlow service endpoint reference

Recorded 2026-09-22 from the user-provided connection guide and Docker mapping inspection. Target container: `bankflow`. Credentials and token-bearing URLs are not stored in this document.

## Service endpoints

| Service | Windows host | Inside bankflow | Status |
|---|---|---|---|
| PostgreSQL | `localhost:5433` | `localhost:5432` | Application health query verified on 2026-09-24 |
| Redis | `localhost:6380` | `localhost:6379` | Responding; authentication required |
| Kafka bootstrap | `localhost:9093` | `localhost:9092` | Mapping inspected; metadata unavailable during startup |
| HiveServer2 JDBC | `jdbc:hive2://localhost:10002` | `localhost:10000` | Mapping inspected, query untested |
| HiveServer2 Thrift | `thrift://localhost:10002` | `localhost:10000` | Mapping inspected, request untested |
| Hive Metastore | `thrift://localhost:9084` | `localhost:9083` | Mapping inspected, request untested |
| MongoDB | `localhost:27018` | `localhost:27017` | Mapping inspected; outside BankFlow scope |
| HDFS filesystem | Port 9000 not published | `hdfs://localhost:9000` | User-reported internal URI; storage untested |
| Spark RPC | Port 7077 not published | `spark://localhost:7077` | User-reported internal URI; submission untested |

Kafka clients use `host:port` without the helper's `kafka://` display prefix. Published bootstrap ports do not guarantee that broker-advertised addresses are reachable. Validate broker metadata from the selected client runtime before implementing messaging.

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
| Trino | `8096/` | HTTP endpoint |
| Superset | `8095/` | Web UI |
| MinIO | `9006/` | Object storage API |
| MinIO Console | `9007/` | Web UI |

Trino JDBC: `jdbc:trino://localhost:8096/hive/default`, reported user `trino`, catalog/schema `hive.default`. Hive defaults are reported as authentication NONE, user `datalab`, database `default`; these have not been tested. Available tools do not automatically become BankFlow dependencies.

## Storage and runtime boundaries

- Runtime volume: `datalab-runtime-bankflow` at `/home/datalab/runtime`. No other container currently mounts it; copied contents are not assumed empty.
- Repository mount: `/home/datalab/bankflow`. Edits there change the host repository.
- Reported Hive config: `/opt/hive/conf/hive-site.xml`.
- Reported Hive warehouse: `hdfs://localhost:9000/hive/warehouse`, from inside the container.
- The copied helper lists `/medilake/bronze` and `/medilake/silver`. Proposed BankFlow paths are `/bankflow/bronze` and `/bankflow/silver`; they have not been created. Do not rename/delete copied data as part of adopting this container.
- Use in-container jobs for later HDFS/Spark work unless host RPC connectivity is deliberately configured and validated.

Recheck with `docker port bankflow` after recreation. A published port, browser UI, or TCP connection alone does not prove backend readiness.
