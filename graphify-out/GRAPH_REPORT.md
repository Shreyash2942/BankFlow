# Graph Report - BankFlow  (2026-09-28)

## Day 4 completion update

BankFlow now has session-bound customer, account, card, and transaction repositories. Typed lookups, deterministic history, bounded pagination, versioned row-locked balance updates, transaction creation, and persistence exceptions are verified by 26 tests, including 11 live PostgreSQL checks. Day 5 authentication and Redis remain planned.

Local credential values are excluded from the graph. Actual agent token usage and billing are unavailable; unknown is not zero.

## Corpus Check
- 85 files · ~40,959 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 728 nodes · 1210 edges · 56 communities detected
- Extraction: 78% EXTRACTED · 21% INFERRED · 1% AMBIGUOUS · INFERRED: 256 edges (avg confidence: 0.79)
- Actual token usage and financial cost: unavailable; not zero. See `cost.json`.

## Community Hubs (Navigation)
- [Database and Seed Code](graph.html)
- [Repository Implementation](graph.html)
- [Domain Model and SQLAlchemy](graph.html)
- [Academic Prototype Correctness](graph.html)
- [ATM Transaction Flow](graph.html)
- [Database Foundation Validation](graph.html)
- [Planned BankFlow Platform](graph.html)
- [Python Package Foundation](graph.html)
- [Composite UML Flow](graph.html)
- [Generated Activity Flow One](graph.html)
- [Generated Activity Flow Two](graph.html)
- [Environment and Dependencies](graph.html)
- [Repository Contract](graph.html)
- [Local Database Provisioning](graph.html)
- [Detailed State Machine](graph.html)
- [Numbered Transaction Flow](graph.html)
- [State Machine Transitions](graph.html)
- [Core Banking Domain Model](graph.html)
- [Alternate State Machine](graph.html)
- [PIN Retry Screenshot](graph.html)
- [Environment Import Checker](graph.html)
- [Repository Module Imports](graph.html)
- [Activity Diagram Swimlanes](graph.html)
- [Alternate Activity Swimlanes](graph.html)
- [Card Lockout Policy](graph.html)
- [Event Secret Exclusion](graph.html)
- [Published Service Ports](graph.html)
- [SQLAlchemy URL Construction](graph.html)
- [Unconnected Session End One](graph.html)
- [Unconnected Session End Two](graph.html)
- [Python Runtime](graph.html)
- [Dependency Snapshot](graph.html)
- [Development Tooling](graph.html)
- [Archived Academic Assets](graph.html)
- [Dated Baseline Analysis](graph.html)
- [Unreleased Foundation](graph.html)
- [Docker Availability](graph.html)
- [Database Access Verification](graph.html)
- [Separate Tool Runtimes](graph.html)
- [Planned Exact Money](graph.html)
- [Planned Atomic Transactions](graph.html)
- [Open Lockout Policy](graph.html)
- [Legacy NaN Defect](graph.html)
- [Legacy Precision Defect](graph.html)
- [Pending Precision Policy](graph.html)
- [Legacy Retry Conflict](graph.html)
- [Kafka Failure Risk](graph.html)
- [Future Outbox Option](graph.html)
- [Streamlit Session Risk](graph.html)
- [Container Runtime Volume](graph.html)
- [Repository Bind Mount](graph.html)
- [Container Python Runtime](graph.html)
- [Pending Service Authentication](graph.html)
- [Provisioning Recovery](graph.html)
- [Superseded Day 3 Plan](graph.html)
- [Credential Rotation Recovery](graph.html)

## God Nodes (most connected - your core abstractions)
1. `BankFlow utils layer; implementation follows the task plan.` - 33 edges
2. `Account` - 21 edges
3. `RepositoryNotFoundError` - 21 edges
4. `Sqlalchemy` - 20 edges
5. `Transaction` - 18 edges
6. `ATM` - 17 edges
7. `AuditEvent` - 16 edges
8. `Card` - 16 edges
9. `AccountRepository` - 16 edges
10. `Bank System` - 15 edges

