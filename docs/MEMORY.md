# BankFlow Project Memory

**Project Name:** BankFlow  
**Repository Name:** `BankFlow`  
**Document Type:** Living Project Memory / Handoff File  
**Purpose:** Preserve project context, implementation state, decisions, issues, and next actions across developers, sessions, and AI agents.  
**Last Updated:** 2026-09-27  

---

# 1. How to Use This File

`MEMORY.md` is the operational memory of the BankFlow project.

It should be read **before starting work** and updated **before ending any meaningful development session**.

This file is not a replacement for the project's formal documents.

Use the following documents as the authoritative source for their specific areas:

| Document | Source of Truth For |
|---|---|
| `PRODUCT_REQUIREMENTS.md` | Product scope, goals, users, core features |
| `ARCHITECTURE.md` | System architecture, technology roles, data flow |
| `DESIGN.md` | Visual language, UI components, colors, typography |
| `TASK.md` | 4-week implementation plan, daily tasks, milestones |
| `MEMORY.md` | Current status, active context, issues, decisions, handoff information |

If this file conflicts with one of the formal documents, the formal document wins unless a newer approved decision is explicitly recorded in the **Architecture / Product Decisions** section below.

---

# 2. Project Context

BankFlow began as an academic ATM simulation and is being expanded into a professional portfolio project.

The project evolution is:

```text
Academic ATM Prototype
        ↓
Modular Python Application
        ↓
Streamlit Web Application
        ↓
Persistent Transaction Platform
        ↓
Event-Driven Architecture
        ↓
Operational Analytics
        ↓
Streaming Data Platform
        ↓
Iceberg Lakehouse
        ↓
BankFlow v2.0
```

The project is intentionally designed to demonstrate both:

- software engineering
- data engineering

BankFlow uses fictional/demo banking data only.

It must never connect to real banking systems or store real customer financial credentials.

---

# 3. Product Vision

BankFlow is an event-driven ATM transaction and analytics platform.

## Version 1

Version 1 focuses on:

- Python application architecture
- Streamlit UI
- PostgreSQL persistence
- Redis authentication/session state
- Kafka event streaming
- Airflow orchestration
- dbt analytics
- testing
- CI/CD
- professional documentation

## Version 2

Version 2 extends BankFlow with:

- synthetic transaction generation
- Spark Structured Streaming
- Apache Iceberg
- Hadoop/HDFS
- Hive Metastore
- Bronze / Silver / Gold data layers
- data-quality validation
- analytics-serving patterns

---

# 4. Current Project Status

- Overall status: Implementation - Day 3 core domain model complete.
- Release: v0.1.0 package foundation; no release tag or published application.
- Phase: Phase 1, application foundation.
- Week/day: Week 1, Day 3 complete; Day 4 next.

| Area | Status |
|---|---|
| Requirements, architecture, design, task plan | Canonical copies in docs/ |
| Repository and package foundation | Complete |
| Academic baseline | 18 assets preserved with hashes |
| Python environment | Python 3.14.4, Windows x64; dependencies installed |
| PostgreSQL | Five operational models, exact money, demo seed, and Alembic revision 0002 verified |
| Redis / Kafka connections | Not implemented |
| Transaction services and Streamlit UI | Not implemented |
| Airflow / dbt / Spark / Iceberg | Not implemented |
| Automated application tests / CI | 15 unit cases and eight live PostgreSQL tests pass; CI remains planned |
| Graph and analysis | Baseline preserved; Day 3 graph includes the implemented domain model |

---

# 5. Completed Documentation

The following planning documents have been defined:

```text
PRODUCT_REQUIREMENTS.md
ARCHITECTURE.md
DESIGN.md
TASK.md
MEMORY.md
```

These canonical documents are part of the Day 1 repository foundation. The original workspace copies remain historical inputs.

---

# 6. Current Technology Decisions

## Version 1 Stack

```text
Python
Streamlit
Pydantic
SQLAlchemy
Alembic
PostgreSQL
Redis
Apache Kafka
confluent-kafka
Airflow
dbt
pytest
Docker
GitHub Actions
Git / GitHub
```

## Version 2 Additional Stack

```text
Apache Spark
PySpark
Spark Structured Streaming
Apache Iceberg
Hadoop / HDFS
Hive Metastore
```

