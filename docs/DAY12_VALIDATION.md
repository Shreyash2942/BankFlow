# Day 12 Airflow Analytics DAG Validation

Validated on 2026-10-14 with Airflow 2.9.3, dbt Core 1.8.7, and
dbt-postgres 1.8.2 in the dedicated `bankflow` container.

## Delivered behavior

- `bankflow_daily_analytics` runs daily at 02:00 UTC with catchup disabled and
  only one active run.
- PostgreSQL reachability and the `bankflow.consumed_events` source are checked
  before analytics work starts.
- The latest consumed event must be within the configurable 48-hour freshness
  window. An empty event store is reported explicitly and accepted for a new
  installation.
- dbt staging models, intermediate/mart models, all tests, and documentation are
  executed as separate ordered stages.
- Every task has two exponential-backoff retries, a 20-minute execution timeout,
  and a failure callback that logs task identity without credentials.
- The DAG is version-controlled under `airflow/dags/` and deployed to the
  container's configured `/home/datalab/airflow/dags` directory.

## Runtime evidence

Airflow reported no DAG import errors, the scheduler serialized the definition,
and the DAG was unpaused. An authenticated request to the Airflow grid view
returned HTTP 200 and contained `bankflow_daily_analytics`. Airflow rendered
this dependency chain:

```text
postgresql_health
  -> event_freshness
  -> run_dbt_staging
  -> run_dbt_marts
  -> run_dbt_tests
```

The full command below completed successfully:

```powershell
docker exec bankflow airflow dags test bankflow_daily_analytics 2026-10-14
```

All five Airflow task instances finished in `success`. The freshness task found
the application event store empty and logged that freshness was not applicable.
dbt rebuilt two staging tables, one intermediate view, and three marts; all 67
data tests passed with zero warnings, errors, or skips; documentation generation
wrote the catalog successfully.

The successful DAG run and five successful task instances are persisted in the
Airflow metadata database and available from the Airflow graph/grid views.

## Manual operation

See `airflow/README.md` for deployment, parsing checks, UI triggering, CLI
triggering, and supported environment overrides.

## Knowledge graph update

The incremental Graphify pass re-extracted the Airflow DAG and nine changed
documents. The refreshed graph contains 1,187 nodes, 1,918 edges, 23
hyperedges, and 75 communities, including named Airflow Analytics DAG and Day
12 Orchestration communities. Its benchmark reduces the 363,805-word corpus to
an average query context 97.4 times smaller.

## Reliability boundary

The workflow validates the PostgreSQL event store and transforms data already
persisted by the Kafka consumer. It does not start or supervise that consumer.
The freshness gate detects stale non-empty input; an empty source is accepted so
first-run deployments can create valid empty marts.
