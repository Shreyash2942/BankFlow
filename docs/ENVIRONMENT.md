# Local environment and dedicated BankFlow container

Updated 2026-09-24. The user-created **bankflow** container replaces the original Day 1 choice of the shared `datalab` container. See [ADR-002](architecture/ADR-002-dedicated-container.md).

## Inspected configuration

- Application: Python 3.14.4, Windows x64, isolated repository `.venv` and pinned dependencies.
- Container: `bankflow`, image `shreyash42/data-lab:latest`, running on Docker's `bridge` network.
- Runtime volume: `datalab-runtime-bankflow` -> `/home/datalab/runtime`; no other container mounted it during inspection.
- Repository bind mount: `D:/GitHub/miniprojects/BankFlow` -> `/home/datalab/bankflow`.
- Container default Python: 3.10.12. Continue running the application on Windows; its virtual environment is not portable into Linux.

## Windows application endpoints

| Service | Host endpoint | Internal port | Latest check |
|---|---|---|---|
| PostgreSQL | `127.0.0.1:5433` | 5432 | Application authentication and SELECT 1 verified |
| Redis | `127.0.0.1:6380` | 6379 | Responds with authentication required |
| Kafka | `127.0.0.1:9093` | 9092 | Mapping confirmed; host metadata unavailable during startup |

The lab PostgreSQL database/user are `datalab` / `admin`; `admin` can create databases but cannot create roles. The existing `datalab` database superuser is accessible through the local Unix socket as container OS user `datalab`. Day 2 provisioned separate application resources `bankflow` / `bankflow_user` and test resources `bankflow_test` / `bankflow_test_user`, with generated credentials only in ignored local files. Both owner roles are non-superusers; PUBLIC access to these databases is revoked.

The supplied connection guide mixes host-mapped ports with internal HDFS/Spark addresses. HDFS port 9000 and Spark RPC port 7077 were not published. Those localhost URIs describe access inside the container, not Windows. See the complete [service reference](SERVICES.md).

## Day 2 database setup

The application and test databases are both at Alembic revision `0001`. The revision creates schema `bankflow`; Alembic records its version in `public`. Customer/account/card/transaction models arrive on Day 3.

On a fresh instance of this lab, run `scripts/provision_local_database.py` once from the repository root with the Windows virtual environment. It requires Docker access and the lab's local database superuser. It refuses existing environment files or database resources and checks privileges before writing credentials. A partial failure retains local credential files for deliberate recovery; do not delete or overwrite them to retry blindly.

If a local credential is exposed, start PostgreSQL and run `scripts/provision_local_database.py --rotate-passwords`. Rotation requires both expected databases, roles, and environment files; it changes passwords only and does not reset data. Retain any ignored `.env*.next` files if replacement fails after the database update.

Run `python -m bankflow.database.health`, `alembic upgrade head`, and `alembic current` using the repository virtual environment. Settings load `.env` relative to the working directory; process environment overrides it. See [README](../README.md) for exact PowerShell commands and [Day 2 validation](DAY2_VALIDATION.md) for integration-test isolation.

Redis authentication and Kafka broker-advertised endpoints still need validation at their milestones. The earlier startup metadata failure does not diagnose its cause. Day 2 created only the dedicated database resources; it did not reset volumes or reconfigure other services.

## Dependency boundaries

The application uses Streamlit, Pydantic/settings, SQLAlchemy, Alembic, Psycopg, Redis, and the Kafka Python client. Airflow, dbt, Spark, and Graphify remain separate runtimes. Other available lab tools do not expand the PRD.

Day 1 dependency references: [Streamlit installation](https://docs.streamlit.io/get-started/installation), [Psycopg binary installation](https://www.psycopg.org/psycopg3/docs/basic/install.html), and [Confluent Python client installation](https://github.com/confluentinc/confluent-kafka-python/blob/master/INSTALL.md).