## Technologies Available in the Existing Lab but Not Planned for BankFlow v1/v2

```text
MongoDB
Hudi
Delta Lake
Java
Scala
Terraform
```

These technologies should not be added unless a clear architectural requirement is approved.

---

# 7. Existing Infrastructure Context

The local Docker-based data lab already contains the following stacks:

```text
stacks/airflow
stacks/spark
stacks/kafka
stacks/hive
stacks/hadoop
stacks/dbt
stacks/postgres
stacks/mongodb
stacks/redis
stacks/lakehouse/hudi
stacks/lakehouse/iceberg
stacks/lakehouse/delta
stacks/python
stacks/java
stacks/scala
stacks/terraform
```

BankFlow uses the user-created dedicated `bankflow` container built from the existing lab image; see ADR-002 and docs/SERVICES.md.

Use the services inside `bankflow`; its volume and host mappings have been inspected. Do not change other project containers.

---

# 8. Architecture Snapshot

## Version 1

```text
User
  ↓
Streamlit
  ↓
Python Service Layer
  ├── Authentication Service
  ├── Account Service
  └── Transaction Service
          ↓
    PostgreSQL
          +
        Redis
          ↓
     Kafka Producer
          ↓
bankflow.transaction.events
          ↓
     Kafka Consumer
          ↓
 Operational Event Store
          ↓
        Airflow
          ↓
          dbt
          ↓
PostgreSQL Analytics Marts
          ↓
 Streamlit Analytics
```

## Version 2

```text
Application / Synthetic Generator
              ↓
             Kafka
              ↓
    Spark Structured Streaming
              ↓
         Iceberg Bronze
              ↓
         Iceberg Silver
              ↓
          Iceberg Gold
              ↓
 PostgreSQL Analytics Serving
              ↓
             dbt
              ↓
     Streamlit Analytics
```

---

# 9. Core Business Rules

Current approved business rules:

## Authentication

```text
BR-001: A user must authenticate before accessing account operations.
BR-002: PIN validation uses a stored PIN hash, not a plain-text PIN.
BR-003: Failed PIN attempts are counted.
BR-004: Maximum PIN attempts default to 3.
BR-005: The card is locked when the maximum attempt limit is reached.
BR-006: PIN values and PIN hashes must never appear in application logs or Kafka events.
```

## Transactions

```text
BR-007: Withdrawal amount must be greater than zero.
BR-008: Deposit amount must be greater than zero.
BR-009: Withdrawal cannot exceed available balance.
BR-010: Financial values use Decimal / exact numeric database types.
BR-011: Account balance update and transaction creation must be atomic.
BR-012: Every transaction receives a unique transaction ID.
BR-013: Successful transactions record balance-before and balance-after values.
```

## Academic Compatibility Rule

```text
BR-014: Account closure at zero balance is retained as a configurable demo rule.
```

Configuration:

```python
AUTO_CLOSE_ZERO_BALANCE = True
```

This is not intended to represent normal real-world banking behavior.

---

# 10. Kafka Event Contract Memory

Primary topic:

```text
bankflow.transaction.events
```

Expected event types:

```text
authentication.succeeded
authentication.failed
card.locked
balance.viewed
withdrawal.requested
withdrawal.completed
withdrawal.declined
deposit.completed
account.closed
session.ended
```

Every event should include an envelope similar to:

```text
event_id
event_type
schema_version
event_timestamp
source
account_id (when applicable)
transaction_id (when applicable)
status
payload
```

Never publish:

```text
PIN
PIN hash
database password
API secrets
real personal data
```

---

# 11. Database Memory

Expected operational PostgreSQL entities:

```text
customers
accounts
cards
transactions
audit_events
```

Expected analytics-serving entities:

```text
analytics_daily_transactions
analytics_authentication_metrics
analytics_account_activity
analytics_hourly_volume
```

Money should use:

```text
Decimal in Python
NUMERIC / DECIMAL in PostgreSQL
```

Do not use floating-point values for balances or transaction amounts.

---

# 12. Redis Memory

Redis is temporary operational state only.

Expected key patterns:

```text
bankflow:session:<session_id>
bankflow:card:<card_id>:pin_attempts
bankflow:card:<card_id>:lock
```

PostgreSQL remains the permanent system of record.

