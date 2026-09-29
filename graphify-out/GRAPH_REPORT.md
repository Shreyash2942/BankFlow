# Graph Report - .  (2026-09-29)

## Corpus Check
- 96 files · ~339,198 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 747 nodes · 1243 edges · 38 communities detected
- Extraction: 68% EXTRACTED · 31% INFERRED · 1% AMBIGUOUS · INFERRED: 387 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Authentication Architecture|Authentication Architecture]]
- [[_COMMUNITY_Repository Persistence|Repository Persistence]]
- [[_COMMUNITY_Academic Prototype Code|Academic Prototype Code]]
- [[_COMMUNITY_Authentication Service Code|Authentication Service Code]]
- [[_COMMUNITY_ORM Domain Models|ORM Domain Models]]
- [[_COMMUNITY_Foundation Validation|Foundation Validation]]
- [[_COMMUNITY_ATM Sequence Interactions|ATM Sequence Interactions]]
- [[_COMMUNITY_Configuration and Migrations|Configuration and Migrations]]
- [[_COMMUNITY_Database Migration Tests|Database Migration Tests]]
- [[_COMMUNITY_ATM Workflow Requirements|ATM Workflow Requirements]]
- [[_COMMUNITY_UML Sequence Diagrams|UML Sequence Diagrams]]
- [[_COMMUNITY_UML Activity Review|UML Activity Review]]
- [[_COMMUNITY_Activity Diagram Details|Activity Diagram Details]]
- [[_COMMUNITY_ATM State Machine Behavior|ATM State Machine Behavior]]
- [[_COMMUNITY_UML State Diagram|UML State Diagram]]
- [[_COMMUNITY_PIN Hashing Security|PIN Hashing Security]]
- [[_COMMUNITY_Architecture Decisions|Architecture Decisions]]
- [[_COMMUNITY_Project Design Rationale|Project Design Rationale]]
- [[_COMMUNITY_Database Provisioning|Database Provisioning]]
- [[_COMMUNITY_Legacy Execution Scenario|Legacy Execution Scenario]]
- [[_COMMUNITY_Two-Stage Platform|Two-Stage Platform]]
- [[_COMMUNITY_Repository Boundary ADR|Repository Boundary ADR]]
- [[_COMMUNITY_Lakehouse Roadmap|Lakehouse Roadmap]]
- [[_COMMUNITY_Environment Import Check|Environment Import Check]]
- [[_COMMUNITY_Domain Metadata Tests|Domain Metadata Tests]]
- [[_COMMUNITY_Activity Diagram Swimlanes|Activity Diagram Swimlanes]]
- [[_COMMUNITY_Diagram Swimlane Duplicate|Diagram Swimlane Duplicate]]
- [[_COMMUNITY_Delivery Roadmap|Delivery Roadmap]]
- [[_COMMUNITY_Kafka Consistency Risk|Kafka Consistency Risk]]
- [[_COMMUNITY_Safe Database URL|Safe Database URL]]
- [[_COMMUNITY_Development Tooling|Development Tooling]]
- [[_COMMUNITY_Python Dependency Lock|Python Dependency Lock]]
- [[_COMMUNITY_UI Lockout Conflict|UI Lockout Conflict]]
- [[_COMMUNITY_Fictional Data Scope|Fictional Data Scope]]
- [[_COMMUNITY_Event Secret Exclusion|Event Secret Exclusion]]
- [[_COMMUNITY_Dedicated Container Decision|Dedicated Container Decision]]
- [[_COMMUNITY_Session End Node|Session End Node]]
- [[_COMMUNITY_Duplicate Session End Node|Duplicate Session End Node]]

## God Nodes (most connected - your core abstractions)
1. `Shared utility functions.` - 40 edges
2. `AuthenticationStateStore` - 24 edges
3. `Settings` - 23 edges
4. `Account` - 22 edges
5. `RepositoryNotFoundError` - 21 edges
6. `Card` - 18 edges
7. `AuthenticationSession` - 18 edges
8. `AuditEvent` - 17 edges
9. `Customer` - 17 edges
10. `Transaction` - 17 edges

## Surprising Connections (you probably didn't know these)
- `Planned validated withdrawal workflow` --semantically_similar_to--> `request_withdrawal()`  [INFERRED] [semantically similar]
  docs/PRODUCT_REQUIREMENTS.md → docs/original-college-project/atm_simulation.py
- `Restrictive Financial History with Durable Audit Rows` --conceptually_related_to--> `Secret-Free Authentication Audit Events`  [INFERRED]
  docs/DAY3_VALIDATION.md → src/bankflow/services/auth_service.py
