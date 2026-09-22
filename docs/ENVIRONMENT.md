# Local environment and shared Data-Lab

Inspected 2026-09-22. Day 1 chooses **BankFlow on the Windows host**, with services supplied by the existing Data-Lab. No additional service containers are required for this stage.

## Verified locally

- Python 3.14, Windows x64; application dependencies installed inside `BankFlow/.venv`.
- Docker engine 29.8.0 responds. No containers were running during inspection.
- Existing container `datalab`, image `shreyash42/data-lab:latest`, is stopped.
- Published mappings: PostgreSQL host 5432 → container 5432; Redis 6379 → 6379; Kafka 9092 → 9092.
- Other stopped containers (`fraudlens`, `medilake`, and `takeo`) belong to other projects and are not BankFlow targets.
- Existing Data-Lab source: `D:/GitHub/Data-Lab`. This is a developer-local path, not a required clone location.

These observations supersede the earlier baseline finding that Docker's engine was unavailable. Port mappings do not prove that a service is listening, authenticating, or healthy.

## Connection contract

| Service | Host application endpoint | Day 1 status |
|---|---|---|
| PostgreSQL | `127.0.0.1:5432` | Mapping inspected; connection and schema creation pending |
| Redis | `127.0.0.1:6379` | Mapping inspected; authentication and PING pending |
| Kafka | `127.0.0.1:9092` | Mapping inspected; broker metadata and advertised listeners pending |

`POSTGRES_DB=bankflow` and `POSTGRES_USER=bankflow_user` name proposed dedicated resources. They have not been provisioned. Never assume that a blank example password is a working credential. Redis credentials also belong in local configuration, with the actual authentication mode confirmed from the lab.

When running inside the lab container, localhost refers to its internal services. A future separate BankFlow container will need a verified shared Docker network and reachable service addresses; `127.0.0.1` inside that new container will refer to itself. The earlier planning examples using separate `postgres`, `redis`, and `kafka` hostnames are illustrative, not this lab's verified topology.

## Day 2 preflight

1. Recheck `docker ps -a` and `docker port datalab`; mappings can change.
2. Start the intended existing lab container/services following its own documentation. Starting the container alone may not start PostgreSQL, Redis, or Kafka.
3. Confirm credentials privately, create a dedicated BankFlow database/user without altering other projects, and fill the ignored `.env`.
4. Implement settings validation, then verify database authentication and a health query before running migrations.
5. Verify Redis when implementing authentication, and Kafka broker metadata/advertised listeners when implementing messaging.

No lab service was started or reconfigured during Day 1. Live connectivity remains a later prerequisite, not a completed validation.

## Dependency boundaries

The application environment contains Streamlit, Pydantic/settings, SQLAlchemy, Alembic, Psycopg, Redis, and the Kafka Python client. It does not install Airflow, dbt, Spark, or Graphify into the application runtime; those tools have separate environments.

Dependencies were selected against current package documentation and then installed and imported locally. References: [Streamlit installation](https://docs.streamlit.io/get-started/installation), [Psycopg binary installation](https://www.psycopg.org/psycopg3/docs/basic/install.html), and [Confluent Python client installation](https://github.com/confluentinc/confluent-kafka-python/blob/master/INSTALL.md). Import success is not a database/broker compatibility test.
