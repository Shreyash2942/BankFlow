# Graph Report - .  (2026-10-01)

## Corpus Check
- 117 files · ~345,847 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 811 nodes · 1266 edges · 56 communities detected
- Extraction: 72% EXTRACTED · 28% INFERRED · 1% AMBIGUOUS · INFERRED: 349 edges (avg confidence: 0.67)
- Token cost: unavailable from agent execution; recorded as unknown, not zero

## Community Hubs (Navigation)
- [[_COMMUNITY_Academic ATM Code|Academic ATM Code]]
- [[_COMMUNITY_Core ORM Models|Core ORM Models]]
- [[_COMMUNITY_Account Service|Account Service]]
- [[_COMMUNITY_Repository Layer|Repository Layer]]
- [[_COMMUNITY_Foundation Validation Decisions|Foundation Validation Decisions]]
- [[_COMMUNITY_Streamlit Runtime and Demo Reset|Streamlit Runtime and Demo Reset]]
- [[_COMMUNITY_Authentication and Redis|Authentication and Redis]]
- [[_COMMUNITY_Transaction Service Design|Transaction Service Design]]
- [[_COMMUNITY_Streamlit Interface Architecture|Streamlit Interface Architecture]]
- [[_COMMUNITY_Alembic and Database Runtime|Alembic and Database Runtime]]
- [[_COMMUNITY_ATM Sequence Model|ATM Sequence Model]]
- [[_COMMUNITY_Academic Interaction Trace|Academic Interaction Trace]]
- [[_COMMUNITY_UML Sequence and Activity|UML Sequence and Activity]]
- [[_COMMUNITY_ATM Activity Model|ATM Activity Model]]
- [[_COMMUNITY_ATM Activity Diagram|ATM Activity Diagram]]
- [[_COMMUNITY_ATM State Machine Logic|ATM State Machine Logic]]
- [[_COMMUNITY_ATM State Diagram|ATM State Diagram]]
- [[_COMMUNITY_Database Provisioning|Database Provisioning]]
- [[_COMMUNITY_Demo Seed and UI Tests|Demo Seed and UI Tests]]
- [[_COMMUNITY_ATM State Model Details|ATM State Model Details]]
- [[_COMMUNITY_Demo Execution Scenario|Demo Execution Scenario]]
- [[_COMMUNITY_Academic Reports and Engineering Lessons|Academic Reports and Engineering Lessons]]
- [[_COMMUNITY_Foundation Architecture|Foundation Architecture]]
- [[_COMMUNITY_Settings Validation Tests|Settings Validation Tests]]
- [[_COMMUNITY_Domain Model Architecture|Domain Model Architecture]]
- [[_COMMUNITY_Exact Money UI Contracts|Exact Money UI Contracts]]
- [[_COMMUNITY_Repository Architecture|Repository Architecture]]
- [[_COMMUNITY_Transaction Schema Tests|Transaction Schema Tests]]
- [[_COMMUNITY_Planned Lakehouse|Planned Lakehouse]]
- [[_COMMUNITY_Schema Bootstrap Migration|Schema Bootstrap Migration]]
- [[_COMMUNITY_Environment Import Check|Environment Import Check]]
- [[_COMMUNITY_Model Metadata Tests|Model Metadata Tests]]
- [[_COMMUNITY_UML Activity Swimlanes|UML Activity Swimlanes]]
- [[_COMMUNITY_UML Swimlane Source|UML Swimlane Source]]
- [[_COMMUNITY_Test Settings Isolation|Test Settings Isolation]]
- [[_COMMUNITY_Kafka Sequencing|Kafka Sequencing]]
- [[_COMMUNITY_Transaction Engine Evidence|Transaction Engine Evidence]]
- [[_COMMUNITY_Withdrawal UI|Withdrawal UI]]
- [[_COMMUNITY_Deposit UI|Deposit UI]]
- [[_COMMUNITY_Layered UI Architecture|Layered UI Architecture]]
- [[_COMMUNITY_Welcome and Authentication UI|Welcome and Authentication UI]]
- [[_COMMUNITY_Account Dashboard UI|Account Dashboard UI]]
- [[_COMMUNITY_Transaction History UI|Transaction History UI]]
- [[_COMMUNITY_Demo Constants|Demo Constants]]
- [[_COMMUNITY_Development Tooling|Development Tooling]]
- [[_COMMUNITY_Dependency Snapshot|Dependency Snapshot]]
- [[_COMMUNITY_Lockout Design|Lockout Design]]
- [[_COMMUNITY_Database Isolation|Database Isolation]]
- [[_COMMUNITY_Redis Isolation|Redis Isolation]]
- [[_COMMUNITY_Fictional Data Policy|Fictional Data Policy]]
- [[_COMMUNITY_Event Secret Exclusion|Event Secret Exclusion]]
- [[_COMMUNITY_Kafka Connectivity Gap|Kafka Connectivity Gap]]
- [[_COMMUNITY_Dedicated Lab Container|Dedicated Lab Container]]
- [[_COMMUNITY_Session Termination Flow|Session Termination Flow]]
- [[_COMMUNITY_Session Termination Design|Session Termination Design]]
- [[_COMMUNITY_Day 5 Service Handoff|Day 5 Service Handoff]]

