# BankFlow Project Memory

**Project Name:** BankFlow  
**Repository Name:** `BankFlow`  
**Document Type:** Living Project Memory / Handoff File  
**Purpose:** Preserve project context, implementation state, decisions, issues, and next actions across developers, sessions, and AI agents.  
**Last Updated:** 2026-10-28  

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

- Overall status: Version 1 released; Days 15–16 streaming source and Spark ingestion foundation complete.
- Release: BankFlow Application Platform v1.0.0.
- Phase: Phase 3 active; Kafka-to-Spark ingestion complete and Iceberg Bronze is next.
- Week/day: Week 3, Day 16 complete; Day 17 next.

| Area | Status |
|---|---|
| Requirements, architecture, design, task plan | Canonical copies in docs/ |
| Repository and package foundation | Complete |
| Academic baseline | 18 assets preserved with hashes |
| Python environment | Python 3.14.4, Windows x64; dependencies installed |
| PostgreSQL | Six operational/event-store models, exact money, demo seed, and Alembic revision 0003 verified |
| Repository layer | Customer, account, card, and transaction access verified against PostgreSQL |
| Authentication / Redis | Authenticated client, expiring counters/sessions, audit events, and durable card lock verified |
| Kafka events | Versioned producer, Python consumer, synthetic publisher, and Spark consumer verified against Kafka 3.7.1 |
| Transaction services | Exact balance inquiry, withdrawal, deposit, decline, closure, and history workflows verified |
| Streamlit UI | ATM flows plus mart-backed analytics and failure-tolerant platform status verified against supplied designs |
| Airflow / dbt / Spark / Iceberg | Version 1 Airflow/dbt complete; Spark 3.5.1 streaming foundation complete; Iceberg layers remain planned |
| Automated application tests / CI | 117 service-free cases and all 146 cases pass with PostgreSQL/Redis/Streamlit/Kafka opt-ins; Spark live evidence is documented separately |
| Graph and analysis | Days 1–13 graph: 1,187 nodes, 1,918 edges, 23 hyperedges, and 75 communities; Airflow orchestration, analytics, platform health, and validation provenance included; 97.4x benchmark reduction |

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
consumed_events
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

**Status:** Resolved for PostgreSQL, Redis, and Kafka  
**Severity:** Medium  
**Type:** Environment / Dependency  

**Description**

The project plans to reuse PostgreSQL, Redis, Kafka, Airflow, dbt, Spark, Hadoop, Hive, and Iceberg from an existing Docker-based data lab.

The user created the running `bankflow` container with a dedicated runtime volume. Day 2 verified authenticated PostgreSQL access and migrations with separate application/test databases. Day 5 verified authenticated Redis access. Day 9 found and corrected the copied broker's unreachable advertised listener and verified Kafka 3.7.1 metadata and delivery.

**Impact**

PostgreSQL, Redis, and Kafka application endpoints are verified. Later services remain milestone-specific.

**Next Action**

Inspect each later service when its milestone begins; do not infer health from an exposed port.

---

### ISSUE-002 ? Legacy amount validation accepts non-finite and sub-cent values

**Status:** Resolved in the application core; retained in the archived prototype  
**Severity:** High for transaction correctness  
**Evidence:** `atm_simulation.py` accepts `nan` and reports a NaN balance; `0.001` is accepted and displayed as a $0.00 withdrawal. Reproduced with captured console inputs in `docs/analysis/PROTOTYPE_VALIDATION.json`.

**Resolution:** Day 6 requires finite positive Python `Decimal`, enforces cent precision and `NUMERIC(18,2)` bounds, and tests the rejected legacy cases. The academic script remains unchanged as provenance.

### ISSUE-003 ? Lockout policy and diagram inconsistencies

**Status:** Resolved for the application; legacy diagrams remain archived  
**Evidence:** TASK Day 5 specifies persistent PostgreSQL lock status; DESIGN section 13 calls the lock temporary. Legacy UML includes incorrect retry connectors, retain/eject conflicts, and different debit/dispense ordering.