## Surprising Connections (you probably didn't know these)

- `Account Repository` --implemented_by--> `AccountRepository`  [INFERRED 0.98]
  Day 4 validation evidence → `src/bankflow/repositories/account_repository.py`
- `Versioned Balance Update` --implemented_by--> `.update_balance()`  [INFERRED 0.98]
  Row locking and model versioning meet at the repository boundary.
- `Transaction Creation with Flush` --implemented_by--> `.create()`  [INFERRED 0.98]
  Flush exposes constraint failures while the caller retains commit and rollback ownership.
- `23 passing tests including eight live PostgreSQL tests` --includes--> `test_tables_relationships_timestamps_and_decimal_round_trip()`  [INFERRED]
  docs/DAY3_VALIDATION.md → tests\integration\test_models.py
- `Planned validated withdrawal workflow` --semantically_similar_to--> `request_withdrawal()`  [INFERRED] [semantically similar]
  docs/PRODUCT_REQUIREMENTS.md → docs/original-college-project/atm_simulation.py
- `Account model with exact balance` --implemented_by--> `Account`  [INFERRED]
  docs/DAY3_VALIDATION.md → src\bankflow\models\account.py
- `Transaction model with balance snapshots` --implemented_by--> `Transaction`  [INFERRED]
  docs/DAY3_VALIDATION.md → src\bankflow\models\transaction.py
- `Alembic revision 0002` --implemented_by--> `upgrade()`  [INFERRED]
  docs/DAY3_VALIDATION.md → migrations\versions\0002_create_core_banking_domain_models.py

## Hyperedges (group relationships)
- **Academic requirements/model/code/execution traceability** — academic_trace, uml_state, uml_activity, uml_sequence, prototype, manual_scenarios [EXTRACTED 1.00]
- **Validated Day 1 Windows package environment** — package, python314, pins, lock, day1checks [EXTRACTED 1.00]
- **Planned transaction correctness contract** — txn, money, atomic, postgres [EXTRACTED 1.00]
- **Unresolved lockout lifecycle** — auth, temporary, persistent, lock_conflict [EXTRACTED 1.00]
- **Opted-in migration reversal is isolated from application data by credentials, role grants and database guards** — day2_test_database, day2_test_guard, day2_role_isolation, day2_migration_validation, day2_app_protection [EXTRACTED 1.00]
- **Schema bootstrap keeps migration bookkeeping independent while refusing destructive cascade** — migration, day2_schema, day2_public_version, day2_bootstrap_rationale, day2_no_cascade [EXTRACTED 1.00]
- **Day 3 exact and traceable persistence contract** — day3_domain_model, day3_exact_money, day3_financial_fks, day3_audit_retention, day3_migration_0002, day3_tests_23 [EXTRACTED 1.00]
- **Day 4 Repository Family** — day4_customer_repository, day4_account_repository, day4_card_repository, day4_transaction_repository [EXTRACTED 1.00]
- **Concurrency-Safe Balance Write** — day4_versioned_balance_update, day4_postgresql_row_lock, day4_stable_repository_exceptions, day4_caller_owned_unit_of_work [INFERRED 0.88]
- **Preparation for Atomic Transactions** — day4_caller_owned_unit_of_work, day4_versioned_balance_update, day4_transaction_creation_flush, day4_transaction_repository [INFERRED 0.86]

## Communities

### Community 0 - "Database and Seed Code"
Cohesion: 0.04
Nodes (71): Create the application schema; domain tables follow in Day 3.  Revision ID: 0001, downgrade(), create core banking domain models  Revision ID: 0002 Revises: 0001, upgrade(), Alembic, Alembic Config, Alembic Util, Argparse (+63 more)

### Community 1 - "Repository Implementation"
Cohesion: 0.05
Nodes (41): AccountRepository, Account lookups and exact-balance persistence., Persist account state while the caller owns commit and rollback., Bankflow Repositories, CardRepository, Card lookup queries for later authentication services., Read fictional card credentials without owning a transaction., Collections Abc (+33 more)

