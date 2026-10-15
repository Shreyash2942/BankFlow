# ADR-013: Mart-Backed Analytics and Failure-Tolerant Platform Status

- **Status:** Accepted
- **Date:** 2026-10-14

## Context

Day 13 needs business metrics and infrastructure status in Streamlit. Reporting
directly from operational banking tables would disagree with the event-driven
analytics boundary established in ADR-012. Requiring an authenticated runtime
for the status screen would also make diagnostics inaccessible during a
PostgreSQL or Redis outage.

## Decision

The analytics page reads the three materialized Version 1 dbt marts through a
read-only query boundary. One date filter is applied consistently to transaction
and authentication metrics. Exact amounts remain `Decimal`, and missing marts
produce an actionable empty state without exposing database errors.

The platform-status page is session-independent. PostgreSQL, Redis, Kafka, and
Airflow probes run concurrently with short configured timeouts and return a
small `healthy`, `degraded`, `unavailable`, or `pending` vocabulary. dbt status
comes from local `manifest.json` and `run_results.json` artifacts. The Airflow
scheduler and the BankFlow analytics DAG are reported separately, so a healthy
scheduler cannot imply that the separately deployed DAG exists.

The supplied UI images define layout, hierarchy, palette, and status treatment.
Every displayed value must come from a BankFlow service, mart, or build artifact.

## Consequences

Analytics freshness depends on Kafka consumption and a successful dbt rebuild.
The status page remains available during ATM-session failures and never performs
recovery actions. Local dbt artifacts are rebuildable and ignored by Git, so a
new checkout reports `pending` until dbt runs. Airflow orchestration remains a
separate deployable component described by ADR-014.