**Resolution:** Day 5 made PostgreSQL card lockout permanent while Redis counters remain temporary. The maintained architecture flow now reflects the implementation; original diagrams remain unchanged. See ADR-006.

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

Day 9 publishes only after commit, bounds delivery waits, logs broker failures, and returns the committed banking result. TD-001 records the remaining crash gap; use an outbox if guaranteed recovery becomes a release requirement.

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

The legacy prototype uses float money and process-local state; preserve that baseline and replace these limitations in the new core rather than treating it as the completed platform.

```text
TD-001
Title: Direct post-commit Kafka publication has no durable replay
Status: Accepted for V1
Priority: Medium
Introduced: Day 9
Reason: Preserve PostgreSQL authority without adding outbox schema and relay scope to producer day
Impact: A process crash after commit and before acknowledgement can omit an event
Planned Resolution: Add a transactional outbox and idempotent relay if release reliability requires recovery
Target Version: Future reliability milestone
```

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

## ADR-MEM-008 — Session-Bound Repository Boundary

**Status:** Accepted

**Decision**

Repositories receive the caller's SQLAlchemy session, use typed ORM queries, flush writes, and never commit or roll back. Transaction history uses deterministic newest-first ordering. Balance updates combine a row lock with the account version counter. Stable repository exceptions shield services from persistence details. See `docs/architecture/ADR-005-repository-boundary.md`.

## ADR-MEM-009 — Split Authentication State by Durability

**Decision**

PostgreSQL stores salted PIN hashes and permanent card locks. Redis stores only expiring failed-attempt counters and sessions. Card rows are locked during authentication; session tokens are opaque and hashed in Redis keys; authentication fails closed if Redis is unavailable. See `docs/architecture/ADR-006-authentication-state.md`.

## ADR-MEM-010 — Exact and Atomic Transaction Engine

**Decision**

Transaction requests require finite positive Python `Decimal` values at cent precision. Services verify the authenticated customer/account/card graph, lock the account row, and persist balance changes, UUID transaction snapshots, account versions, and audit rows in one caller-owned transaction. Insufficient funds are persisted as a decline; zero-balance closure remains configurable. See `docs/architecture/ADR-007-transaction-engine.md`.

## ADR-MEM-011 — Versioned and Secret-Free Event Contract

**Decision**

Application events use one immutable schema-version-1 envelope with UUID4 identity, dotted event type, UTC occurrence time, fixed application source, and a discriminated transaction or authentication payload. Exact money serializes as decimal strings. Closed schemas reject unknown or inconsistent fields, and event factories never expose PIN material, card/session tokens, credentials, or unnecessary personal data. Factories remain independent of Kafka; Day 9 owns post-commit publication. See `docs/architecture/ADR-009-event-contract.md`.

## ADR-MEM-012 — Acknowledged Post-Commit Kafka Publication

**Decision**

`BankFlowRuntime` publishes validated events only after its caller-owned PostgreSQL transaction commits. The producer uses idempotence, `acks=all`, bounded delivery callbacks, aggregate keys, and safe headers. Broker failures are logged and do not reverse the committed banking operation. The known commit-to-publish gap is accepted for V1. See `docs/architecture/ADR-010-kafka-producer.md`.

## ADR-MEM-013 — Idempotent Validating Kafka Consumer

**Decision**

The operational consumer validates the complete version-1 envelope, persists valid records to the independent `consumed_events` table, and commits Kafka offsets only after persistence, duplicate confirmation, or deliberate invalid-message rejection. Event ID and Kafka position uniqueness make replay idempotent. Logs contain identifiers and positions rather than message bodies. See `docs/architecture/ADR-011-kafka-consumer-event-store.md`.

## ADR-MEM-014 — Daily Airflow Analytics Orchestration

**Decision**

Airflow runs one daily, sequential Version 1 workflow: PostgreSQL health, consumed-event freshness, dbt staging, dbt intermediate/marts, and dbt tests plus documentation. Empty first-run input is explicit and acceptable; stale non-empty input fails. Tasks use bounded execution, two exponential-backoff retries, and credential-safe failure logging. See `docs/architecture/ADR-014-airflow-analytics-orchestration.md`.