## God Nodes (most connected - your core abstractions)
1. `Streamlit-facing adapters; domain rules remain in application services.` - 44 edges
2. `Account` - 20 edges
3. `TransactionService` - 20 edges
4. `AuditEvent` - 17 edges
5. `Transaction` - 17 edges
6. `AccountRepository` - 17 edges
7. `RepositoryNotFoundError` - 17 edges
8. `ATM` - 17 edges
9. `Card` - 16 edges
10. `BankFlowRuntime` - 16 edges

## Surprising Connections (you probably didn't know these)
- `Planned validated withdrawal workflow` --semantically_similar_to--> `request_withdrawal()`  [INFERRED] [semantically similar]
  docs/PRODUCT_REQUIREMENTS.md → docs/original-college-project/atm_simulation.py
- `Restrictive Financial History with Durable Audit Rows` --conceptually_related_to--> `Secret-Free Authentication Audit Events`  [INFERRED]
  docs/DAY3_VALIDATION.md → src/bankflow/services/auth_service.py
- `PostgreSQL Transactional Source Of Truth` --conceptually_related_to--> `Caller-Owned Service Unit Of Work`  [INFERRED]
  docs/ARCHITECTURE.md → src/bankflow/services/transaction_service.py
- `Scenario 2: Incorrect PIN then successful authentication` --illustrates_legacy_behavior--> `authenticate_customer()`  [INFERRED]
  docs/original-college-project/ATM_Execution_Screenshots/incorrect_then_correct_pin.png → docs/original-college-project/atm_simulation.py
- `Alembic environment using the same validated settings as the application.` --uses--> `Base`  [INFERRED]
  migrations\env.py → src\bankflow\database\base.py

## Hyperedges (group relationships)
- **Transactional Card Authentication Flow** — authentication_request_contract, authentication_service, card_row_lock_lookup, constant_time_pin_verification, authentication_state_store, authentication_result_contract [EXTRACTED 1.00]
- **Opted-in migration reversal is isolated from application data by credentials, role grants and database guards** — day2_test_database, day2_test_guard, day2_role_isolation, day2_migration_validation, day2_app_protection [EXTRACTED 1.00]
- **Academic requirements/model/code/execution traceability** — academic_trace, uml_state, uml_activity, uml_sequence, prototype, manual_scenarios [EXTRACTED 1.00]
- **Schema bootstrap keeps migration bookkeeping independent while refusing destructive cascade** — migration, day2_schema, day2_public_version, day2_bootstrap_rationale, day2_no_cascade [EXTRACTED 1.00]
- **BankFlow Authentication State Flow** — bankflow_authentication_service, postgresql_system_of_record, redis_temporary_operational_state, durable_card_lockout, expiring_failed_attempt_counter, opaque_hashed_session_token, secret_free_authentication_audit [EXTRACTED 1.00]
- **Exact Money Validation Flow** — positive_money_contract, withdrawal_request_contract, deposit_request_contract, schema_accepts_positive_decimal_cents_test, schema_rejects_unsafe_money_test, day6_exact_money_acceptance, adr007_legacy_money_defect_rationale [EXTRACTED 1.00]
- **Locked Atomic Financial Operation Flow** — authorized_account_resolution, account_row_locking, withdrawal_workflow, deposit_workflow, persisted_transaction_record, audit_event_append, caller_owned_service_uow, transaction_failure_rollback_test [EXTRACTED 1.00]
- **Academic ATM Requirements-to-Evidence Traceability Chain** — secure_withdrawal_workflow, three_complementary_uml_views, numbered_artifact_traceability, four_atm_execution_scenarios [EXTRACTED 1.00]
- **Day 7 Completion Evidence** — task_day7_interactive_demo, day7_validation_acceptance_path, adr8_thin_streamlit_boundary, memory_day7_complete [EXTRACTED 0.98]
- **Redis-Backed Authentication Contract** — day7_validation_redis_authority, adr8_external_session_authority, adr8_transient_secret_handling [EXTRACTED 1.00]
- **Repeatable Demo Safety** — day7_validation_atomic_demo_reset, adr8_fixed_demo_reset_boundary, readme_fictional_data_boundary [INFERRED 0.90]
- **Day 8 Event Schema Handoff** — memory_day8_next_action, task_day8_event_contract, task_day8_event_envelope, task_day8_domain_payloads, task_day8_sensitive_field_policy, task_day8_serialization_contract_tests, adr8_future_kafka_extension_boundary [EXTRACTED 0.98]
- **Week 1 Core Application Milestone** — task_week1_v050_milestone, task_day7_interactive_demo, memory_week1_quality_gate, changelog_no_release_tag [EXTRACTED 0.94]

