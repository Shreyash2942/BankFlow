# Graph Report - .  (2026-09-30)

## Corpus Check
- 104 files · ~342,009 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 710 nodes · 1137 edges · 44 communities detected
- Extraction: 70% EXTRACTED · 29% INFERRED · 1% AMBIGUOUS · INFERRED: 330 edges (avg confidence: 0.66)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Transaction Service Code|Transaction Service Code]]
- [[_COMMUNITY_ORM Domain Models|ORM Domain Models]]
- [[_COMMUNITY_Academic Prototype Code|Academic Prototype Code]]
- [[_COMMUNITY_Repository Persistence|Repository Persistence]]
- [[_COMMUNITY_Foundation Validation|Foundation Validation]]
- [[_COMMUNITY_PIN Workflow Review|PIN Workflow Review]]
- [[_COMMUNITY_Authentication Architecture|Authentication Architecture]]
- [[_COMMUNITY_Transaction Engine Architecture|Transaction Engine Architecture]]
- [[_COMMUNITY_Database Infrastructure Tests|Database Infrastructure Tests]]
- [[_COMMUNITY_ATM Workflow Requirements|ATM Workflow Requirements]]
- [[_COMMUNITY_UML Sequence Diagrams|UML Sequence Diagrams]]
- [[_COMMUNITY_UML Activity Review|UML Activity Review]]
- [[_COMMUNITY_Day 6 Evidence and Handoff|Day 6 Evidence and Handoff]]
- [[_COMMUNITY_ATM State Machine Behavior|ATM State Machine Behavior]]
- [[_COMMUNITY_UML State Diagram|UML State Diagram]]
- [[_COMMUNITY_Database Provisioning|Database Provisioning]]
- [[_COMMUNITY_State Diagram Details|State Diagram Details]]
- [[_COMMUNITY_Project Design Rationale|Project Design Rationale]]
- [[_COMMUNITY_Withdrawal Activity Details|Withdrawal Activity Details]]
- [[_COMMUNITY_Legacy Retry Scenario|Legacy Retry Scenario]]
- [[_COMMUNITY_Foundation Architecture|Foundation Architecture]]
- [[_COMMUNITY_Legacy Success Scenario|Legacy Success Scenario]]
- [[_COMMUNITY_Settings Tests|Settings Tests]]
- [[_COMMUNITY_Domain Model ADR|Domain Model ADR]]
- [[_COMMUNITY_Repository Boundary ADR|Repository Boundary ADR]]
- [[_COMMUNITY_Lakehouse Roadmap|Lakehouse Roadmap]]
- [[_COMMUNITY_Initial Schema Migration|Initial Schema Migration]]
- [[_COMMUNITY_Environment Import Check|Environment Import Check]]
- [[_COMMUNITY_Domain Metadata Tests|Domain Metadata Tests]]
- [[_COMMUNITY_Activity Diagram Swimlanes|Activity Diagram Swimlanes]]
- [[_COMMUNITY_Diagram Swimlane Duplicate|Diagram Swimlane Duplicate]]
- [[_COMMUNITY_Test Environment Isolation|Test Environment Isolation]]
- [[_COMMUNITY_Kafka Deferral Decision|Kafka Deferral Decision]]
- [[_COMMUNITY_Development Tooling|Development Tooling]]
- [[_COMMUNITY_Python Dependency Lock|Python Dependency Lock]]
- [[_COMMUNITY_UI Lockout Conflict|UI Lockout Conflict]]
- [[_COMMUNITY_Database Isolation|Database Isolation]]
- [[_COMMUNITY_Redis Database Isolation|Redis Database Isolation]]
- [[_COMMUNITY_Fictional Data Scope|Fictional Data Scope]]
- [[_COMMUNITY_Event Secret Exclusion|Event Secret Exclusion]]
- [[_COMMUNITY_Kafka Validation Gap|Kafka Validation Gap]]
- [[_COMMUNITY_Dedicated Container Decision|Dedicated Container Decision]]
- [[_COMMUNITY_Session End Node|Session End Node]]
- [[_COMMUNITY_Duplicate Session End Node|Duplicate Session End Node]]

