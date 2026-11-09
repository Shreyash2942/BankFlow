# ADR-021: Cross-Layer Data-Quality Framework

- Status: Accepted
- Date: 2026-11-09
- Scope: Day 23

## Context

Bronze, Silver, and Gold jobs already contain local safeguards, but BankFlow also needs one explicit, queryable quality gate that verifies contracts across layer boundaries and can be surfaced to operators.

## Decision

BankFlow defines a version-controlled registry of Trino SQL rules in `bankflow.quality`. Each rule has a stable identifier, layer, category, description, and a query that returns exactly one nonnegative `violation_count`.

The runner evaluates rules independently so one query failure does not hide other results. A violation produces `failed`; a query or transport problem produces `error`. Both states fail the command unless diagnostic `--report-only` mode is explicitly selected.

Run summaries and per-rule results are written transactionally to the separate PostgreSQL `bankflow_quality` schema. Only counts and safe messages are stored; raw payloads and customer attributes are excluded. Streamlit reads only the latest persisted run.

## Consequences

- Quality status is durable, auditable, and independent of application transactions.
- Day 22 orchestration can invoke the runner as a strict task without duplicating rule logic.
- Reconciliation failures and infrastructure/query errors remain distinguishable.
- Adding or changing a rule requires a stable rule ID and focused test coverage.
- The initial framework validates batch-level current state; trend charts and alert routing remain future observability work.