## Communities

### Community 0 - "Academic ATM Code"
Cohesion: 0.04
Nodes (61): Academic simulation is not production banking security, Numbered UML activities traced to executable output, Academic zero-balance closure behavior, authenticate_customer(), print_step(), ATM Simulation CSC505 - Principles of Software Engineering  This program follows, Print a numbered activity that matches the UML Activity Diagram., Authenticate the customer using a PIN with a maximum of three attempts. (+53 more)

### Community 1 - "Core ORM Models"
Cohesion: 0.09
Nodes (33): Account, Account-operation responses exposed by the service layer., AuditEvent, Append-oriented operational audit record with secret-free structured details., Base, Base, Shared ORM metadata for BankFlow's application schema., Card (+25 more)

### Community 2 - "Account Service"
Cohesion: 0.13
Nodes (39): AccountBalance, A consistent balance snapshot and its persisted inquiry transaction., AccountAuthorizationError, AccountService, AccountUnavailableError, BankingServiceError, Authorized account lookup and persisted balance inquiry., Base exception for stable transaction-service failures. (+31 more)

### Community 3 - "Repository Layer"
Cohesion: 0.09
Nodes (28): AccountRepository, Account lookups and exact-balance persistence., Persist account state while the caller owns commit and rollback., CustomerRepository, Customer persistence queries., Read customers without owning the surrounding transaction., ConcurrentUpdateError, InvalidRepositoryQueryError (+20 more)

### Community 4 - "Foundation Validation Decisions"
Cohesion: 0.05
Nodes (48): Day 1 import, lint, hash and CLI checks, Initial admin-role setup attempt could not create roles; no database resources created, Migration downgrade must never run against application database, Autogeneration inspects bankflow schema; future models require metadata registration, Base metadata targets bankflow with stable constraint names, Migration bookkeeping must survive application-schema bootstrap and downgrade, Pytest configured for concise tracebacks after connection-argument exposure, Bounded connection pool, timeout, pre-ping and hidden SQL parameters (+40 more)

### Community 5 - "Streamlit Runtime and Demo Reset"
Cohesion: 0.06
Nodes (25): DemoDataUnavailableError, DemoResetResult, DemoService, Atomic reset for the one fixed, fictional BankFlow demo graph., The fixed identifiers do not resolve to the expected demo graph., Manage demo-only state inside a caller-owned database transaction., AccountSummary, BankFlowRuntime (+17 more)

### Community 6 - "Authentication and Redis"
Cohesion: 0.07
Nodes (42): ADR-006 Split Authentication State by Durability, Four-ASCII-Digit PIN Contract, Authentication Outcome Vocabulary, Secret-Safe Authentication Request Contract, Secret-Safe Authentication Result Contract, Transactional Authentication Service, Identifier-Only Authentication Session Payload, Redis Authentication State Store (+34 more)

### Community 7 - "Transaction Service Design"
Cohesion: 0.07
Nodes (40): Account Authorization Error, Account Balance Snapshot Contract, Account Row Locking For Consistent Operations, Account Unavailable Error, Audit Rows Share The Database Transaction, Caller-Owned SQLAlchemy Transaction Decision, Persist Declined Insufficient-Funds Attempts, PostgreSQL Transactional Source Of Truth (+32 more)