### Community 2 - "Domain Model and SQLAlchemy"
Cohesion: 0.08
Nodes (56): Account, Persistent customer account and exact available balance., AuditEvent, Append-oriented operational audit record with secret-free structured details., Bankflow Database Base, Bankflow Models, Bankflow Models Account, Bankflow Models Audit Event (+48 more)

### Community 3 - "Academic Prototype Correctness"
Cohesion: 0.04
Nodes (53): Academic simulation is not production banking security, Numbered UML activities traced to executable output, Academic zero-balance closure behavior, authenticate_customer(), print_step(), ATM Simulation CSC505 - Principles of Software Engineering  This program follows, Print a numbered activity that matches the UML Activity Diagram., Authenticate the customer using a PIN with a maximum of three attempts. (+45 more)

### Community 4 - "ATM Transaction Flow"
Cohesion: 0.07
Nodes (47): Academic PIN check and three-failure session rejection, Check Account Balance, Close Account at zero balance, Display Transaction Complete / Updated Balance, Dispense Cash, End ATM Session: remove card, Amount <= Balance?, Enter Withdrawal Amount (+39 more)

### Community 5 - "Database Foundation Validation"
Cohesion: 0.06
Nodes (36): Day 2 configuration and PostgreSQL foundation complete, Initial admin-role setup attempt could not create roles; no database resources created, Migration downgrade must never run against application database, Autogeneration inspects bankflow schema; future models require metadata registration, Base metadata targets bankflow with stable constraint names, Migration bookkeeping must survive application-schema bootstrap and downgrade, Pytest configured for concise tracebacks after connection-argument exposure, Settings and health/migration errors hide credentials and raw driver details (+28 more)

### Community 6 - "Planned BankFlow Platform"
Cohesion: 0.1
Nodes (35): Planned account service, Planned Airflow orchestration, Planned three-attempt PIN lockout, Planned authentication service, BankFlow: implemented database foundation, planned ATM platform, Planned immutable Iceberg Bronze events, Planned Python Kafka consumer, Planned Streamlit analytics (+27 more)

### Community 7 - "Python Package Foundation"
Cohesion: 0.06
Nodes (33): Proposed /bankflow/bronze and /bankflow/silver paths not created, Five canonical documents in docs/, Copied helper defaults /medilake/bronze and /medilake/silver, Dedicated bankflow container: running, Day 1 foundation complete, Editable install avoids manual PYTHONPATH, Windows host application uses dedicated container published ports, bankflow-atm distribution / bankflow import (+25 more)

### Community 8 - "Composite UML Flow"
Cohesion: 0.09
Nodes (28): Numbered activity panel, Sequence ATM lifeline, Authenticated / show menu, Check available account balance, Sequence Bank System lifeline, Dispense Cash after debit success, Check Balance, Account Closed for zero balance (+20 more)

### Community 9 - "Generated Activity Flow One"
Cohesion: 0.09
Nodes (26): Activity arrow routing disagrees with numbered PIN and bank balance flow, Increment Failed Attempt Counter, Authenticate Customer, Bank Check Balance, Bank debit amount from account, Check Account Balance, Close Account automatically at zero balance, Display Transaction Complete / Updated Balance (+18 more)

### Community 10 - "Generated Activity Flow Two"
Cohesion: 0.1
Nodes (22): Activity arrow routing disagrees with numbered PIN and bank balance flow, Increment Failed Attempt Counter, Authenticate Customer, Bank Check Balance, Bank debit amount from account, Check Account Balance, Close Account automatically at zero balance, Display Transaction Complete / Updated Balance (+14 more)

### Community 11 - "Environment and Dependencies"
Cohesion: 0.13
Nodes (20): Day 1 import, lint, hash and CLI checks, Bounded connection pool, timeout, pre-ping and hidden SQL parameters, Explicit engine creation/disposal and no connections during imports, Alembic dependency installed, Confluent Kafka client dependency installed, Psycopg dependency installed, Pydantic dependency installed, Pydantic Settings dependency installed (+12 more)