---

# 21. Active Work

Day 16 is complete. BankFlow now consumes the synthetic/application Kafka stream through Spark 3.5.1, parses the version-1 contract with exact decimal fields, classifies invalid records, emits structured batch metrics, and resumes from HDFS checkpoints. Invalid quarantine stores transport metadata and a SHA-256 fingerprint, never the raw value.

---

# 22. Next Actions

1. Begin Day 17's Iceberg Bronze layer using the validated Day 16 stream.
2. Inspect and approve the existing Hive Metastore/Iceberg catalog configuration before creating tables.
3. Preserve raw Kafka metadata and version-1 event values in Bronze while keeping invalid-record policy explicit.

Keep TD-001 visible in analytics freshness expectations; consumer idempotence cannot recover events never published by the application.

---

# 23. Environment Memory

Environment inventory from 2026-09-22; PostgreSQL, Redis, and Kafka updated and verified through 2026-10-27:

- Python 3.14.4, Windows x64; isolated `.venv` with pinned dependencies.
- Docker engine 29.8.0; Docker Compose 5.5.1.
- Dedicated container `bankflow`, image `shreyash42/data-lab:latest`, running on `bridge`.
- Runtime volume `datalab-runtime-bankflow` -> `/home/datalab/runtime`; no other container currently mounts it.
- Repository bind mount -> `/home/datalab/bankflow`; container default Python is 3.10.12. The application remains on Windows Python 3.14.4.
- Published host ports: PostgreSQL 5433, Redis 6380, Kafka 9093. Internal ports remain 5432, 6379, and 9092.
- PostgreSQL 14.22 authenticates from Windows on port 5433. Redis 6.0.16 authenticates on port 6380; counters and expiring sessions succeed. Kafka 3.7.1 acknowledges producer events and supports validating consumer persistence, replay deduplication, invalid-message offset advancement, and paced synthetic publication on port 9093.
- HDFS 9000 and Spark RPC 7077 are internal-only in the inspected mappings.
- Copied `/medilake` storage paths are not adopted; future `/bankflow/bronze` and `/bankflow/silver` paths are proposed, not created.
- Selected connection strategy: application on Windows -> `127.0.0.1` published ports.
- User created and started the dedicated container/services. Day 2 provisioned only BankFlow database resources without resetting data or reconfiguring services.
- Application database/owner: `bankflow` / `bankflow_user`; test database/owner: `bankflow_test` / `bankflow_test_user`. Both are at migration 0003 with five banking/audit tables plus `consumed_events`. The application database has one fictional demo graph; generated credentials stay in ignored local files.
- Kafka advertises `host.docker.internal:9093`; its application topic has one partition and replication factor one.
- dbt Core 1.8.7 with dbt-postgres 1.8.2 runs inside the container. Test and application targets build into their own `bankflow_analytics` schemas; generated docs live in ignored `dbt/target/`.
- Day 12 deploys `bankflow_daily_analytics` to Airflow 2.9.3. A full five-task run succeeded, rebuilding six dbt models, passing all 67 data tests, and generating documentation.
- Day 13 live probes verify PostgreSQL, Redis, one Kafka broker, the Airflow scheduler, the analytics DAG definition, and current dbt artifacts.
- Day 16 verifies Spark 3.5.1/Scala 2.12 through `spark://localhost:7077`, resolves `spark-sql-kafka-0-10_2.12:3.5.1`, consumes Kafka through `localhost:9092`, and stores checkpoints/quarantine metadata under HDFS `/bankflow` paths as the `datalab` user.
- Other service versions and V2 resource limits remain unverified.

See `docs/ENVIRONMENT.md` for setup and `docs/architecture/ADR-003-database-foundation.md` for database decisions. Never record credentials here.

---

# 24. Validation Evidence

Baseline characterization: five intended CLI scenarios behaved as expected; NaN and fractional-cent inputs exposed known legacy defects. Evidence: `docs/analysis/PROTOTYPE_VALIDATION.json`.

