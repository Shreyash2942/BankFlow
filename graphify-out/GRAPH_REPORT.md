# Graph Report - .  (2026-10-05)

## Corpus Check
- 124 files · ~349,396 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 887 nodes · 1432 edges · 61 communities detected
- Extraction: 71% EXTRACTED · 29% INFERRED · 0% AMBIGUOUS · INFERRED: 415 edges (avg confidence: 0.66)
- Token cost: unavailable — agent execution does not expose actual token usage; unknown is not zero.

## Community Hubs (Navigation)
- [[_COMMUNITY_Academic CLI Traceability|Academic CLI Traceability]]
- [[_COMMUNITY_PIN Authentication UML|PIN Authentication UML]]
- [[_COMMUNITY_Core ORM Models|Core ORM Models]]
- [[_COMMUNITY_Event Schemas and Factories|Event Schemas and Factories]]
- [[_COMMUNITY_Account Services|Account Services]]
- [[_COMMUNITY_Repository Layer|Repository Layer]]
- [[_COMMUNITY_Foundation Validation|Foundation Validation]]
- [[_COMMUNITY_Event Contract Architecture|Event Contract Architecture]]
- [[_COMMUNITY_Streamlit Runtime and Demo|Streamlit Runtime and Demo]]
- [[_COMMUNITY_Authentication and Redis|Authentication and Redis]]
- [[_COMMUNITY_Transaction Service Decisions|Transaction Service Decisions]]
- [[_COMMUNITY_Alembic Database Runtime|Alembic Database Runtime]]
- [[_COMMUNITY_ATM Sequence Model|ATM Sequence Model]]
- [[_COMMUNITY_Database Provisioning|Database Provisioning]]
- [[_COMMUNITY_UML Execution Trace|UML Execution Trace]]
- [[_COMMUNITY_ATM State Machine Logic|ATM State Machine Logic]]
- [[_COMMUNITY_ATM State Diagram|ATM State Diagram]]
- [[_COMMUNITY_ATM State Scenarios|ATM State Scenarios]]
- [[_COMMUNITY_Withdrawal Activity Flow|Withdrawal Activity Flow]]
- [[_COMMUNITY_Academic Withdrawal Flow|Academic Withdrawal Flow]]
- [[_COMMUNITY_Prototype Acceptance Scenarios|Prototype Acceptance Scenarios]]
- [[_COMMUNITY_Streamlit Interface Boundary|Streamlit Interface Boundary]]
- [[_COMMUNITY_Software Engineering Lessons|Software Engineering Lessons]]
- [[_COMMUNITY_Foundation and Environment|Foundation and Environment]]
- [[_COMMUNITY_Settings Validation Tests|Settings Validation Tests]]
- [[_COMMUNITY_Core Domain Decision|Core Domain Decision]]
- [[_COMMUNITY_Exact Money Requests|Exact Money Requests]]
- [[_COMMUNITY_Repository Boundary Decision|Repository Boundary Decision]]
- [[_COMMUNITY_Transaction Schema Tests|Transaction Schema Tests]]
- [[_COMMUNITY_V2 Lakehouse Plan|V2 Lakehouse Plan]]
- [[_COMMUNITY_Initial Alembic Migration|Initial Alembic Migration]]
- [[_COMMUNITY_Environment Import Check|Environment Import Check]]
- [[_COMMUNITY_ORM Metadata Tests|ORM Metadata Tests]]
- [[_COMMUNITY_UML Swimlane Diagram|UML Swimlane Diagram]]
- [[_COMMUNITY_UML Activity Swimlanes|UML Activity Swimlanes]]
- [[_COMMUNITY_Test Environment Isolation|Test Environment Isolation]]
- [[_COMMUNITY_Transaction Engine ADR|Transaction Engine ADR]]
- [[_COMMUNITY_Withdrawal Page|Withdrawal Page]]
- [[_COMMUNITY_Deposit Page|Deposit Page]]
- [[_COMMUNITY_Demo Reset Boundary|Demo Reset Boundary]]
- [[_COMMUNITY_Streamlit Entry Page|Streamlit Entry Page]]
- [[_COMMUNITY_Dashboard Page|Dashboard Page]]
- [[_COMMUNITY_History Page|History Page]]
- [[_COMMUNITY_Demo Identifiers|Demo Identifiers]]
- [[_COMMUNITY_Kafka Extension Boundary|Kafka Extension Boundary]]
- [[_COMMUNITY_Development Tooling|Development Tooling]]
- [[_COMMUNITY_Dependency Lock|Dependency Lock]]
- [[_COMMUNITY_UI Lockout Design|UI Lockout Design]]
- [[_COMMUNITY_Database Isolation|Database Isolation]]
- [[_COMMUNITY_Redis Test Isolation|Redis Test Isolation]]
- [[_COMMUNITY_Fictional Data Policy|Fictional Data Policy]]
- [[_COMMUNITY_Event Secret Exclusion|Event Secret Exclusion]]
- [[_COMMUNITY_Kafka Readiness Gap|Kafka Readiness Gap]]
- [[_COMMUNITY_Dedicated Lab Container|Dedicated Lab Container]]
- [[_COMMUNITY_Session Ending|Session Ending]]
- [[_COMMUNITY_ATM Session End|ATM Session End]]
- [[_COMMUNITY_Day 5 Scope Boundary|Day 5 Scope Boundary]]
- [[_COMMUNITY_Day 6 Kafka Deferral|Day 6 Kafka Deferral]]
- [[_COMMUNITY_Kafka Delivery Sequence|Kafka Delivery Sequence]]
- [[_COMMUNITY_Secret Masking|Secret Masking]]
- [[_COMMUNITY_Accessible Status Design|Accessible Status Design]]