### Community 12 - "Repository Contract"
Cohesion: 0.18
Nodes (20): Account Repository, Bounded Repository Pagination, Caller-Owned Unit of Work, Card Repository, Customer Repository, Database Constraint Boundary, Deterministic Transaction History, Exact Decimal Money Inputs (+12 more)

### Community 13 - "Local Database Provisioning"
Cohesion: 0.16
Nodes (18): Json, admin_sql(), main(), provision(), Provision or rotate local Day 2 database access without resetting data., Render one local environment file without exposing its password., Replace exactly one setting while preserving every other local choice., Rotate both owner passwords and atomically replace their ignored files. (+10 more)

### Community 14 - "Detailed State Machine"
Cohesion: 0.15
Nodes (18): Authenticated: showMenu, Check Balance: validateAmount, Account Closed: displayClosedMsg, Transaction Complete, Final State, PIN format validation, Idle: displayWelcome / clearScreen, Increment Attempts: incrementCounter (+10 more)

### Community 15 - "Numbered Transaction Flow"
Cohesion: 0.14
Nodes (17): ATM System, Attempts >= 3?, Authenticate Customer: access granted, Bank / Account System, Bank checks sufficient funds, Debit Amount from Account, Customer, Enter PIN using keypad (+9 more)

### Community 16 - "State Machine Transitions"
Cohesion: 0.15
Nodes (17): Account Active / transaction complete, Authenticated Customer, Check Balance, Account Closed, ATM UML State Machine Diagram, Eject Card, Final State / End of Session, Idle / waiting for card (+9 more)

### Community 17 - "Core Banking Domain Model"
Cohesion: 0.15
Nodes (17): Account model with exact balance, Retained audit event model, Nullable SET NULL audit references, Fictional card token and PIN hash, Checked string status enums, Day 3 core domain persistence complete, Customer model, Day 4 repository layer handoff (+9 more)

### Community 18 - "Alternate State Machine"
Cohesion: 0.19
Nodes (14): Account Active: transaction complete; display new balance, Authenticated: showMenu, Check Balance after withdrawal, Account Closed: display closed message, Final State: end of session, Idle: waiting for card; display welcome, Increment Attempts: increase failed attempt counter, Initial State (+6 more)

### Community 19 - "PIN Retry Screenshot"
Cohesion: 0.18
Nodes (11): Account status ACTIVE, Authenticate Customer: access granted, Starting balance $500.00, Cash dispensed $100.00, Correct PIN 2468 on third input, End ATM Session and remove card, Incorrect PIN 1111: failed attempts 1/3, Updated balance $400.00 (+3 more)

### Community 20 - "Environment Import Checker"
Cohesion: 0.29
Nodes (6): main(), Check Day 1 imports without opening network connections or loading secrets., Return nonzero if the selected interpreter or an application import fails., Importlib, Importlib Metadata, Sys

### Community 21 - "Repository Module Imports"
Cohesion: 0.4
Nodes (4): Bankflow Repositories Account Repository, Bankflow Repositories Card Repository, Bankflow Repositories Customer Repository, Bankflow Repositories Transaction Repository

### Community 22 - "Activity Diagram Swimlanes"
Cohesion: 0.5
Nodes (4): ATM System swimlane, Bank / Account System swimlane, Customer swimlane, Numbered ATM UML activity diagram

### Community 23 - "Alternate Activity Swimlanes"
Cohesion: 0.5
Nodes (4): ATM System swimlane, Bank / Account System swimlane, Customer swimlane, Numbered ATM UML activity diagram

### Community 24 - "Card Lockout Policy"
Cohesion: 1.0
Nodes (2): Persistent PostgreSQL card lock in Day 5, Temporary card lockout in UI design

### Community 25 - "Event Secret Exclusion"
Cohesion: 1.0
Nodes (2): PINs and hashes excluded from events, Planned bankflow.transaction.events topic