Day 1: Python environment and editable package installation succeeded; dependency consistency, import smoke checks, formatting, original-file hashes, and a legacy withdrawal scenario were checked. Evidence and exact commands: `docs/DAY1_VALIDATION.md`.

Day 2: all 17 tests passed at that milestone. See `docs/DAY2_VALIDATION.md`.

Day 3: all 23 tests pass, including eight live PostgreSQL tests for migration reversal, table relationships, exact cent round trips, timestamps, database constraints, role isolation, sessions, and idempotent seeding. Alembic reports 0002 (head), and autogeneration reports no new operations. See `docs/DAY3_VALIDATION.md`. Repositories, banking business logic, Redis, Kafka, and UI are not covered yet.

Day 4: all 26 tests pass, including 11 live PostgreSQL tests. Repository coverage verifies UUID/business-key lookups, stable list/history ordering, bounded pagination, exact `Decimal` inputs, row locks, version increments and conflicts, transaction creation, constraint translation, and caller-owned rollback. See `docs/DAY4_VALIDATION.md`. Authentication, Redis state, banking rules, Kafka, and UI are not covered yet.

Day 5: all 44 tests pass, including 14 live PostgreSQL/Redis tests. Authentication coverage verifies correct PINs, three-step lockout, locked-card denial, counter reset, expiring sessions, durable card status, secret-free audit details, and fail-closed Redis errors. See `docs/DAY5_VALIDATION.md`. Banking rules, Kafka, and UI are not covered yet.

Day 6: all 71 tests pass, including 20 live PostgreSQL/Redis tests. Transaction coverage verifies strict finite cent-precision money, balance inquiry, successful and declined withdrawals, deposits, overflow prevention, UUID history, subject authorization, configurable zero-balance closure, and whole-unit rollback after persistence failure. See `docs/DAY6_VALIDATION.md`. Streamlit, Kafka, and analytics remain planned.

Day 7: all 73 tests pass, including 22 live PostgreSQL/Redis/Streamlit tests. UI acceptance coverage verifies authentication, balance inquiry, withdrawal, deposit, history ordering, atomic demo reset, and Redis session termination through the actual Streamlit pages. See `docs/DAY7_VALIDATION.md`. Kafka and analytics remain planned.

Day 8: 68 service-free tests pass and all 90 tests pass with the 22 live PostgreSQL/Redis/Streamlit cases enabled. Event coverage verifies the closed version-1 envelope, UUID4 identity, UTC timestamps, exact decimal serialization, event-to-payload consistency, transaction/authentication factory mappings, prohibited-field absence, secret-free authentication output, and JSON round trips. See `docs/DAY8_VALIDATION.md`. Kafka transport and analytics remain planned.

Day 9: 74 service-free tests pass and all 100 tests pass with 26 live PostgreSQL/Redis/Streamlit/Kafka cases enabled. Producer coverage verifies idempotent all-ack configuration, serialization, aggregate keys, safe headers, callbacks, receipts, timeouts, queue failures, post-commit visibility, authentication/card/transaction lifecycles, unavailable-broker commit preservation, and a live produce/consume round trip. See `docs/DAY9_VALIDATION.md`. Kafka consumption and analytics remain planned.

Day 10: 83 service-free tests pass and all 112 tests pass with 29 live PostgreSQL/Redis/Streamlit/Kafka cases enabled. Consumer coverage verifies manual commit configuration, complete-envelope validation, structured secret-free logs, PostgreSQL-before-offset ordering, exact JSON payload persistence, event-ID and Kafka-position deduplication, broker/database failure behavior, graceful shutdown, and a live persistence/replay/invalid-message path. See `docs/DAY10_VALIDATION.md`.

Day 11: dbt debug and full builds pass against the test and application databases. Six models and their generic/singular tests validate the source contract, exact-money casts, controlled dimensions, unique grains, bounded financial metrics, and source-to-mart reconciliation. A controlled nine-event fixture produced the expected transaction, authentication, and account totals, then was removed before the clean rebuild. dbt documentation generation succeeds. See `docs/DAY11_VALIDATION.md`.