### Community 8 - "Streamlit Interface Architecture"
Cohesion: 0.07
Nodes (37): Accessible Text-Bearing Status Design, Balance Inquiry Rerun Control, Exact-Money Service Adapter, External Redis Session Authority, Fixed Demo Reset Boundary, Future Kafka Extension Below Service Boundary, Infrastructure-Only Streamlit Cache, Rationale: Add Kafka Without Changing UI Forms (+29 more)

### Community 9 - "Alembic and Database Runtime"
Cohesion: 0.08
Nodes (24): downgrade(), create core banking domain models  Revision ID: 0002 Revises: 0001, upgrade(), database_engine(), migrated_database(), create_database_engine(), Lazy SQLAlchemy engine construction; the caller owns engine disposal., Create a pool without opening a connection until first use. (+16 more)

### Community 10 - "ATM Sequence Model"
Cohesion: 0.08
Nodes (32): ATM System, Attempts >= 3?, Authenticate Customer: access granted, Bank / Account System, Bank checks sufficient funds, Debit Amount from Account, Check Account Balance, Close Account at zero balance (+24 more)

### Community 11 - "Academic Interaction Trace"
Cohesion: 0.11
Nodes (32): Academic PIN check and three-failure session rejection, Account, ATM, 15 Balance, Bank System, 12 Check Balance(amount), 5 Check PIN, Customer (+24 more)

### Community 12 - "UML Sequence and Activity"
Cohesion: 0.09
Nodes (28): Numbered activity panel, Sequence ATM lifeline, Authenticated / show menu, Check available account balance, Sequence Bank System lifeline, Dispense Cash after debit success, Check Balance, Account Closed for zero balance (+20 more)

### Community 13 - "ATM Activity Model"
Cohesion: 0.09
Nodes (26): Activity arrow routing disagrees with numbered PIN and bank balance flow, Increment Failed Attempt Counter, Authenticate Customer, Bank Check Balance, Bank debit amount from account, Check Account Balance, Close Account automatically at zero balance, Display Transaction Complete / Updated Balance (+18 more)

### Community 14 - "ATM Activity Diagram"
Cohesion: 0.1
Nodes (22): Activity arrow routing disagrees with numbered PIN and bank balance flow, Increment Failed Attempt Counter, Authenticate Customer, Bank Check Balance, Bank debit amount from account, Check Account Balance, Close Account automatically at zero balance, Display Transaction Complete / Updated Balance (+14 more)

### Community 15 - "ATM State Machine Logic"
Cohesion: 0.15
Nodes (18): Authenticated: showMenu, Check Balance: validateAmount, Account Closed: displayClosedMsg, Transaction Complete, Final State, PIN format validation, Idle: displayWelcome / clearScreen, Increment Attempts: incrementCounter (+10 more)

### Community 16 - "ATM State Diagram"
Cohesion: 0.15
Nodes (17): Account Active / transaction complete, Authenticated Customer, Check Balance, Account Closed, ATM UML State Machine Diagram, Eject Card, Final State / End of Session, Idle / waiting for card (+9 more)

### Community 17 - "Database Provisioning"
Cohesion: 0.23
Nodes (14): admin_sql(), main(), provision(), Provision or rotate local Day 2 database access without resetting data., Render one local environment file without exposing its password., Replace exactly one setting while preserving every other local choice., Rotate both owner passwords and atomically replace their ignored files., render_environment() (+6 more)

### Community 18 - "Demo Seed and UI Tests"
Cohesion: 0.17
Nodes (13): main(), Insert the idempotent fictional BankFlow demo customer, account, and card., Existing fixed demo identifiers do not form the expected complete seed., Create the fixed demo graph once and reject partial/conflicting state., seed_demo_data(), SeedConflictError, SeedResult, _button() (+5 more)

### Community 19 - "ATM State Model Details"
Cohesion: 0.19
Nodes (14): Account Active: transaction complete; display new balance, Authenticated: showMenu, Check Balance after withdrawal, Account Closed: display closed message, Final State: end of session, Idle: waiting for card; display welcome, Increment Attempts: increase failed attempt counter, Initial State (+6 more)