## God Nodes (most connected - your core abstractions)
1. `Typed event construction; Kafka transport follows on Day 9.` - 44 edges
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
- `Scenario 2: Incorrect PIN then successful authentication` --illustrates_legacy_behavior--> `authenticate_customer()`  [INFERRED]
  docs/original-college-project/ATM_Execution_Screenshots/incorrect_then_correct_pin.png → docs/original-college-project/atm_simulation.py
- `Alembic environment using the same validated settings as the application.` --uses--> `Base`  [INFERRED]
  migrations\env.py → src\bankflow\database\base.py
- `Autogeneration must not propose changes to unrelated schemas.` --uses--> `Base`  [INFERRED]
  migrations\env.py → src\bankflow\database\base.py

## Hyperedges (group relationships)
- **Transactional Card Authentication Flow** — authentication_request_contract, authentication_service, card_row_lock_lookup, constant_time_pin_verification, authentication_state_store, authentication_result_contract [EXTRACTED 1.00]
- **Opted-in migration reversal is isolated from application data by credentials, role grants and database guards** — day2_test_database, day2_test_guard, day2_role_isolation, day2_migration_validation, day2_app_protection [EXTRACTED 1.00]
- **Academic requirements/model/code/execution traceability** — academic_trace, uml_state, uml_activity, uml_sequence, prototype, manual_scenarios [EXTRACTED 1.00]
- **Schema bootstrap keeps migration bookkeeping independent while refusing destructive cascade** — migration, day2_schema, day2_public_version, day2_bootstrap_rationale, day2_no_cascade [EXTRACTED 1.00]
- **Exact Money Validation Flow** — positive_money_contract, withdrawal_request_contract, deposit_request_contract, schema_accepts_positive_decimal_cents_test, schema_rejects_unsafe_money_test, day6_exact_money_acceptance, adr007_legacy_money_defect_rationale [EXTRACTED 1.00]
- **Locked Atomic Financial Operation Flow** — authorized_account_resolution, account_row_locking, withdrawal_workflow, deposit_workflow, persisted_transaction_record, audit_event_append, caller_owned_service_uow, transaction_failure_rollback_test [EXTRACTED 1.00]
- **Redis-Backed Authentication Contract** — day7_validation_redis_authority, adr8_external_session_authority, adr8_transient_secret_handling [EXTRACTED 1.00]
- **Academic ATM Requirements-to-Evidence Traceability Chain** — secure_withdrawal_workflow, three_complementary_uml_views, numbered_artifact_traceability, four_atm_execution_scenarios [EXTRACTED 1.00]
- **Authentication Event Family** — event_schema_authentication_payload, event_schema_authentication_succeeded, event_schema_authentication_failed, event_schema_card_locked, event_schema_session_ended [EXTRACTED 1.00]
- **Transaction Event Family** — event_schema_transaction_payload, event_schema_balance_viewed, event_schema_withdrawal_requested, event_schema_withdrawal_completed, event_schema_withdrawal_declined, event_schema_deposit_completed, event_schema_account_closed [EXTRACTED 1.00]

## Communities

