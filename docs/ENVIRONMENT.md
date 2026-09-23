# Local environment and dedicated BankFlow container

Updated 2026-09-22. The user-created **bankflow** container replaces the original Day 1 choice of the shared `datalab` container. See [ADR-002](architecture/ADR-002-dedicated-container.md).

## Inspected configuration

- Application: Python 3.14.4, Windows x64, isolated repository `.venv` and pinned dependencies.
- Container: `bankflow`, image `shreyash42/data-lab:latest`, running on Docker's `bridge` network.
- Runtime volume: `datalab-runtime-bankflow` -> `/home/datalab/runtime`; no other container mounted it during inspection.
- Repository bind mount: `D:/GitHub/miniprojects/BankFlow` -> `/home/datalab/bankflow`.
- Container default Python: 3.10.12. Continue running the application on Windows; its virtual environment is not portable into Linux.

## Windows application endpoints

| Service | Host endpoint | Internal port | Latest check |
|---|---|---|---|
| PostgreSQL | `127.0.0.1:5433` | 5432 | Accepting connections; host client receives password-required response |
| Redis | `127.0.0.1:6380` | 6379 | Responds with authentication required |
| Kafka | `127.0.0.1:9093` | 9092 | Mapping confirmed; host metadata unavailable during startup |

The reported lab PostgreSQL database/user are `datalab` / `admin`. The application template names proposed dedicated resources `bankflow` / `bankflow_user`; neither was provisioned during this inspection. Redis's reported ACL user is `default`. Database passwords must be confirmed separately from UI passwords and stay in ignored local configuration.

The supplied connection guide mixes host-mapped ports with internal HDFS/Spark addresses. HDFS port 9000 and Spark RPC port 7077 were not published. Those localhost URIs describe access inside the container, not Windows. See the complete [service reference](SERVICES.md).

## Day 2 preflight

1. Recheck `docker ps` and `docker port bankflow`.
2. Confirm database credentials privately and provision dedicated BankFlow database/user resources in this container.
3. Fill the ignored `.env`; do not assume a UI password is also a database password.
4. Implement settings validation, SQLAlchemy engine/session/base, and a database health query before running migrations.
5. At their milestones, verify Redis authentication and Kafka broker-advertised endpoints from Windows. The startup metadata failure is not a diagnosis of its cause.

The user started the services. This inspection did not reset volumes, change service configuration, or create database objects. Readiness responses do not establish authenticated application access.

## Dependency boundaries

The application uses Streamlit, Pydantic/settings, SQLAlchemy, Alembic, Psycopg, Redis, and the Kafka Python client. Airflow, dbt, Spark, and Graphify remain separate runtimes. Other available lab tools do not expand the PRD.

Day 1 dependency references: [Streamlit installation](https://docs.streamlit.io/get-started/installation), [Psycopg binary installation](https://www.psycopg.org/psycopg3/docs/basic/install.html), and [Confluent Python client installation](https://github.com/confluentinc/confluent-kafka-python/blob/master/INSTALL.md).
