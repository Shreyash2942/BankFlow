# ADR-014: Airflow Analytics Orchestration

- Status: Accepted
- Date: 2026-10-14

## Context

Day 11 created reproducible dbt models, but their execution remained manual.
Version 1 needs an observable daily workflow that checks its source, rebuilds
models in dependency order, runs quality gates, and exposes failures in the
existing Airflow service.

## Decision

Use one daily Airflow DAG with five sequential BashOperator tasks: PostgreSQL
health, consumed-event freshness, dbt staging, dbt intermediate/marts, and dbt
tests plus documentation generation. The DAG reads credentials from the ignored
BankFlow environment file at task runtime and maps the host-oriented application
configuration to container-local PostgreSQL port 5432.

The freshness gate accepts an empty source with an explicit message and fails a
non-empty source older than 48 hours. The threshold is configurable. Tasks retry
twice with exponential backoff, have bounded execution time, and use a
credential-safe failure callback.

## Consequences

Analytics rebuilds now have a schedule, dependency graph, retry policy, quality
gate, and Airflow run history. An idle non-empty event stream becomes visible as
a failed freshness task. Operators must deploy the checked-in DAG from the
mounted repository to the container's separate Airflow DAG directory; the
runbook records that step.

The DAG orchestrates persisted Version 1 events only. Kafka consumer lifecycle
management and Version 2 lakehouse orchestration remain separate work.