### Community 0 - "Academic CLI Traceability"
Cohesion: 0.04
Nodes (61): Academic simulation is not production banking security, Numbered UML activities traced to executable output, Academic zero-balance closure behavior, authenticate_customer(), print_step(), ATM Simulation CSC505 - Principles of Software Engineering  This program follows, Print a numbered activity that matches the UML Activity Diagram., Authenticate the customer using a PIN with a maximum of three attempts. (+53 more)

### Community 1 - "PIN Authentication UML"
Cohesion: 0.05
Nodes (58): Academic PIN check and three-failure session rejection, Activity arrow routing disagrees with numbered PIN and bank balance flow, Increment Failed Attempt Counter, Authenticate Customer, Bank Check Balance, PIN correct decision, Enter PIN, Insert Card (+50 more)

### Community 2 - "Core ORM Models"
Cohesion: 0.09
Nodes (33): Account, Account-operation responses exposed by the service layer., AuditEvent, Append-oriented operational audit record with secret-free structured details., Base, Base, Shared ORM metadata for BankFlow's application schema., Card (+25 more)

### Community 3 - "Event Schemas and Factories"
Cohesion: 0.09
Nodes (48): balance_viewed_event(), deserialize_event(), _envelope(), event_from_authentication_result(), event_from_transaction_result(), EventFactoryError, Create and serialize schema-version-1 events from application-service results., Return compact UTF-8 JSON; Decimal values remain exact JSON strings. (+40 more)

### Community 4 - "Account Services"
Cohesion: 0.13
Nodes (39): AccountBalance, A consistent balance snapshot and its persisted inquiry transaction., AccountAuthorizationError, AccountService, AccountUnavailableError, BankingServiceError, Authorized account lookup and persisted balance inquiry., Base exception for stable transaction-service failures. (+31 more)

### Community 5 - "Repository Layer"
Cohesion: 0.09
Nodes (28): AccountRepository, Account lookups and exact-balance persistence., Persist account state while the caller owns commit and rollback., CustomerRepository, Customer persistence queries., Read customers without owning the surrounding transaction., ConcurrentUpdateError, InvalidRepositoryQueryError (+20 more)

### Community 6 - "Foundation Validation"
Cohesion: 0.05
Nodes (48): Day 1 import, lint, hash and CLI checks, Initial admin-role setup attempt could not create roles; no database resources created, Migration downgrade must never run against application database, Autogeneration inspects bankflow schema; future models require metadata registration, Base metadata targets bankflow with stable constraint names, Migration bookkeeping must survive application-schema bootstrap and downgrade, Pytest configured for concise tracebacks after connection-argument exposure, Bounded connection pool, timeout, pre-ping and hidden SQL parameters (+40 more)

### Community 7 - "Event Contract Architecture"
Cohesion: 0.06
Nodes (48): Avoid Revealing Unknown Card Existence, Authentication Subject Identifier Policy, Closed BankFlowEvent Envelope, Kafka Delivery and Database-Broker Atomicity Limit, Discriminated Transaction and Authentication Payloads, ADR-009 Versioned and Secret-Free Application Event Contract, Distinct Event and Transaction Identities, Exact Decimal Money as JSON Strings (+40 more)

### Community 8 - "Streamlit Runtime and Demo"
Cohesion: 0.06
Nodes (25): DemoDataUnavailableError, DemoResetResult, DemoService, Atomic reset for the one fixed, fictional BankFlow demo graph., The fixed identifiers do not resolve to the expected demo graph., Manage demo-only state inside a caller-owned database transaction., AccountSummary, BankFlowRuntime (+17 more)

### Community 9 - "Authentication and Redis"
Cohesion: 0.07
Nodes (42): ADR-006 Split Authentication State by Durability, Four-ASCII-Digit PIN Contract, Authentication Outcome Vocabulary, Secret-Safe Authentication Request Contract, Secret-Safe Authentication Result Contract, Transactional Authentication Service, Identifier-Only Authentication Session Payload, Redis Authentication State Store (+34 more)

### Community 10 - "Transaction Service Decisions"
Cohesion: 0.08
Nodes (36): Account Authorization Error, Account Balance Snapshot Contract, Account Row Locking For Consistent Operations, Account Unavailable Error, Audit Rows Share The Database Transaction, Caller-Owned SQLAlchemy Transaction Decision, Persist Declined Insufficient-Funds Attempts, Audit Event Append Helper (+28 more)