Day 12: Airflow reports zero DAG import errors. All five tasks in `bankflow_daily_analytics` completed successfully, including two staging models, one intermediate model, three marts, 67 passing dbt data tests, and documentation generation. See `docs/DAY12_VALIDATION.md`.

Day 13: 91 service-free tests and all 120 tests with PostgreSQL/Redis/Streamlit/Kafka opt-ins pass. Coverage verifies exact mart aggregation, date filtering, safe missing-data behavior, live service health probes, dbt artifact summaries, missing-DAG behavior, and navigation through both new Streamlit pages. See `docs/DAY13_VALIDATION.md`.

Day 14: 92 service-free tests and all 121 tests with PostgreSQL/Redis/Streamlit/Kafka opt-ins pass. Ruff, dependency, and Python 3.14 environment checks pass. A clean dbt build completes six models and 67 tests, Airflow reports zero import errors and completes all five DAG tasks, and live status reports all five monitored systems healthy. See `docs/DAY14_VALIDATION.md`.

Day 15: 105 service-free tests and all 134 tests with PostgreSQL/Redis/Streamlit/Kafka opt-ins pass. A deterministic 10,000-event dry run round-tripped through the version-1 schema, and a paced 40-event stream was acknowledged by Kafka and independently consumed with matching type counts, unique event IDs, and ATM provenance. See `docs/DAY15_VALIDATION.md`.

Day 16: 117 service-free tests and all 146 tests with PostgreSQL/Redis/Streamlit/Kafka opt-ins pass. Three live Spark batches consumed 50 valid events plus one malformed and two structurally invalid records, checkpointed offsets in HDFS, resumed without replay, and wrote only safe invalid metadata. See `docs/DAY16_VALIDATION.md`.

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
Q-004: What Hive/Iceberg catalog configuration already exists?
Q-005: What local resource limits should be assumed for V2 scale testing?
```

When resolved, move the answer into the appropriate permanent section and remove the question.

---

# 27. Session Handoff

## Last Session Summary

Completed Day 16. The repository now includes a Spark Structured Streaming Kafka consumer, explicit version-1 Spark schema/validation, HDFS checkpoints, bounded triggers, structured metrics, safe invalid-record quarantine, and a container runbook. See `docs/DAY16_VALIDATION.md` and `streaming/README.md`.

Populated `BankFlow` using `docs/` as the canonical documentation root and `src/bankflow/` as the application package. Preserved 18 academic assets unchanged, normalized the architecture filename, and retained dated baseline reviews. Added environment template, pinned dependencies, Windows dependency snapshot, Python setup guide, import checker, and package/linter configuration.

## Last Known Working State

The `bankflow-atm==1.0.0` editable package and application dependencies import on Python 3.14.4. All 146 application tests pass with service opt-ins. Spark 3.5.1 consumed the Day 16 validation topic through the standalone master; HDFS checkpoint commits 0–2 prove restart progress, and the quarantine contains three safe invalid metadata records. The existing 67 dbt tests and five-task Airflow DAG remain the Version 1 analytics baseline.

## Last Completed Task

Day 16 Spark Structured Streaming foundation and live Kafka/HDFS validation. See `docs/DAY16_VALIDATION.md`.

## Next Task

Day 17: create the Iceberg Bronze layer from the validated Spark stream.

## Blockers

The dedicated container must be running for live PostgreSQL/Redis/Kafka/Airflow/dbt/Spark/HDFS validation. Before Day 17 writes data, inspect the Hive Metastore and Iceberg catalog configuration and confirm the intended `/bankflow/bronze` HDFS namespace.

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

> BankFlow is a fictional ATM portfolio project. Days 1–16 are complete: v1.0.0 provides the application/event platform, Day 15 adds deterministic high-volume events, and Day 16 adds checkpointed Spark 3.5.1 Kafka ingestion with explicit schemas, metrics, and secret-safe invalid quarantine in HDFS. All 117 service-free tests and all 146 tests with service opt-ins pass. Continue with Day 17 Iceberg Bronze using the released version-1 event contract and the Day 16 Spark stream as boundaries.