- `Scenario 2: Incorrect PIN then successful authentication` --illustrates_legacy_behavior--> `authenticate_customer()`  [INFERRED]
  docs/original-college-project/ATM_Execution_Screenshots/incorrect_then_correct_pin.png → docs/original-college-project/atm_simulation.py
- `Create the fixed demo graph once and reject partial/conflicting state.` --uses--> `ConfigurationError`  [INFERRED]
  scripts\seed_database.py → src\bankflow\config\settings.py
- `Run with python -m bankflow.database.health from the repository root.` --uses--> `ConfigurationError`  [INFERRED]
  src\bankflow\database\health.py → src\bankflow\config\settings.py

## Hyperedges (group relationships)
- **Opted-in migration reversal is isolated from application data by credentials, role grants and database guards** — day2_test_database, day2_test_guard, day2_role_isolation, day2_migration_validation, day2_app_protection [EXTRACTED 1.00]
- **Academic requirements/model/code/execution traceability** — academic_trace, uml_state, uml_activity, uml_sequence, prototype, manual_scenarios [EXTRACTED 1.00]
- **Schema bootstrap keeps migration bookkeeping independent while refusing destructive cascade** — migration, day2_schema, day2_public_version, day2_bootstrap_rationale, day2_no_cascade [EXTRACTED 1.00]
- **Transactional Card Authentication Flow** — authentication_request_contract, authentication_service, card_row_lock_lookup, constant_time_pin_verification, authentication_state_store, authentication_result_contract [EXTRACTED 1.00]
- **Day 5 Security Acceptance Evidence** — schema_secret_masking_tests, redis_failure_security_test, pin_hashing_security_tests, redis_state_unit_tests, integration_lockout_scenario, integration_success_session_scenario [INFERRED 0.90]
- **BankFlow Authentication State Flow** — bankflow_authentication_service, postgresql_system_of_record, redis_temporary_operational_state, durable_card_lockout, expiring_failed_attempt_counter, opaque_hashed_session_token, secret_free_authentication_audit [EXTRACTED 1.00]
- **BankFlow Lakehouse Medallion Pipeline** — bankflow_v2_streaming_lakehouse, kafka_event_backbone, medallion_lakehouse_layers, analytics_workload_isolation [EXTRACTED 1.00]
- **Academic ATM Requirements-to-Evidence Traceability Chain** — secure_withdrawal_workflow, three_complementary_uml_views, numbered_artifact_traceability, four_atm_execution_scenarios [EXTRACTED 1.00]

## Communities

### Community 0 - "Authentication Architecture"
Cohesion: 0.05
Nodes (67): ADR-006 Split Authentication State by Durability, Four-ASCII-Digit PIN Contract, Authentication Outcome Vocabulary, Secret-Safe Authentication Request Contract, Secret-Safe Authentication Result Contract, Transactional Authentication Service, Identifier-Only Authentication Session Payload, Redis Authentication State Store (+59 more)

### Community 1 - "Repository Persistence"
Cohesion: 0.07
Nodes (37): AccountRepository, Account lookups and exact-balance persistence., Persist account state while the caller owns commit and rollback., CardRepository, Card lookup queries for later authentication services., Read fictional card credentials without owning a transaction., CustomerRepository, Customer persistence queries. (+29 more)

### Community 2 - "Academic Prototype Code"
Cohesion: 0.04
Nodes (61): Academic simulation is not production banking security, Numbered UML activities traced to executable output, Academic zero-balance closure behavior, authenticate_customer(), print_step(), ATM Simulation CSC505 - Principles of Software Engineering  This program follows, Print a numbered activity that matches the UML Activity Diagram., Authenticate the customer using a PIN with a maximum of three attempts. (+53 more)

### Community 3 - "Authentication Service Code"
Cohesion: 0.08
Nodes (32): AuthenticationService, AuthenticationStateUnavailableError, Transactional card authentication with Redis-backed temporary state., Redis could not safely maintain authentication state., Authenticate one request inside a caller-owned database transaction., Return a generic denial or an expiring session; never persist input secrets., AuthenticationOutcome, AuthenticationRequest (+24 more)

### Community 4 - "ORM Domain Models"
Cohesion: 0.1
Nodes (35): Account, Persistent customer account and exact available balance., AuditEvent, Append-oriented operational audit record with secret-free structured details., Base, Base, Shared ORM metadata for BankFlow's application schema., Card (+27 more)

### Community 5 - "Foundation Validation"
Cohesion: 0.05
Nodes (48): Day 1 import, lint, hash and CLI checks, Initial admin-role setup attempt could not create roles; no database resources created, Migration downgrade must never run against application database, Autogeneration inspects bankflow schema; future models require metadata registration, Base metadata targets bankflow with stable constraint names, Migration bookkeeping must survive application-schema bootstrap and downgrade, Pytest configured for concise tracebacks after connection-argument exposure, Bounded connection pool, timeout, pre-ping and hidden SQL parameters (+40 more)