---

# 13. Lakehouse Memory

Version 2 uses:

```text
Apache Iceberg
```

Do not use Hudi and Delta Lake in the same BankFlow implementation unless the project scope is explicitly expanded.

Expected layers:

## Bronze

```text
bronze_bankflow_events
```

## Silver

```text
silver_transactions
silver_authentication_events
silver_account_events
```

## Gold

```text
gold_daily_transaction_metrics
gold_hourly_transaction_volume
gold_account_activity
gold_authentication_metrics
gold_declined_transactions
```

---

# 14. UI / Design Memory

Brand direction:

```text
Modern
Minimal
Trustworthy
Data-focused
```

Primary colors:

```text
Navy     #0F172A
Blue     #2563EB
Emerald  #059669
Background #F8FAFC
Error    #DC2626
Warning  #D97706
```

Primary interface:

```text
Streamlit
```

Important visual rule:

```text
The application must always identify itself as a demo environment.
```

The UI must not imitate a real bank so closely that users could mistake it for an actual banking service.

---

# 15. Repository Structure

The existing repository is `BankFlow`. The Python distribution is `bankflow-atm` and its import package is `bankflow`.

- Canonical planning and handoff: `docs/`.
- Application package: `src/bankflow/{config,models,schemas,services,repositories,database,cache,messaging,utils}`.
- Reserved integration paths: `pages/`, `consumers/`, `migrations/`, `airflow/`, `dbt/`, `streaming/`, `spark/`.
- Tests: `tests/{unit,integration,kafka,spark,data_quality}`.
- Academic originals: `docs/original-college-project/`, with checksum manifest.
- Historical analysis: `docs/analysis/`.
- Graph: `graphify-out/`.

Original workspace copies outside the repository are source snapshots, not the maintained documents. See `README.md` and `docs/architecture/ADR-001-foundation.md`.

---

# 16. Release Roadmap Memory

```text
v0.1.0 — Project Foundation
v0.2.0 — PostgreSQL Persistence
v0.3.0 — Authentication + Redis
v0.4.0 — Transaction Engine
v0.5.0 — Streamlit UI

v0.6.0 — Kafka Events
v0.7.0 — Kafka Consumer
v0.8.0 — Airflow + dbt
v0.9.0 — Testing + CI
v1.0.0 — BankFlow Application Platform

v1.1.0 — Synthetic Event Generator
v1.2.0 — Spark Structured Streaming
v1.3.0 — Iceberg Bronze
v1.4.0 — Silver / Gold Lakehouse
v1.5.0 — Serving Analytics

v2.0.0 — BankFlow Data Platform
```

---

# 17. Current Issues / Bugs

## Open Issues

Configuration and database foundation are implemented; domain services and UI are still planned. The existing academic prototype was reviewed and executed on 2026-09-22; its known defects are listed below.

Current planning issue:

### ISSUE-001 — Existing Docker Service Details Not Yet Inspected

**Status:** PostgreSQL resolved; Redis and Kafka validation pending  
**Severity:** Medium  
**Type:** Environment / Dependency  

**Description**

The project plans to reuse PostgreSQL, Redis, Kafka, Airflow, dbt, Spark, Hadoop, Hive, and Iceberg from an existing Docker-based data lab.

The user created the running `bankflow` container with a dedicated runtime volume. Day 2 verified authenticated PostgreSQL access and migrations with separate application/test databases. Redis authentication and Kafka metadata remain future checks.

**Impact**

PostgreSQL configuration is verified. Redis and Kafka integration require their own readiness and authentication checks.

**Next Action**

Inspect:

```bash
docker ps
docker network ls
```

and relevant Docker Compose files before creating BankFlow service configuration.

---

### ISSUE-002 ? Legacy amount validation accepts non-finite and sub-cent values

**Status:** Open (legacy prototype)  
**Severity:** High for transaction correctness  
**Evidence:** `atm_simulation.py` accepts `nan` and reports a NaN balance; `0.001` is accepted and displayed as a $0.00 withdrawal. Reproduced with captured console inputs in `docs/analysis/PROTOTYPE_VALIDATION.json`.

**Next Action:** Preserve the academic script as provenance; implement and test finite Decimal values and an explicit precision policy in the new transaction core.

### ISSUE-003 ? Lockout policy and diagram inconsistencies