### Community 20 - "Demo Execution Scenario"
Cohesion: 0.18
Nodes (11): Account status ACTIVE, Authenticate Customer: access granted, Starting balance $500.00, Cash dispensed $100.00, Correct PIN 2468 on third input, End ATM Session and remove card, Incorrect PIN 1111: failed attempts 1/3, Updated balance $400.00 (+3 more)

### Community 21 - "Academic Reports and Engineering Lessons"
Cohesion: 0.18
Nodes (11): ATM System Design and Implementation Report, Classroom-to-Production ATM Security Gap, Four ATM Execution Scenarios, Numbered Design-to-Execution Traceability, Waterfall Prototyping and Agile Tradeoffs, Requirements Before Implementation, Authenticated ATM Withdrawal Workflow, Security Across the Software Lifecycle (+3 more)

### Community 22 - "Foundation Architecture"
Cohesion: 0.22
Nodes (9): ADR-001 Repository and Runtime Foundation, BankFlow Service Endpoint Reference, Dedicated BankFlow Data-Lab Container, Host and Container Network Boundary, Installable src/bankflow Package Layout, Legacy ATM Prototype Limitations, Original Academic ATM Archive, Preserved Academic Source Provenance (+1 more)

### Community 23 - "Settings Validation Tests"
Cohesion: 0.25
Nodes (0): 

### Community 24 - "Domain Model Architecture"
Cohesion: 0.29
Nodes (7): ADR-004 Exact and Traceable Banking Domain Model, Application-Generated UUID Identity, Exact NUMERIC and Decimal Money Policy, Restrictive Financial History Retention, Avoid Academic Prototype Floating-Point Defects, Idempotent Fixed Demo Seed, Tokenized Card and Salted PIN-Hash Persistence

### Community 25 - "Exact Money UI Contracts"
Cohesion: 0.29
Nodes (7): Day 7 Must Convert UI Values Deliberately, Day 6 Exact Money Acceptance, Deposit Request Contract, Strict Positive Decimal Money Contract, Positive Decimal Cents Acceptance Test, Unsafe Money Rejection Test, Withdrawal Request Contract

### Community 26 - "Repository Architecture"
Cohesion: 0.4
Nodes (6): ADR-005 Session-Bound Repository Boundary, Repository Preparation for Atomic Transactions, Caller-Owned Database Unit of Work, Account Row Lock and Version Check, Stable Repository Exceptions, Stable Newest-First Transaction History

### Community 27 - "Transaction Schema Tests"
Cohesion: 0.4
Nodes (2): Transaction inputs accept exact positive cents and reject unsafe money., test_transaction_history_query_enforces_repository_bounds()

### Community 28 - "Planned Lakehouse"
Cohesion: 0.4
Nodes (5): Planned immutable Iceberg Bronze events, Planned Gold business metrics, Planned standardized Silver datasets, Planned synthetic event generator, Planned V2 streaming lakehouse

### Community 29 - "Schema Bootstrap Migration"
Cohesion: 0.5
Nodes (1): Create the application schema; domain tables follow in Day 3.  Revision ID: 0001

### Community 30 - "Environment Import Check"
Cohesion: 0.5
Nodes (3): main(), Check Day 1 imports without opening network connections or loading secrets., Return nonzero if the selected interpreter or an application import fails.

### Community 31 - "Model Metadata Tests"
Cohesion: 0.5
Nodes (0): 

### Community 32 - "UML Activity Swimlanes"
Cohesion: 0.5
Nodes (4): ATM System swimlane, Bank / Account System swimlane, Customer swimlane, Numbered ATM UML activity diagram

### Community 33 - "UML Swimlane Source"
Cohesion: 0.5
Nodes (4): ATM System swimlane, Bank / Account System swimlane, Customer swimlane, Numbered ATM UML activity diagram

### Community 34 - "Test Settings Isolation"
Cohesion: 0.67
Nodes (1): Keep external environment overrides from changing test database selection.

### Community 35 - "Kafka Sequencing"
Cohesion: 0.67
Nodes (3): Kafka Follows Day 8 Contract And Day 9 Integration, Database Completion Before Event Publication, Day 6 Kafka Deferral

### Community 36 - "Transaction Engine Evidence"
Cohesion: 0.67
Nodes (3): ADR-007 Exact And Atomic Service Boundary, Correct Legacy Float And Fractional-Cent Defects, Day 6 Transaction Engine Validation Evidence