### Community 26 - "Published Service Ports"
Cohesion: 1.0
Nodes (2): Inside-container PostgreSQL 5432 / Redis 6379 / Kafka 9092, Published service mappings: 5433 / 6380 / 9093

### Community 27 - "SQLAlchemy URL Construction"
Cohesion: 1.0
Nodes (2): Build a URL without interpolating or manually escaping credentials., Settings Settings Database Url

### Community 28 - "Unconnected Session End One"
Cohesion: 1.0
Nodes (1): End ATM Session

### Community 29 - "Unconnected Session End Two"
Cohesion: 1.0
Nodes (1): End ATM Session

### Community 30 - "Python Runtime"
Cohesion: 1.0
Nodes (1): Python 3.14.4 Windows x64 application runtime

### Community 31 - "Dependency Snapshot"
Cohesion: 1.0
Nodes (1): Windows Python 3.14 dependency snapshot

### Community 32 - "Development Tooling"
Cohesion: 1.0
Nodes (1): pytest and Ruff development tooling

### Community 33 - "Archived Academic Assets"
Cohesion: 1.0
Nodes (1): 18 byte-preserved academic assets

### Community 34 - "Dated Baseline Analysis"
Cohesion: 1.0
Nodes (1): Baseline analysis is a dated snapshot

### Community 35 - "Unreleased Foundation"
Cohesion: 1.0
Nodes (1): Unreleased Day 2 foundation; no application release tag

### Community 36 - "Docker Availability"
Cohesion: 1.0
Nodes (1): Docker engine reachable

### Community 37 - "Database Access Verification"
Cohesion: 1.0
Nodes (1): Authenticated PostgreSQL access and isolated provisioning verified

### Community 38 - "Separate Tool Runtimes"
Cohesion: 1.0
Nodes (1): Airflow dbt Spark Graphify use separate runtimes

### Community 39 - "Planned Exact Money"
Cohesion: 1.0
Nodes (1): Planned Decimal and exact numeric money

### Community 40 - "Planned Atomic Transactions"
Cohesion: 1.0
Nodes (1): Planned atomic balance and transaction write

### Community 41 - "Open Lockout Policy"
Cohesion: 1.0
Nodes (1): Open lock duration and reset policy

### Community 42 - "Legacy NaN Defect"
Cohesion: 1.0
Nodes (1): Legacy bug: NaN corrupts balance

### Community 43 - "Legacy Precision Defect"
Cohesion: 1.0
Nodes (1): Legacy bug: fractional cents accepted

### Community 44 - "Pending Precision Policy"
Cohesion: 1.0
Nodes (1): Finite Decimal and precision policy pending

### Community 45 - "Legacy Retry Conflict"
Cohesion: 1.0
Nodes (1): Legacy UML retry retain/eject ordering conflicts

### Community 46 - "Kafka Failure Risk"
Cohesion: 1.0
Nodes (1): Database success / Kafka failure risk

### Community 47 - "Future Outbox Option"
Cohesion: 1.0
Nodes (1): Possible future outbox improvement

### Community 48 - "Streamlit Session Risk"
Cohesion: 1.0
Nodes (1): Streamlit rerun session risk

### Community 49 - "Container Runtime Volume"
Cohesion: 1.0
Nodes (1): Dedicated runtime volume datalab-runtime-bankflow at /home/datalab/runtime

### Community 50 - "Repository Bind Mount"
Cohesion: 1.0
Nodes (1): Repository bind mount at /home/datalab/bankflow changes host files

### Community 51 - "Container Python Runtime"
Cohesion: 1.0
Nodes (1): Container default Python 3.10.12; Windows virtual environment is not portable

### Community 52 - "Pending Service Authentication"
Cohesion: 1.0
Nodes (1): PostgreSQL authentication verified; Redis authentication and Kafka metadata still pending

### Community 53 - "Provisioning Recovery"
Cohesion: 1.0
Nodes (1): Partial provisioning failure retains generated local credentials for deliberate recovery

### Community 54 - "Superseded Day 3 Plan"
Cohesion: 1.0
Nodes (1): Day 3 planned exact numeric money, model migration and demo seed data

