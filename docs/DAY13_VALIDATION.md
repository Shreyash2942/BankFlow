# Day 13 Analytics Dashboard and Platform Status Validation

Validated on 2026-10-14 from Windows Python 3.14 against the dedicated
`bankflow` container and the Version 1 dbt analytics schema.

## Delivered behavior

- `pages/5_Analytics.py` reads only the Day 11 dbt marts and supports 7-, 30-,
  and 90-day or all-history views.
- The analytics dashboard exposes transaction count, successful and declined
  outcomes, completed volume, withdrawal/deposit counts and amounts,
  authentication failures, and card locks.
- Transaction-volume and transaction-type charts render only persisted mart
  results. A guided empty state explains how to run the consumer and dbt when no
  events have reached analytics.
- `pages/6_Platform_Status.py` performs concurrent, bounded, read-only health
  probes for PostgreSQL, Redis, Kafka, and Airflow.
- The status page summarizes dbt models, tests, build results, and artifact time.
  It remains reachable without an ATM session so outages do not hide diagnostics.
- Airflow scheduler health and analytics-DAG availability are reported
  independently, so either failure remains visible.
- Both pages use the existing BankFlow design system and the supplied analytics
  and platform-status reference images.

## Live service evidence

The copied container returned the following bounded probe results:

```text
PostgreSQL: healthy
Redis: healthy
Kafka: healthy (1 broker reachable)
Airflow: healthy (scheduler healthy)
dbt: healthy (6 models, 67 tests, 73 successful build results)
bankflow_daily_analytics DAG: available after Day 12 deployment
```

The application analytics schema was queried successfully. It currently contains
zero consumed-event metrics, so the production dashboard correctly displays its
empty state instead of fabricated demo totals.

## Automated checks

```powershell
.\.venv\Scripts\python.exe -m ruff check src pages tests
.\.venv\Scripts\python.exe -m ruff format --check src pages tests
.\.venv\Scripts\python.exe -m pytest -q
```

The service-free suite passes 91 tests with 29 integration tests skipped. With
PostgreSQL, Redis, Kafka, and Streamlit opt-ins enabled, all 120 tests pass.
Coverage includes exact analytics aggregation, shared date filtering, safe
missing-mart behavior, Airflow scheduler interpretation, Kafka broker metadata,
dbt artifact summaries, honest missing-DAG status, and navigation through both
new Streamlit pages.

## Knowledge graph update

The incremental Graphify pass re-extracted the 10 changed Python files and the
Day 13 documentation. The refreshed graph contains 1,170 nodes, 1,905 edges,
and 72 communities, including named Analytics Dashboard, Platform Health
Monitoring, and Day 13 Validation communities. Its benchmark reduces the
362,143-word corpus to an average query context 110.1 times smaller.

## Reliability boundary

The dashboard is a read-only view of the latest materialized dbt build; it is not
a real-time view of operational tables. Service checks prove reachability at the
time shown, not continuous availability. No credentials, raw event payloads, or
driver error messages are rendered.