### Community 37 - "Withdrawal UI"
Cohesion: 0.67
Nodes (1): Authenticated withdrawal form.

### Community 38 - "Deposit UI"
Cohesion: 0.67
Nodes (1): Authenticated deposit form.

### Community 39 - "Layered UI Architecture"
Cohesion: 1.0
Nodes (2): Service Repository And UI Separation, Streamlit Interaction-Only Responsibility

### Community 40 - "Welcome and Authentication UI"
Cohesion: 1.0
Nodes (1): BankFlow welcome and authentication screen.

### Community 41 - "Account Dashboard UI"
Cohesion: 1.0
Nodes (1): Authenticated BankFlow account dashboard.

### Community 42 - "Transaction History UI"
Cohesion: 1.0
Nodes (1): Authenticated transaction-history page.

### Community 43 - "Demo Constants"
Cohesion: 1.0
Nodes (1): Stable identifiers and public credentials for the fictional demo account.

### Community 44 - "Development Tooling"
Cohesion: 1.0
Nodes (1): pytest and Ruff development tooling

### Community 45 - "Dependency Snapshot"
Cohesion: 1.0
Nodes (1): Windows Python 3.14 dependency snapshot

### Community 46 - "Lockout Design"
Cohesion: 1.0
Nodes (1): Temporary card lockout in UI design

### Community 47 - "Database Isolation"
Cohesion: 1.0
Nodes (1): Isolated Application and Test Databases

### Community 48 - "Redis Isolation"
Cohesion: 1.0
Nodes (1): Redis Application and Integration-Test Database Isolation

### Community 49 - "Fictional Data Policy"
Cohesion: 1.0
Nodes (1): Educational fictional data only

### Community 50 - "Event Secret Exclusion"
Cohesion: 1.0
Nodes (1): PINs and hashes excluded from events

### Community 51 - "Kafka Connectivity Gap"
Cohesion: 1.0
Nodes (1): Kafka Broker Metadata Validation Gap

### Community 52 - "Dedicated Lab Container"
Cohesion: 1.0
Nodes (1): Dedicated user-provided lab container replaces shared lab

### Community 53 - "Session Termination Flow"
Cohesion: 1.0
Nodes (1): End ATM Session

### Community 54 - "Session Termination Design"
Cohesion: 1.0
Nodes (1): End ATM Session

### Community 55 - "Day 5 Service Handoff"
Cohesion: 1.0
Nodes (1): Day 5 Defers Banking Operations To Day 6

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
- **210 isolated node(s):** `ATM Simulation CSC505 - Principles of Software Engineering  This program follows`, `Print a numbered activity that matches the UML Activity Diagram.`, `Authenticate the customer using a PIN with a maximum of three attempts.`, `Request and validate a withdrawal amount.`, `Run one complete ATM session.` (+205 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Layered UI Architecture`** (2 nodes): `Service Repository And UI Separation`, `Streamlit Interaction-Only Responsibility`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Welcome and Authentication UI`** (2 nodes): `app.py`, `BankFlow welcome and authentication screen.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Account Dashboard UI`** (2 nodes): `Authenticated BankFlow account dashboard.`, `1_Dashboard.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Transaction History UI`** (2 nodes): `Authenticated transaction-history page.`, `4_Transaction_History.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Demo Constants`** (2 nodes): `Stable identifiers and public credentials for the fictional demo account.`, `demo.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Development Tooling`** (1 nodes): `pytest and Ruff development tooling`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dependency Snapshot`** (1 nodes): `Windows Python 3.14 dependency snapshot`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Lockout Design`** (1 nodes): `Temporary card lockout in UI design`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Database Isolation`** (1 nodes): `Isolated Application and Test Databases`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Redis Isolation`** (1 nodes): `Redis Application and Integration-Test Database Isolation`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Fictional Data Policy`** (1 nodes): `Educational fictional data only`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Event Secret Exclusion`** (1 nodes): `PINs and hashes excluded from events`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Kafka Connectivity Gap`** (1 nodes): `Kafka Broker Metadata Validation Gap`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dedicated Lab Container`** (1 nodes): `Dedicated user-provided lab container replaces shared lab`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Session Termination Flow`** (1 nodes): `End ATM Session`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Session Termination Design`** (1 nodes): `End ATM Session`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Day 5 Service Handoff`** (1 nodes): `Day 5 Defers Banking Operations To Day 6`
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