**Status:** Open (specification)  
**Evidence:** TASK Day 5 specifies persistent PostgreSQL lock status; DESIGN section 13 calls the lock temporary. Legacy UML includes incorrect retry connectors, retain/eject conflicts, and different debit/dispense ordering.

**Next Action:** Resolve the lockout/reset policy before authentication work and revise implementation diagrams against the new requirements. See `docs/analysis/DOCUMENT_REVIEW.md` and `docs/analysis/DIAGRAM_REVIEW.md`.

---

# 18. Known Risks

## RISK-001 — Scope Creep

**Risk**

BankFlow has access to many technologies.

Adding every available technology could make the project difficult to complete and difficult to explain.

**Mitigation**

Only use technologies defined in `PRODUCT_REQUIREMENTS.md` and `ARCHITECTURE.md`.

---

## RISK-002 — Infrastructure Coupling

**Risk**

BankFlow may become too dependent on the existing local Docker lab.

**Mitigation**

Keep application configuration environment-driven and document service dependencies clearly.

---

## RISK-003 — Kafka / Database Consistency

**Risk**

A database transaction may succeed while event publication fails.

**Mitigation**

For V1, explicitly handle producer failures and document behavior.

Consider an outbox pattern as a future improvement if reliability requirements increase.

---

## RISK-004 — Streamlit Session Behavior

**Risk**

Streamlit reruns can create unexpected session behavior.

**Mitigation**

Keep business state outside the UI where possible and use `st.session_state` only for presentation/session navigation.

Persistent data remains in PostgreSQL / Redis.

---

## RISK-005 — Local Resource Limits

**Risk**

Spark, Kafka, Airflow, Hadoop, Hive, Iceberg, PostgreSQL, and Redis running simultaneously may exceed local resources.

**Mitigation**

Start only required services for each phase and record local resource constraints during V2 performance testing.

---

# 19. Technical Debt Register

No new BankFlow implementation debt has been introduced. The legacy prototype uses float money and process-local state; preserve that baseline and replace these limitations in the new core rather than treating it as the completed platform.

Use this section once implementation begins.

Template:

```text
TD-001
Title:
Status:
Priority:
Introduced:
Reason:
Impact:
Planned Resolution:
Target Version:
```

---

# 20. Architecture / Product Decisions

Important decisions should be recorded here so future developers or agents do not reopen settled questions unnecessarily.

---

## ADR-MEM-001 — Use Streamlit Instead of React

**Status:** Accepted  

**Decision**

Use Streamlit for BankFlow's portfolio UI.

**Reason**

The project is Python-focused and prioritizes rapid delivery of a professional interactive demo over frontend-framework complexity.

---

## ADR-MEM-002 — PostgreSQL Is the System of Record

**Status:** Accepted  

**Decision**

PostgreSQL stores permanent operational state.

Redis must not store permanent balances or financial transaction history.

---

## ADR-MEM-003 — Redis for Temporary Authentication State

**Status:** Accepted  

**Decision**

Redis stores sessions, failed-attempt counters, and temporary lock state.

---

## ADR-MEM-004 — Kafka as Event Backbone

**Status:** Accepted  

**Decision**

Application events are published to:

```text
bankflow.transaction.events
```

Kafka decouples transaction processing from downstream analytics.

---

## ADR-MEM-005 — Apache Iceberg for V2

**Status:** Accepted  

**Decision**

Use Apache Iceberg as BankFlow's V2 lakehouse format.

Hudi and Delta are intentionally excluded from the current scope.

---

## ADR-MEM-006 — Reuse Existing Docker Data Lab

**Status:** Accepted  

**Decision**

Original Day 1 decision: reuse the shared lab. Superseded by the user-approved dedicated `bankflow` copy; see `docs/architecture/ADR-002-dedicated-container.md`.

---

## ADR-MEM-007 — Exact and Traceable Domain Persistence

**Status:** Accepted  

**Decision**

Use UUID identities, checked string enums, timezone-aware timestamps, `NUMERIC(18,2)` money, restrictive financial-history foreign keys, nullable retained audit references, and an account version counter. Store a fictional card token and salted PIN hash rather than a PAN or plaintext PIN. See `docs/architecture/ADR-004-core-domain-model.md`.

---