### Community 6 - "ATM Sequence Interactions"
Cohesion: 0.07
Nodes (46): Academic PIN check and three-failure session rejection, Account, ATM, 15 Balance, Bank System, 12 Check Balance(amount), 5 Check PIN, Customer (+38 more)

### Community 7 - "Configuration and Migrations"
Cohesion: 0.07
Nodes (34): validate_pin(), BaseSettings, Keep external environment overrides from changing test database selection., include_name(), Alembic environment using the same validated settings as the application., Autogeneration must not propose changes to unrelated schemas., run_migrations_online(), check_redis_health() (+26 more)

### Community 8 - "Database Migration Tests"
Cohesion: 0.07
Nodes (26): downgrade(), Create the application schema; domain tables follow in Day 3.  Revision ID: 0001, upgrade(), downgrade(), create core banking domain models  Revision ID: 0002 Revises: 0001, upgrade(), AbstractContextManager, database_engine() (+18 more)

### Community 9 - "ATM Workflow Requirements"
Cohesion: 0.08
Nodes (32): ATM System, Attempts >= 3?, Authenticate Customer: access granted, Bank / Account System, Bank checks sufficient funds, Debit Amount from Account, Check Account Balance, Close Account at zero balance (+24 more)

### Community 10 - "UML Sequence Diagrams"
Cohesion: 0.09
Nodes (28): Numbered activity panel, Sequence ATM lifeline, Authenticated / show menu, Check available account balance, Sequence Bank System lifeline, Dispense Cash after debit success, Check Balance, Account Closed for zero balance (+20 more)

### Community 11 - "UML Activity Review"
Cohesion: 0.09
Nodes (26): Activity arrow routing disagrees with numbered PIN and bank balance flow, Increment Failed Attempt Counter, Authenticate Customer, Bank Check Balance, Bank debit amount from account, Check Account Balance, Close Account automatically at zero balance, Display Transaction Complete / Updated Balance (+18 more)

### Community 12 - "Activity Diagram Details"
Cohesion: 0.1
Nodes (22): Activity arrow routing disagrees with numbered PIN and bank balance flow, Increment Failed Attempt Counter, Authenticate Customer, Bank Check Balance, Bank debit amount from account, Check Account Balance, Close Account automatically at zero balance, Display Transaction Complete / Updated Balance (+14 more)

### Community 13 - "ATM State Machine Behavior"
Cohesion: 0.15
Nodes (18): Authenticated: showMenu, Check Balance: validateAmount, Account Closed: displayClosedMsg, Transaction Complete, Final State, PIN format validation, Idle: displayWelcome / clearScreen, Increment Attempts: incrementCounter (+10 more)

### Community 14 - "UML State Diagram"
Cohesion: 0.15
Nodes (17): Account Active / transaction complete, Authenticated Customer, Check Balance, Account Closed, ATM UML State Machine Diagram, Eject Card, Final State / End of Session, Idle / waiting for card (+9 more)

### Community 15 - "PIN Hashing Security"
Cohesion: 0.19
Nodes (14): _decode(), _encode(), hash_pin(), InvalidPinError, Scrypt PIN hashing with a versioned, self-describing storage format., A PIN failed the public four-digit input contract., Return a salted scrypt hash; the plaintext PIN is never retained., Verify a PIN in constant time and reject malformed hashes safely. (+6 more)

### Community 16 - "Architecture Decisions"
Cohesion: 0.12
Nodes (16): ADR-001 Repository and Runtime Foundation, ADR-004 Exact and Traceable Banking Domain Model, Application-Generated UUID Identity, BankFlow Service Endpoint Reference, Dedicated BankFlow Data-Lab Container, Exact NUMERIC and Decimal Money Policy, Restrictive Financial History Retention, Avoid Academic Prototype Floating-Point Defects (+8 more)

### Community 17 - "Project Design Rationale"
Cohesion: 0.13
Nodes (16): ATM System Design and Implementation Report, BankFlow Transaction Service, BankFlow Withdrawal Flow, Classroom-to-Production ATM Security Gap, Configurable Demo Business Rules, Four ATM Execution Scenarios, Kafka Event Backbone, Kafka Broker Metadata Validation Gap (+8 more)

### Community 18 - "Database Provisioning"
Cohesion: 0.25
Nodes (13): admin_sql(), main(), provision(), Provision or rotate local Day 2 database access without resetting data., Render one local environment file without exposing its password., Replace exactly one setting while preserving every other local choice., Rotate both owner passwords and atomically replace their ignored files., render_environment() (+5 more)