### Community 11 - "Alembic Database Runtime"
Cohesion: 0.08
Nodes (24): downgrade(), create core banking domain models  Revision ID: 0002 Revises: 0001, upgrade(), database_engine(), migrated_database(), create_database_engine(), Lazy SQLAlchemy engine construction; the caller owns engine disposal., Create a pool without opening a connection until first use. (+16 more)

### Community 12 - "ATM Sequence Model"
Cohesion: 0.08
Nodes (32): ATM System, Attempts >= 3?, Authenticate Customer: access granted, Bank / Account System, Bank checks sufficient funds, Debit Amount from Account, Check Account Balance, Close Account at zero balance (+24 more)

### Community 13 - "Database Provisioning"
Cohesion: 0.1
Nodes (26): admin_sql(), main(), provision(), Provision or rotate local Day 2 database access without resetting data., Render one local environment file without exposing its password., Replace exactly one setting while preserving every other local choice., Rotate both owner passwords and atomically replace their ignored files., render_environment() (+18 more)

### Community 14 - "UML Execution Trace"
Cohesion: 0.09
Nodes (28): Numbered activity panel, Sequence ATM lifeline, Authenticated / show menu, Check available account balance, Sequence Bank System lifeline, Dispense Cash after debit success, Check Balance, Account Closed for zero balance (+20 more)

### Community 15 - "ATM State Machine Logic"
Cohesion: 0.15
Nodes (18): Authenticated: showMenu, Check Balance: validateAmount, Account Closed: displayClosedMsg, Transaction Complete, Final State, PIN format validation, Idle: displayWelcome / clearScreen, Increment Attempts: incrementCounter (+10 more)

### Community 16 - "ATM State Diagram"
Cohesion: 0.15
Nodes (17): Account Active / transaction complete, Authenticated Customer, Check Balance, Account Closed, ATM UML State Machine Diagram, Eject Card, Final State / End of Session, Idle / waiting for card (+9 more)

### Community 17 - "ATM State Scenarios"
Cohesion: 0.19
Nodes (14): Account Active: transaction complete; display new balance, Authenticated: showMenu, Check Balance after withdrawal, Account Closed: display closed message, Final State: end of session, Idle: waiting for card; display welcome, Increment Attempts: increase failed attempt counter, Initial State (+6 more)

### Community 18 - "Withdrawal Activity Flow"
Cohesion: 0.2
Nodes (11): Bank debit amount from account, Check Account Balance, Close Account automatically at zero balance, Display Transaction Complete / Updated Balance, Dispense Cash, Amount <= Balance decision, Display Insufficient Funds Message, Request Withdrawal Amount (+3 more)

### Community 19 - "Academic Withdrawal Flow"
Cohesion: 0.2
Nodes (11): Bank debit amount from account, Check Account Balance, Close Account automatically at zero balance, Display Transaction Complete / Updated Balance, Dispense Cash, Amount <= Balance decision, Display Insufficient Funds Message, Request Withdrawal Amount (+3 more)

### Community 20 - "Prototype Acceptance Scenarios"
Cohesion: 0.18
Nodes (11): Account status ACTIVE, Authenticate Customer: access granted, Starting balance $500.00, Cash dispensed $100.00, Correct PIN 2468 on third input, End ATM Session and remove card, Incorrect PIN 1111: failed attempts 1/3, Updated balance $400.00 (+3 more)

### Community 21 - "Streamlit Interface Boundary"
Cohesion: 0.2
Nodes (11): Balance Inquiry Rerun Control, Exact-Money Service Adapter, External Redis Session Authority, Infrastructure-Only Streamlit Cache, Rationale: Preserve PostgreSQL and Redis Authority, Rationale: Prevent Duplicate Inquiry Transactions, Thin Streamlit Interface Boundary, Day 7 Live Acceptance Path (+3 more)

### Community 22 - "Software Engineering Lessons"
Cohesion: 0.18
Nodes (11): ATM System Design and Implementation Report, Classroom-to-Production ATM Security Gap, Four ATM Execution Scenarios, Numbered Design-to-Execution Traceability, Waterfall Prototyping and Agile Tradeoffs, Requirements Before Implementation, Authenticated ATM Withdrawal Workflow, Security Across the Software Lifecycle (+3 more)

