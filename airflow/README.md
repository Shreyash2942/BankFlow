# BankFlow Airflow Orchestration

`bankflow_daily_analytics` rebuilds the Version 1 analytics layer every day at
02:00 UTC. It runs one ordered chain:

```text
postgresql_health
  -> event_freshness
  -> run_dbt_staging
  -> run_dbt_marts
  -> run_dbt_tests
```

The database task checks PostgreSQL and the `bankflow.consumed_events` source.
The freshness task fails when the newest consumed event is older than 48 hours.
An empty event store passes with an explicit `not applicable` message so a new
installation can build empty marts. Override the threshold with
`BANKFLOW_EVENT_FRESHNESS_HOURS` in the Airflow process environment.

Each task retries twice with exponential backoff. The failure callback records
the DAG, task, run, attempt, and exception type without logging database
credentials or command output.

## Deploy to the copied container

The repository is mounted at `/home/datalab/bankflow`, while Airflow scans
`/home/datalab/airflow/dags`. Copy the version-controlled DAG into that runtime
directory:

```powershell
docker exec bankflow bash -lc `
  "install -o datalab -g datalab -m 0644 `
  /home/datalab/bankflow/airflow/dags/bankflow_daily_analytics.py `
  /home/datalab/airflow/dags/bankflow_daily_analytics.py"
```

Validate parsing and dependency order:

```powershell
docker exec bankflow airflow dags list-import-errors --output table
docker exec bankflow airflow tasks list bankflow_daily_analytics --tree
```

## Trigger manually

Open [Airflow](http://localhost:8081/) and sign in with the local credentials
listed in `docs/SERVICES.md`. Find `bankflow_daily_analytics`, enable it if it is
paused, select **Trigger DAG**, and follow the graph or grid view until all five
tasks are green.

The equivalent CLI commands are:

```powershell
docker exec bankflow airflow dags unpause bankflow_daily_analytics
docker exec bankflow airflow dags trigger bankflow_daily_analytics
docker exec bankflow airflow dags list-runs --dag-id bankflow_daily_analytics
```

For an isolated full execution that does not wait for the scheduler:

```powershell
docker exec bankflow airflow dags test bankflow_daily_analytics 2026-10-14
```

The DAG reads the application database name, user, and password from the
ignored project `.env`. It deliberately uses container-local PostgreSQL port
5432 instead of the host-mapped port. Optional overrides are
`BANKFLOW_AIRFLOW_POSTGRES_HOST`, `BANKFLOW_AIRFLOW_POSTGRES_PORT`,
`BANKFLOW_PROJECT_DIR`, `BANKFLOW_ENV_FILE`, and `BANKFLOW_DBT_PROJECT_DIR`.