### Community 19 - "Legacy Execution Scenario"
Cohesion: 0.18
Nodes (11): Account status ACTIVE, Authenticate Customer: access granted, Starting balance $500.00, Cash dispensed $100.00, Correct PIN 2468 on third input, End ATM Session and remove card, Incorrect PIN 1111: failed attempts 1/3, Updated balance $400.00 (+3 more)

### Community 20 - "Two-Stage Platform"
Cohesion: 0.33
Nodes (6): Operational and Analytics Workload Isolation, BankFlow Two-Stage Architecture, BankFlow Version 1 Application and Event Platform, BankFlow Version 2 Streaming Lakehouse Platform, Iceberg Bronze Silver Gold Layers, Separation of Concerns

### Community 21 - "Repository Boundary ADR"
Cohesion: 0.4
Nodes (6): ADR-005 Session-Bound Repository Boundary, Repository Preparation for Atomic Transactions, Caller-Owned Database Unit of Work, Account Row Lock and Version Check, Stable Repository Exceptions, Stable Newest-First Transaction History

### Community 22 - "Lakehouse Roadmap"
Cohesion: 0.4
Nodes (5): Planned immutable Iceberg Bronze events, Planned Gold business metrics, Planned standardized Silver datasets, Planned synthetic event generator, Planned V2 streaming lakehouse

### Community 23 - "Environment Import Check"
Cohesion: 0.5
Nodes (3): main(), Check Day 1 imports without opening network connections or loading secrets., Return nonzero if the selected interpreter or an application import fails.

### Community 24 - "Domain Metadata Tests"
Cohesion: 0.5
Nodes (0): 

### Community 25 - "Activity Diagram Swimlanes"
Cohesion: 0.5
Nodes (4): ATM System swimlane, Bank / Account System swimlane, Customer swimlane, Numbered ATM UML activity diagram

### Community 26 - "Diagram Swimlane Duplicate"
Cohesion: 0.5
Nodes (4): ATM System swimlane, Bank / Account System swimlane, Customer swimlane, Numbered ATM UML activity diagram

### Community 27 - "Delivery Roadmap"
Cohesion: 1.0
Nodes (2): BankFlow Delivery Sequence, Transaction Services and Streamlit UI Remain Planned

### Community 28 - "Kafka Consistency Risk"
Cohesion: 1.0
Nodes (2): Kafka and Database Consistency Risk, Outbox Pattern as Future Reliability Option

### Community 29 - "Safe Database URL"
Cohesion: 1.0
Nodes (1): Build a URL without interpolating or manually escaping credentials.

### Community 30 - "Development Tooling"
Cohesion: 1.0
Nodes (1): pytest and Ruff development tooling

### Community 31 - "Python Dependency Lock"
Cohesion: 1.0
Nodes (1): Windows Python 3.14 dependency snapshot

### Community 32 - "UI Lockout Conflict"
Cohesion: 1.0
Nodes (1): Temporary card lockout in UI design

### Community 33 - "Fictional Data Scope"
Cohesion: 1.0
Nodes (1): Educational fictional data only

### Community 34 - "Event Secret Exclusion"
Cohesion: 1.0
Nodes (1): PINs and hashes excluded from events

### Community 35 - "Dedicated Container Decision"
Cohesion: 1.0
Nodes (1): Dedicated user-provided lab container replaces shared lab

### Community 36 - "Session End Node"
Cohesion: 1.0
Nodes (1): End ATM Session

### Community 37 - "Duplicate Session End Node"
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
- **165 isolated node(s):** `ATM Simulation CSC505 - Principles of Software Engineering  This program follows`, `Print a numbered activity that matches the UML Activity Diagram.`, `Authenticate the customer using a PIN with a maximum of three attempts.`, `Request and validate a withdrawal amount.`, `Run one complete ATM session.` (+160 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Delivery Roadmap`** (2 nodes): `BankFlow Delivery Sequence`, `Transaction Services and Streamlit UI Remain Planned`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Kafka Consistency Risk`** (2 nodes): `Kafka and Database Consistency Risk`, `Outbox Pattern as Future Reliability Option`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Safe Database URL`** (1 nodes): `Build a URL without interpolating or manually escaping credentials.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Development Tooling`** (1 nodes): `pytest and Ruff development tooling`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Python Dependency Lock`** (1 nodes): `Windows Python 3.14 dependency snapshot`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `UI Lockout Conflict`** (1 nodes): `Temporary card lockout in UI design`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Fictional Data Scope`** (1 nodes): `Educational fictional data only`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Event Secret Exclusion`** (1 nodes): `PINs and hashes excluded from events`
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