### Community 55 - "Credential Rotation Recovery"
Cohesion: 1.0
Nodes (1): Rotation changes passwords only; retain ignored .next files if post-update file replacement fails

## Ambiguous Edges - Review These
- `PIN Entry: prompt for PIN` → `Retry (attempts < 3) label without connected retry arrow`  [AMBIGUOUS]
  docs/original-college-project/ATM System - UML State Machine Diagram.jpg · relation: intended_retry_destination
- `Validate PIN` → `Activity arrow routing disagrees with numbered PIN and bank balance flow`  [AMBIGUOUS]
  docs/original-college-project/ChatGPT Image Aug 31, 2026, 07_45_29 PM.png · relation: flags_routing_ambiguity
- `Bank Check Balance` → `Activity arrow routing disagrees with numbered PIN and bank balance flow`  [AMBIGUOUS]
  docs/original-college-project/ChatGPT Image Aug 31, 2026, 07_45_29 PM.png · relation: flags_routing_ambiguity
- `Validate PIN` → `Activity arrow routing disagrees with numbered PIN and bank balance flow`  [AMBIGUOUS]
  docs/original-college-project/ChatGPT Image Aug 31, 2026, 07_47_23 PM.png · relation: flags_routing_ambiguity
- `Bank Check Balance` → `Activity arrow routing disagrees with numbered PIN and bank balance flow`  [AMBIGUOUS]
  docs/original-college-project/ChatGPT Image Aug 31, 2026, 07_47_23 PM.png · relation: flags_routing_ambiguity
- `Increment Attempts` → `Retry label and increment-to-final routing appear inconsistent`  [AMBIGUOUS]
  docs/original-college-project/ChatGPT Image Aug 31, 2026, 07_47_42 PM.png · relation: flags_routing_ambiguity
- `Numbered activity panel` → `Activity PIN failure branch reaches final node and retry guards are misrouted`  [AMBIGUOUS]
  docs/original-college-project/ChatGPT Image Aug 31, 2026, 07_56_47 PM.png · relation: flags_routing_ambiguity
- `Temporary card lockout in UI design` → `Persistent PostgreSQL card lock in Day 5`  [AMBIGUOUS]
  docs/analysis/DOCUMENT_REVIEW.md · relation: same_lock_policy_unclear