# 21. Active Work

Day 3 is complete: five persistent domain models, exact monetary values, migration `0002`, live constraint/relationship tests, and an idempotent fictional demo seed. Day 4 repositories are next. No business services or Streamlit screens have been implemented.

---

# 22. Next Actions

1. Create Customer, Account, Card, and Transaction repository classes.
2. Add typed lookup, history, transaction creation, and balance-update operations.
3. Keep transaction boundaries in the service/unit-of-work caller; repositories must not commit.
4. Add repository exceptions without leaking SQL or credentials.
5. Validate repository ordering, isolation, missing-record behavior, and exact money in `bankflow_test`.
6. Update Day 4 evidence, task checklist, graph, and this memory.

Resolve lockout policy, request idempotency, and post-commit publication behavior at their relevant later milestones. Do not infer live connectivity from dependency imports.

---

# 23. Environment Memory

Environment inventory from 2026-09-22; PostgreSQL updated and verified 2026-09-27:

- Python 3.14.4, Windows x64; isolated `.venv` with pinned dependencies.
- Docker engine 29.8.0; Docker Compose 5.5.1.
- Dedicated container `bankflow`, image `shreyash42/data-lab:latest`, running on `bridge`.
- Runtime volume `datalab-runtime-bankflow` -> `/home/datalab/runtime`; no other container currently mounts it.
- Repository bind mount -> `/home/datalab/bankflow`; container default Python is 3.10.12. The application remains on Windows Python 3.14.4.
- Published host ports: PostgreSQL 5433, Redis 6380, Kafka 9093. Internal ports remain 5432, 6379, and 9092.
- PostgreSQL 14.22 authenticates from Windows on port 5433; the application health query succeeds. Redis required authentication and Kafka metadata was unavailable in the earlier startup checks.
- HDFS 9000 and Spark RPC 7077 are internal-only in the inspected mappings.
- Copied `/medilake` storage paths are not adopted; future `/bankflow/bronze` and `/bankflow/silver` paths are proposed, not created.
- Selected connection strategy: application on Windows -> `127.0.0.1` published ports.
- User created and started the dedicated container/services. Day 2 provisioned only BankFlow database resources without resetting data or reconfiguring services.
- Application database/owner: `bankflow` / `bankflow_user`; test database/owner: `bankflow_test` / `bankflow_test_user`. Both are at migration 0002 with five operational tables. The application database has one fictional demo graph; generated credentials stay in ignored local files.
- Redis authentication, Kafka advertised listeners, other service versions, and V2 resource limits remain unverified.

See `docs/ENVIRONMENT.md` for setup and `docs/architecture/ADR-003-database-foundation.md` for database decisions. Never record credentials here.

---

# 24. Validation Evidence

Baseline characterization: five intended CLI scenarios behaved as expected; NaN and fractional-cent inputs exposed known legacy defects. Evidence: `docs/analysis/PROTOTYPE_VALIDATION.json`.

Day 1: Python environment and editable package installation succeeded; dependency consistency, import smoke checks, formatting, original-file hashes, and a legacy withdrawal scenario were checked. Evidence and exact commands: `docs/DAY1_VALIDATION.md`.

Day 2: all 17 tests passed at that milestone. See `docs/DAY2_VALIDATION.md`.

Day 3: all 23 tests pass, including eight live PostgreSQL tests for migration reversal, table relationships, exact cent round trips, timestamps, database constraints, role isolation, sessions, and idempotent seeding. Alembic reports 0002 (head), and autogeneration reports no new operations. See `docs/DAY3_VALIDATION.md`. Repositories, banking business logic, Redis, Kafka, and UI are not covered yet.

---

# 25. Failed Experiments / Rejected Approaches

Record approaches that were tried and intentionally abandoned.

This prevents another developer or AI agent from repeating failed work.

Template:

```text
EXPERIMENT-001
Date:
Approach:
Reason Tried:
Result:
Why Rejected:
Replacement:
```

Current entries:

```text
None.
```

---

# 26. Open Questions

Questions requiring future decisions:

```text
Q-001: Can Kafka return usable broker metadata from Windows?
Q-002: What Kafka deployment mode/version is currently used?
Q-004: What Hive/Iceberg catalog configuration already exists?
Q-005: What local resource limits should be assumed for V2 scale testing?
```