### Community 23 - "Foundation and Environment"
Cohesion: 0.22
Nodes (9): ADR-001 Repository and Runtime Foundation, BankFlow Service Endpoint Reference, Dedicated BankFlow Data-Lab Container, Host and Container Network Boundary, Installable src/bankflow Package Layout, Legacy ATM Prototype Limitations, Original Academic ATM Archive, Preserved Academic Source Provenance (+1 more)

### Community 24 - "Settings Validation Tests"
Cohesion: 0.25
Nodes (0): 

### Community 25 - "Core Domain Decision"
Cohesion: 0.29
Nodes (7): ADR-004 Exact and Traceable Banking Domain Model, Application-Generated UUID Identity, Exact NUMERIC and Decimal Money Policy, Restrictive Financial History Retention, Avoid Academic Prototype Floating-Point Defects, Idempotent Fixed Demo Seed, Tokenized Card and Salted PIN-Hash Persistence

### Community 26 - "Exact Money Requests"
Cohesion: 0.29
Nodes (7): Day 7 Must Convert UI Values Deliberately, Day 6 Exact Money Acceptance, Deposit Request Contract, Strict Positive Decimal Money Contract, Positive Decimal Cents Acceptance Test, Unsafe Money Rejection Test, Withdrawal Request Contract

### Community 27 - "Repository Boundary Decision"
Cohesion: 0.4
Nodes (6): ADR-005 Session-Bound Repository Boundary, Repository Preparation for Atomic Transactions, Caller-Owned Database Unit of Work, Account Row Lock and Version Check, Stable Repository Exceptions, Stable Newest-First Transaction History

### Community 28 - "Transaction Schema Tests"
Cohesion: 0.4
Nodes (2): Transaction inputs accept exact positive cents and reject unsafe money., test_transaction_history_query_enforces_repository_bounds()

### Community 29 - "V2 Lakehouse Plan"
Cohesion: 0.4
Nodes (5): Planned immutable Iceberg Bronze events, Planned Gold business metrics, Planned standardized Silver datasets, Planned synthetic event generator, Planned V2 streaming lakehouse

### Community 30 - "Initial Alembic Migration"
Cohesion: 0.5
Nodes (1): Create the application schema; domain tables follow in Day 3.  Revision ID: 0001

### Community 31 - "Environment Import Check"
Cohesion: 0.5
Nodes (3): main(), Check Day 1 imports without opening network connections or loading secrets., Return nonzero if the selected interpreter or an application import fails.

### Community 32 - "ORM Metadata Tests"
Cohesion: 0.5
Nodes (0): 

### Community 33 - "UML Swimlane Diagram"
Cohesion: 0.5
Nodes (4): ATM System swimlane, Bank / Account System swimlane, Customer swimlane, Numbered ATM UML activity diagram

### Community 34 - "UML Activity Swimlanes"
Cohesion: 0.5
Nodes (4): ATM System swimlane, Bank / Account System swimlane, Customer swimlane, Numbered ATM UML activity diagram

### Community 35 - "Test Environment Isolation"
Cohesion: 0.67
Nodes (1): Keep external environment overrides from changing test database selection.

### Community 36 - "Transaction Engine ADR"
Cohesion: 0.67
Nodes (3): ADR-007 Exact And Atomic Service Boundary, Correct Legacy Float And Fractional-Cent Defects, Day 6 Transaction Engine Validation Evidence

### Community 37 - "Withdrawal Page"
Cohesion: 0.67
Nodes (1): Authenticated withdrawal form.

### Community 38 - "Deposit Page"
Cohesion: 0.67
Nodes (1): Authenticated deposit form.

### Community 39 - "Demo Reset Boundary"
Cohesion: 0.67
Nodes (3): Fixed Demo Reset Boundary, Rationale: Make Portfolio Demonstrations Repeatable, Atomic Fixed-Demo Reset

### Community 40 - "Streamlit Entry Page"
Cohesion: 1.0
Nodes (1): BankFlow welcome and authentication screen.

### Community 41 - "Dashboard Page"
Cohesion: 1.0
Nodes (1): Authenticated BankFlow account dashboard.

### Community 42 - "History Page"
Cohesion: 1.0
Nodes (1): Authenticated transaction-history page.

### Community 43 - "Demo Identifiers"
Cohesion: 1.0
Nodes (1): Stable identifiers and public credentials for the fictional demo account.

### Community 44 - "Kafka Extension Boundary"
Cohesion: 1.0
Nodes (2): Future Kafka Extension Below Service Boundary, Rationale: Add Kafka Without Changing UI Forms