## God Nodes (most connected - your core abstractions)
1. `Shared utility functions.` - 43 edges
2. `TransactionService` - 21 edges
3. `Account` - 20 edges
4. `AuditEvent` - 17 edges
5. `Transaction` - 17 edges
6. `AccountRepository` - 17 edges
7. `RepositoryNotFoundError` - 17 edges
8. `ATM` - 17 edges
9. `Card` - 16 edges
10. `session_scope()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `Planned validated withdrawal workflow` --semantically_similar_to--> `request_withdrawal()`  [INFERRED] [semantically similar]
  docs/PRODUCT_REQUIREMENTS.md → docs/original-college-project/atm_simulation.py
- `Restrictive Financial History with Durable Audit Rows` --conceptually_related_to--> `Secret-Free Authentication Audit Events`  [INFERRED]
  docs/DAY3_VALIDATION.md → src/bankflow/services/auth_service.py
- `PostgreSQL Transactional Source Of Truth` --conceptually_related_to--> `Caller-Owned Service Unit Of Work`  [INFERRED]
  docs/ARCHITECTURE.md → src/bankflow/services/transaction_service.py
- `Scenario 2: Incorrect PIN then successful authentication` --illustrates_legacy_behavior--> `authenticate_customer()`  [INFERRED]
  docs/original-college-project/ATM_Execution_Screenshots/incorrect_then_correct_pin.png → docs/original-college-project/atm_simulation.py
- `Scenario 1: Successful withdrawal` --illustrates_legacy_behavior--> `run_atm()`  [INFERRED]
  docs/original-college-project/ATM_Execution_Screenshots/successful_withdrawal.png → docs/original-college-project/atm_simulation.py

## Hyperedges (group relationships)
- **Transactional Card Authentication Flow** — authentication_request_contract, authentication_service, card_row_lock_lookup, constant_time_pin_verification, authentication_state_store, authentication_result_contract [EXTRACTED 1.00]
- **Opted-in migration reversal is isolated from application data by credentials, role grants and database guards** — day2_test_database, day2_test_guard, day2_role_isolation, day2_migration_validation, day2_app_protection [EXTRACTED 1.00]
- **Academic requirements/model/code/execution traceability** — academic_trace, uml_state, uml_activity, uml_sequence, prototype, manual_scenarios [EXTRACTED 1.00]
- **Schema bootstrap keeps migration bookkeeping independent while refusing destructive cascade** — migration, day2_schema, day2_public_version, day2_bootstrap_rationale, day2_no_cascade [EXTRACTED 1.00]
- **BankFlow Authentication State Flow** — bankflow_authentication_service, postgresql_system_of_record, redis_temporary_operational_state, durable_card_lockout, expiring_failed_attempt_counter, opaque_hashed_session_token, secret_free_authentication_audit [EXTRACTED 1.00]
- **Academic ATM Requirements-to-Evidence Traceability Chain** — secure_withdrawal_workflow, three_complementary_uml_views, numbered_artifact_traceability, four_atm_execution_scenarios [EXTRACTED 1.00]
- **Exact Money Validation Flow** — positive_money_contract, withdrawal_request_contract, deposit_request_contract, schema_accepts_positive_decimal_cents_test, schema_rejects_unsafe_money_test, day6_exact_money_acceptance, adr007_legacy_money_defect_rationale [EXTRACTED 1.00]
- **Locked Atomic Financial Operation Flow** — authorized_account_resolution, account_row_locking, withdrawal_workflow, deposit_workflow, persisted_transaction_record, audit_event_append, caller_owned_service_uow, transaction_failure_rollback_test [EXTRACTED 1.00]
- **Day 6 Service Completion To Day 7 UI Flow** — memory_day6_complete_status, day6_validation_evidence, memory_day6_to_day7_handoff, task_day7_streamlit_objective, adr007_strict_decimal_ui_consequence [EXTRACTED 1.00]

## Communities

### Community 0 - "Transaction Service Code"
Cohesion: 0.11
Nodes (41): AccountBalance, A consistent balance snapshot and its persisted inquiry transaction., AccountAuthorizationError, AccountService, AccountUnavailableError, BankingServiceError, Authorized account lookup and persisted balance inquiry., Base exception for stable transaction-service failures. (+33 more)

### Community 1 - "ORM Domain Models"
Cohesion: 0.1
Nodes (33): Account, Account-operation responses exposed by the service layer., AuditEvent, Append-oriented operational audit record with secret-free structured details., Base, Base, Shared ORM metadata for BankFlow's application schema., Card (+25 more)

### Community 2 - "Academic Prototype Code"
Cohesion: 0.04
Nodes (52): Academic simulation is not production banking security, Numbered UML activities traced to executable output, Academic zero-balance closure behavior, authenticate_customer(), print_step(), ATM Simulation CSC505 - Principles of Software Engineering  This program follows, Print a numbered activity that matches the UML Activity Diagram., Authenticate the customer using a PIN with a maximum of three attempts. (+44 more)

### Community 3 - "Repository Persistence"
Cohesion: 0.09
Nodes (28): AccountRepository, Account lookups and exact-balance persistence., Persist account state while the caller owns commit and rollback., CustomerRepository, Customer persistence queries., Read customers without owning the surrounding transaction., ConcurrentUpdateError, InvalidRepositoryQueryError (+20 more)

### Community 4 - "Foundation Validation"
Cohesion: 0.05
Nodes (48): Day 1 import, lint, hash and CLI checks, Initial admin-role setup attempt could not create roles; no database resources created, Migration downgrade must never run against application database, Autogeneration inspects bankflow schema; future models require metadata registration, Base metadata targets bankflow with stable constraint names, Migration bookkeeping must survive application-schema bootstrap and downgrade, Pytest configured for concise tracebacks after connection-argument exposure, Bounded connection pool, timeout, pre-ping and hidden SQL parameters (+40 more)

### Community 5 - "PIN Workflow Review"
Cohesion: 0.07
Nodes (46): Academic PIN check and three-failure session rejection, Start ATM Session, Activity arrow routing disagrees with numbered PIN and bank balance flow, Increment Failed Attempt Counter, Authenticate Customer, Bank Check Balance, PIN correct decision, Enter PIN (+38 more)

### Community 6 - "Authentication Architecture"
Cohesion: 0.06
Nodes (45): ADR-006 Split Authentication State by Durability, Four-ASCII-Digit PIN Contract, Authentication Outcome Vocabulary, Secret-Safe Authentication Request Contract, Secret-Safe Authentication Result Contract, Transactional Authentication Service, Identifier-Only Authentication Session Payload, Redis Authentication State Store (+37 more)

### Community 7 - "Transaction Engine Architecture"
Cohesion: 0.07
Nodes (42): Account Authorization Error, Account Balance Snapshot Contract, Account Row Locking For Consistent Operations, Account Unavailable Error, Audit Rows Share The Database Transaction, Caller-Owned SQLAlchemy Transaction Decision, Persist Declined Insufficient-Funds Attempts, PostgreSQL Transactional Source Of Truth (+34 more)

### Community 8 - "Database Infrastructure Tests"
Cohesion: 0.08
Nodes (24): downgrade(), create core banking domain models  Revision ID: 0002 Revises: 0001, upgrade(), database_engine(), migrated_database(), create_database_engine(), Lazy SQLAlchemy engine construction; the caller owns engine disposal., Create a pool without opening a connection until first use. (+16 more)

### Community 9 - "ATM Workflow Requirements"
Cohesion: 0.08
Nodes (32): ATM System, Attempts >= 3?, Authenticate Customer: access granted, Bank / Account System, Bank checks sufficient funds, Debit Amount from Account, Check Account Balance, Close Account at zero balance (+24 more)

### Community 10 - "UML Sequence Diagrams"
Cohesion: 0.09
Nodes (28): Numbered activity panel, Sequence ATM lifeline, Authenticated / show menu, Check available account balance, Sequence Bank System lifeline, Dispense Cash after debit success, Check Balance, Account Closed for zero balance (+20 more)

### Community 11 - "UML Activity Review"
Cohesion: 0.1
Nodes (23): Activity arrow routing disagrees with numbered PIN and bank balance flow, Increment Failed Attempt Counter, Authenticate Customer, Bank Check Balance, Bank debit amount from account, Check Account Balance, Close Account automatically at zero balance, Display Transaction Complete / Updated Balance (+15 more)

### Community 12 - "Day 6 Evidence and Handoff"
Cohesion: 0.1
Nodes (21): ADR-007 Exact And Atomic Service Boundary, Correct Legacy Float And Fractional-Cent Defects, Day 7 Must Convert UI Values Deliberately, Service Repository And UI Separation, Streamlit Interaction-Only Responsibility, Day 6 Transaction Engine Changelog, Day 6 Exact Money Acceptance, Day 6 Transaction Engine Validation Evidence (+13 more)

### Community 13 - "ATM State Machine Behavior"
Cohesion: 0.15
Nodes (18): Authenticated: showMenu, Check Balance: validateAmount, Account Closed: displayClosedMsg, Transaction Complete, Final State, PIN format validation, Idle: displayWelcome / clearScreen, Increment Attempts: incrementCounter (+10 more)

### Community 14 - "UML State Diagram"
Cohesion: 0.15
Nodes (17): Account Active / transaction complete, Authenticated Customer, Check Balance, Account Closed, ATM UML State Machine Diagram, Eject Card, Final State / End of Session, Idle / waiting for card (+9 more)

### Community 15 - "Database Provisioning"
Cohesion: 0.23
Nodes (14): admin_sql(), main(), provision(), Provision or rotate local Day 2 database access without resetting data., Render one local environment file without exposing its password., Replace exactly one setting while preserving every other local choice., Rotate both owner passwords and atomically replace their ignored files., render_environment() (+6 more)

### Community 16 - "State Diagram Details"
Cohesion: 0.19
Nodes (14): Account Active: transaction complete; display new balance, Authenticated: showMenu, Check Balance after withdrawal, Account Closed: display closed message, Final State: end of session, Idle: waiting for card; display welcome, Increment Attempts: increase failed attempt counter, Initial State (+6 more)

### Community 17 - "Project Design Rationale"
Cohesion: 0.18
Nodes (11): ATM System Design and Implementation Report, Classroom-to-Production ATM Security Gap, Four ATM Execution Scenarios, Numbered Design-to-Execution Traceability, Waterfall Prototyping and Agile Tradeoffs, Requirements Before Implementation, Authenticated ATM Withdrawal Workflow, Security Across the Software Lifecycle (+3 more)

### Community 18 - "Withdrawal Activity Details"
Cohesion: 0.2
Nodes (11): Bank debit amount from account, Check Account Balance, Close Account automatically at zero balance, Display Transaction Complete / Updated Balance, Dispense Cash, Amount <= Balance decision, Display Insufficient Funds Message, Request Withdrawal Amount (+3 more)

### Community 19 - "Legacy Retry Scenario"
Cohesion: 0.18
Nodes (11): Account status ACTIVE, Authenticate Customer: access granted, Starting balance $500.00, Cash dispensed $100.00, Correct PIN 2468 on third input, End ATM Session and remove card, Incorrect PIN 1111: failed attempts 1/3, Updated balance $400.00 (+3 more)

### Community 20 - "Foundation Architecture"
Cohesion: 0.22
Nodes (9): ADR-001 Repository and Runtime Foundation, BankFlow Service Endpoint Reference, Dedicated BankFlow Data-Lab Container, Host and Container Network Boundary, Installable src/bankflow Package Layout, Legacy ATM Prototype Limitations, Original Academic ATM Archive, Preserved Academic Source Provenance (+1 more)

### Community 21 - "Legacy Success Scenario"
Cohesion: 0.22
Nodes (9): Account status ACTIVE, Authenticate Customer: access granted, Starting balance $500.00, Cash dispensed $100.00, Correct PIN 2468 on first input, End ATM Session and remove card, Updated balance $400.00, Scenario 1: Successful withdrawal (+1 more)

### Community 22 - "Settings Tests"
Cohesion: 0.25
Nodes (0): 

### Community 23 - "Domain Model ADR"
Cohesion: 0.29
Nodes (7): ADR-004 Exact and Traceable Banking Domain Model, Application-Generated UUID Identity, Exact NUMERIC and Decimal Money Policy, Restrictive Financial History Retention, Avoid Academic Prototype Floating-Point Defects, Idempotent Fixed Demo Seed, Tokenized Card and Salted PIN-Hash Persistence

### Community 24 - "Repository Boundary ADR"
Cohesion: 0.4
Nodes (6): ADR-005 Session-Bound Repository Boundary, Repository Preparation for Atomic Transactions, Caller-Owned Database Unit of Work, Account Row Lock and Version Check, Stable Repository Exceptions, Stable Newest-First Transaction History

### Community 25 - "Lakehouse Roadmap"
Cohesion: 0.4
Nodes (5): Planned immutable Iceberg Bronze events, Planned Gold business metrics, Planned standardized Silver datasets, Planned synthetic event generator, Planned V2 streaming lakehouse

### Community 26 - "Initial Schema Migration"
Cohesion: 0.5
Nodes (1): Create the application schema; domain tables follow in Day 3.  Revision ID: 0001

### Community 27 - "Environment Import Check"
Cohesion: 0.5
Nodes (3): main(), Check Day 1 imports without opening network connections or loading secrets., Return nonzero if the selected interpreter or an application import fails.

### Community 28 - "Domain Metadata Tests"
Cohesion: 0.5
Nodes (0): 

### Community 29 - "Activity Diagram Swimlanes"
Cohesion: 0.5
Nodes (4): ATM System swimlane, Bank / Account System swimlane, Customer swimlane, Numbered ATM UML activity diagram

### Community 30 - "Diagram Swimlane Duplicate"
Cohesion: 0.5
Nodes (4): ATM System swimlane, Bank / Account System swimlane, Customer swimlane, Numbered ATM UML activity diagram

### Community 31 - "Test Environment Isolation"
Cohesion: 0.67
Nodes (1): Keep external environment overrides from changing test database selection.

### Community 32 - "Kafka Deferral Decision"
Cohesion: 0.67
Nodes (3): Kafka Follows Day 8 Contract And Day 9 Integration, Database Completion Before Event Publication, Day 6 Kafka Deferral

### Community 33 - "Development Tooling"
Cohesion: 1.0
Nodes (1): pytest and Ruff development tooling

### Community 34 - "Python Dependency Lock"
Cohesion: 1.0
Nodes (1): Windows Python 3.14 dependency snapshot

### Community 35 - "UI Lockout Conflict"
Cohesion: 1.0
Nodes (1): Temporary card lockout in UI design

### Community 36 - "Database Isolation"
Cohesion: 1.0
Nodes (1): Isolated Application and Test Databases

### Community 37 - "Redis Database Isolation"
Cohesion: 1.0
Nodes (1): Redis Application and Integration-Test Database Isolation

### Community 38 - "Fictional Data Scope"
Cohesion: 1.0
Nodes (1): Educational fictional data only

### Community 39 - "Event Secret Exclusion"
Cohesion: 1.0
Nodes (1): PINs and hashes excluded from events

### Community 40 - "Kafka Validation Gap"
Cohesion: 1.0
Nodes (1): Kafka Broker Metadata Validation Gap

### Community 41 - "Dedicated Container Decision"
Cohesion: 1.0
Nodes (1): Dedicated user-provided lab container replaces shared lab

### Community 42 - "Session End Node"
Cohesion: 1.0
Nodes (1): End ATM Session

### Community 43 - "Duplicate Session End Node"
Cohesion: 1.0
Nodes (1): End ATM Session

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

## Knowledge Gaps
- **188 isolated node(s):** `ATM Simulation CSC505 - Principles of Software Engineering  This program follows`, `Print a numbered activity that matches the UML Activity Diagram.`, `Authenticate the customer using a PIN with a maximum of three attempts.`, `Request and validate a withdrawal amount.`, `Run one complete ATM session.` (+183 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Development Tooling`** (1 nodes): `pytest and Ruff development tooling`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Python Dependency Lock`** (1 nodes): `Windows Python 3.14 dependency snapshot`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `UI Lockout Conflict`** (1 nodes): `Temporary card lockout in UI design`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Database Isolation`** (1 nodes): `Isolated Application and Test Databases`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Redis Database Isolation`** (1 nodes): `Redis Application and Integration-Test Database Isolation`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Fictional Data Scope`** (1 nodes): `Educational fictional data only`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Event Secret Exclusion`** (1 nodes): `PINs and hashes excluded from events`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Kafka Validation Gap`** (1 nodes): `Kafka Broker Metadata Validation Gap`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dedicated Container Decision`** (1 nodes): `Dedicated user-provided lab container replaces shared lab`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Session End Node`** (1 nodes): `End ATM Session`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Duplicate Session End Node`** (1 nodes): `End ATM Session`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

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