When resolved, move the answer into the appropriate permanent section and remove the question.

---

# 27. Session Handoff

## Last Session Summary

Completed Day 3 core persistence in the dedicated container. Five SQLAlchemy models, migration 0002, exact-money constraints, relationships, account versioning, and the fictional demo seed are verified. All 23 tests pass. See `docs/DAY3_VALIDATION.md` and ADR-004.

Populated `BankFlow` using `docs/` as the canonical documentation root and `src/bankflow/` as the application package. Preserved 18 academic assets unchanged, normalized the architecture filename, and retained dated baseline reviews. Added environment template, pinned dependencies, Windows dependency snapshot, Python setup guide, import checker, and package/linter configuration.

## Last Known Working State

The editable package and application dependencies import on Python 3.14.4. The archived CLI still performs its original single-session withdrawal. Application/test databases are at revision 0002; the application database contains one fictional customer/account/card graph with an exact $500.00 balance. Repositories, business services, and UI remain planned.

## Last Completed Task

Day 3 core domain models and seed. See `docs/DAY3_VALIDATION.md` for evidence and `graphify-out/GRAPH_REPORT.md` for graph provenance.

## Next Task

Day 4: repository layer for customer, account, card, transaction, balance-update, and ordered-history access.

## Blockers

No Day 4 blockers. The dedicated container must be running for integration tests. Redis authentication and Kafka metadata need later milestone checks.

---

# 28. Update Protocol for Developers and AI Agents

Before starting work:

1. Read `PRODUCT_REQUIREMENTS.md`.
2. Read `ARCHITECTURE.md`.
3. Read the relevant section of `TASK.md`.
4. Read `MEMORY.md`.
5. Confirm the current objective and blockers.
6. Do not assume infrastructure details that are still marked unknown.

During work:

1. Follow existing architecture unless a change is justified.
2. Record important issues as they are discovered.
3. Do not silently change product scope.
4. Add technical debt when shortcuts are intentionally taken.
5. Add architecture decisions when a significant design choice changes.
6. Preserve meaningful Git commit history.

Before ending work:

1. Update **Current Project Status**.
2. Update **Completed Documentation / Features** if needed.
3. Add or close issues.
4. Update **Known Risks** if new risks appear.
5. Update **Technical Debt Register**.
6. Record significant validation evidence.
7. Record failed experiments if relevant.
8. Update **Active Work**.
9. Update **Next Actions**.
10. Rewrite **Session Handoff**.
11. Update the `Last Updated` date.
12. Commit `MEMORY.md` when the state change is meaningful.

---

# 29. Rules for Maintaining Project Memory

## Always Record

- current phase
- current task
- feature completion
- active bugs
- blockers
- unresolved infrastructure issues
- important design changes
- test failures that require later work
- accepted technical debt
- next action
- release status

## Do Not Record

- passwords
- tokens
- private keys
- actual PIN values beyond documented fictional demo credentials
- production secrets
- unnecessary personal information
- long raw logs that belong in issue attachments

---

# 30. Memory Quality Checklist

Before committing this file, verify:

- [ ] Project status is current
- [ ] Active task is accurate
- [ ] Completed work is recorded
- [ ] Bugs are listed
- [ ] Closed bugs are marked resolved
- [ ] Blockers are documented
- [ ] Next action is specific
- [ ] New architecture decisions are recorded
- [ ] Technical debt is updated
- [ ] Validation evidence is recorded
- [ ] Session handoff is rewritten
- [ ] No secrets are present
- [ ] Last Updated date is current

---

# 31. Quick Context for a New Developer or AI Agent

If only one section can be read before starting work, read this:

> BankFlow is a fictional ATM portfolio project. Days 1–3 are complete in the existing `BankFlow` repository: preserved academic assets, Python 3.14 package, validated configuration, PostgreSQL sessions/health, five operational SQLAlchemy models, exact money, migration 0002, and an idempotent fictional demo seed. All 23 tests pass. Application/test databases use restricted owners and ignored credentials; the application database contains one demo graph with a $500.00 balance. Begin Day 4 repositories using `docs/TASK.md`, ADR-004, and `docs/DAY3_VALIDATION.md`. Business services and UI remain planned; Redis authentication and Kafka metadata need later validation.