### Community 45 - "Development Tooling"
Cohesion: 1.0
Nodes (1): pytest and Ruff development tooling

### Community 46 - "Dependency Lock"
Cohesion: 1.0
Nodes (1): Windows Python 3.14 dependency snapshot

### Community 47 - "UI Lockout Design"
Cohesion: 1.0
Nodes (1): Temporary card lockout in UI design

### Community 48 - "Database Isolation"
Cohesion: 1.0
Nodes (1): Isolated Application and Test Databases

### Community 49 - "Redis Test Isolation"
Cohesion: 1.0
Nodes (1): Redis Application and Integration-Test Database Isolation

### Community 50 - "Fictional Data Policy"
Cohesion: 1.0
Nodes (1): Educational fictional data only

### Community 51 - "Event Secret Exclusion"
Cohesion: 1.0
Nodes (1): PINs and hashes excluded from events

### Community 52 - "Kafka Readiness Gap"
Cohesion: 1.0
Nodes (1): Kafka Broker Metadata Validation Gap

### Community 53 - "Dedicated Lab Container"
Cohesion: 1.0
Nodes (1): Dedicated user-provided lab container replaces shared lab

### Community 54 - "Session Ending"
Cohesion: 1.0
Nodes (1): End ATM Session

### Community 55 - "ATM Session End"
Cohesion: 1.0
Nodes (1): End ATM Session

### Community 56 - "Day 5 Scope Boundary"
Cohesion: 1.0
Nodes (1): Day 5 Defers Banking Operations To Day 6

### Community 57 - "Day 6 Kafka Deferral"
Cohesion: 1.0
Nodes (1): Day 6 Kafka Deferral

### Community 58 - "Kafka Delivery Sequence"
Cohesion: 1.0
Nodes (1): Kafka Follows Day 8 Contract And Day 9 Integration

### Community 59 - "Secret Masking"
Cohesion: 1.0
Nodes (1): Transient Masked Secret Handling

### Community 60 - "Accessible Status Design"
Cohesion: 1.0
Nodes (1): Accessible Text-Bearing Status Design

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
- **223 isolated node(s):** `ATM Simulation CSC505 - Principles of Software Engineering  This program follows`, `Print a numbered activity that matches the UML Activity Diagram.`, `Authenticate the customer using a PIN with a maximum of three attempts.`, `Request and validate a withdrawal amount.`, `Run one complete ATM session.` (+218 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Streamlit Entry Page`** (2 nodes): `app.py`, `BankFlow welcome and authentication screen.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Page`** (2 nodes): `Authenticated BankFlow account dashboard.`, `1_Dashboard.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `History Page`** (2 nodes): `Authenticated transaction-history page.`, `4_Transaction_History.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Demo Identifiers`** (2 nodes): `Stable identifiers and public credentials for the fictional demo account.`, `demo.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Kafka Extension Boundary`** (2 nodes): `Future Kafka Extension Below Service Boundary`, `Rationale: Add Kafka Without Changing UI Forms`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Development Tooling`** (1 nodes): `pytest and Ruff development tooling`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dependency Lock`** (1 nodes): `Windows Python 3.14 dependency snapshot`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `UI Lockout Design`** (1 nodes): `Temporary card lockout in UI design`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Database Isolation`** (1 nodes): `Isolated Application and Test Databases`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Redis Test Isolation`** (1 nodes): `Redis Application and Integration-Test Database Isolation`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Fictional Data Policy`** (1 nodes): `Educational fictional data only`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Event Secret Exclusion`** (1 nodes): `PINs and hashes excluded from events`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Kafka Readiness Gap`** (1 nodes): `Kafka Broker Metadata Validation Gap`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dedicated Lab Container`** (1 nodes): `Dedicated user-provided lab container replaces shared lab`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Session Ending`** (1 nodes): `End ATM Session`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `ATM Session End`** (1 nodes): `End ATM Session`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Day 5 Scope Boundary`** (1 nodes): `Day 5 Defers Banking Operations To Day 6`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Day 6 Kafka Deferral`** (1 nodes): `Day 6 Kafka Deferral`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Kafka Delivery Sequence`** (1 nodes): `Kafka Follows Day 8 Contract And Day 9 Integration`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Secret Masking`** (1 nodes): `Transient Masked Secret Handling`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Accessible Status Design`** (1 nodes): `Accessible Text-Bearing Status Design`
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