## Knowledge Gaps
- **191 isolated node(s):** `Check Day 1 imports without opening network connections or loading secrets.`, `Return nonzero if the selected interpreter or an application import fails.`, `importlib`, `importlib_metadata`, `sys` (+186 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Card Lockout Policy`** (2 nodes): `Persistent PostgreSQL card lock in Day 5`, `Temporary card lockout in UI design`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Event Secret Exclusion`** (2 nodes): `PINs and hashes excluded from events`, `Planned bankflow.transaction.events topic`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Published Service Ports`** (2 nodes): `Inside-container PostgreSQL 5432 / Redis 6379 / Kafka 9092`, `Published service mappings: 5433 / 6380 / 9093`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `SQLAlchemy URL Construction`** (2 nodes): `Build a URL without interpolating or manually escaping credentials.`, `Settings Settings Database Url`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Unconnected Session End One`** (1 nodes): `End ATM Session`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Unconnected Session End Two`** (1 nodes): `End ATM Session`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Python Runtime`** (1 nodes): `Python 3.14.4 Windows x64 application runtime`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dependency Snapshot`** (1 nodes): `Windows Python 3.14 dependency snapshot`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Development Tooling`** (1 nodes): `pytest and Ruff development tooling`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Archived Academic Assets`** (1 nodes): `18 byte-preserved academic assets`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dated Baseline Analysis`** (1 nodes): `Baseline analysis is a dated snapshot`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Unreleased Foundation`** (1 nodes): `Unreleased Day 2 foundation; no application release tag`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Docker Availability`** (1 nodes): `Docker engine reachable`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Database Access Verification`** (1 nodes): `Authenticated PostgreSQL access and isolated provisioning verified`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Separate Tool Runtimes`** (1 nodes): `Airflow dbt Spark Graphify use separate runtimes`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Planned Exact Money`** (1 nodes): `Planned Decimal and exact numeric money`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Planned Atomic Transactions`** (1 nodes): `Planned atomic balance and transaction write`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Open Lockout Policy`** (1 nodes): `Open lock duration and reset policy`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Legacy NaN Defect`** (1 nodes): `Legacy bug: NaN corrupts balance`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Legacy Precision Defect`** (1 nodes): `Legacy bug: fractional cents accepted`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Pending Precision Policy`** (1 nodes): `Finite Decimal and precision policy pending`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Legacy Retry Conflict`** (1 nodes): `Legacy UML retry retain/eject ordering conflicts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Kafka Failure Risk`** (1 nodes): `Database success / Kafka failure risk`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Future Outbox Option`** (1 nodes): `Possible future outbox improvement`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Streamlit Session Risk`** (1 nodes): `Streamlit rerun session risk`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Container Runtime Volume`** (1 nodes): `Dedicated runtime volume datalab-runtime-bankflow at /home/datalab/runtime`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Repository Bind Mount`** (1 nodes): `Repository bind mount at /home/datalab/bankflow changes host files`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Container Python Runtime`** (1 nodes): `Container default Python 3.10.12; Windows virtual environment is not portable`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Pending Service Authentication`** (1 nodes): `PostgreSQL authentication verified; Redis authentication and Kafka metadata still pending`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Provisioning Recovery`** (1 nodes): `Partial provisioning failure retains generated local credentials for deliberate recovery`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Superseded Day 3 Plan`** (1 nodes): `Day 3 planned exact numeric money, model migration and demo seed data`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Credential Rotation Recovery`** (1 nodes): `Rotation changes passwords only; retain ignored .next files if post-update file replacement fails`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **How do caller-owned sessions, row locks, version checks, and transaction flushes prepare the Day 6 atomic workflow?**
  _Connects the repository contract, implementation methods, domain versioning, and the next transaction-service milestone._
- **How do repository exceptions keep SQLAlchemy failures out of service code?**
  _Traces database constraints and ORM concurrency errors through the stable persistence boundary._
- **Why does transaction history order by both timestamp and UUID?**
  _Links PostgreSQL transaction timestamp behavior to deterministic pagination and its integration tests._
- **What is the exact relationship between `PIN Entry: prompt for PIN` and `Retry (attempts < 3) label without connected retry arrow`?**
  _Edge tagged AMBIGUOUS (relation: intended_retry_destination) - confidence is low._
- **What is the exact relationship between `Validate PIN` and `Activity arrow routing disagrees with numbered PIN and bank balance flow`?**
  _Edge tagged AMBIGUOUS (relation: flags_routing_ambiguity) - confidence is low._
- **What is the exact relationship between `Bank Check Balance` and `Activity arrow routing disagrees with numbered PIN and bank balance flow`?**
  _Edge tagged AMBIGUOUS (relation: flags_routing_ambiguity) - confidence is low._
- **What is the exact relationship between `Validate PIN` and `Activity arrow routing disagrees with numbered PIN and bank balance flow`?**
  _Edge tagged AMBIGUOUS (relation: flags_routing_ambiguity) - confidence is low._
- **What is the exact relationship between `Bank Check Balance` and `Activity arrow routing disagrees with numbered PIN and bank balance flow`?**
  _Edge tagged AMBIGUOUS (relation: flags_routing_ambiguity) - confidence is low._
- **What is the exact relationship between `Increment Attempts` and `Retry label and increment-to-final routing appear inconsistent`?**
  _Edge tagged AMBIGUOUS (relation: flags_routing_ambiguity) - confidence is low._
- **What is the exact relationship between `Numbered activity panel` and `Activity PIN failure branch reaches final node and retry guards are misrouted`?**
  _Edge tagged AMBIGUOUS (relation: flags_routing_ambiguity) - confidence is low._