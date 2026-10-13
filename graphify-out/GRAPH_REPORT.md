# Graph Report - .  (2026-10-12)

## Corpus Check
- 143 files · ~358,412 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1107 nodes · 1845 edges · 70 communities detected
- Extraction: 70% EXTRACTED · 29% INFERRED · 0% AMBIGUOUS · INFERRED: 540 edges (avg confidence: 0.65)
- Token cost: unavailable; agent execution does not expose actual token usage, and unknown is not zero.

## Community Hubs (Navigation)
- [[_COMMUNITY_Kafka Consumer Implementation|Kafka Consumer Implementation]]
- [[_COMMUNITY_Academic CLI Traceability|Academic CLI Traceability]]
- [[_COMMUNITY_Repository Layer|Repository Layer]]
- [[_COMMUNITY_Post-Commit Runtime Events|Post-Commit Runtime Events]]
- [[_COMMUNITY_Account Services|Account Services]]
- [[_COMMUNITY_Event Schemas and Factories|Event Schemas and Factories]]
- [[_COMMUNITY_Foundation Validation|Foundation Validation]]
- [[_COMMUNITY_Withdrawal Activity Flow|Withdrawal Activity Flow]]
- [[_COMMUNITY_Core and Event ORM Models|Core and Event ORM Models]]
- [[_COMMUNITY_PIN Authentication UML|PIN Authentication UML]]
- [[_COMMUNITY_Authentication and Redis|Authentication and Redis]]
- [[_COMMUNITY_Transaction Service Decisions|Transaction Service Decisions]]
- [[_COMMUNITY_Kafka Producer Implementation|Kafka Producer Implementation]]
- [[_COMMUNITY_Database Provisioning and Tests|Database Provisioning and Tests]]
- [[_COMMUNITY_PIN Validation Flow|PIN Validation Flow]]
- [[_COMMUNITY_dbt Analytics Layer|dbt Analytics Layer]]
- [[_COMMUNITY_Kafka Consumer Architecture|Kafka Consumer Architecture]]
- [[_COMMUNITY_Alembic Database Runtime|Alembic Database Runtime]]
- [[_COMMUNITY_UML Execution Trace|UML Execution Trace]]
- [[_COMMUNITY_ATM State Machine Logic|ATM State Machine Logic]]
- [[_COMMUNITY_Event Contract Architecture|Event Contract Architecture]]
- [[_COMMUNITY_ATM State Diagram|ATM State Diagram]]
- [[_COMMUNITY_Kafka Consumer Architecture 22|Kafka Consumer Architecture 22]]
- [[_COMMUNITY_PIN Authentication UML 23|PIN Authentication UML 23]]
- [[_COMMUNITY_Kafka Producer Architecture|Kafka Producer Architecture]]
- [[_COMMUNITY_Streamlit Interface Boundary|Streamlit Interface Boundary]]
- [[_COMMUNITY_Software Engineering Lessons|Software Engineering Lessons]]
- [[_COMMUNITY_Settings Validation Tests|Settings Validation Tests]]
- [[_COMMUNITY_Core Domain Decision|Core Domain Decision]]
- [[_COMMUNITY_Exact Money Requests|Exact Money Requests]]
- [[_COMMUNITY_Repository Boundary Decision|Repository Boundary Decision]]
- [[_COMMUNITY_Live ORM Persistence Tests|Live ORM Persistence Tests]]
- [[_COMMUNITY_Kafka Analytics Pipeline|Kafka Analytics Pipeline]]
- [[_COMMUNITY_V2 Lakehouse Plan|V2 Lakehouse Plan]]
- [[_COMMUNITY_Foundation and Environment|Foundation and Environment]]
- [[_COMMUNITY_ORM Metadata Tests|ORM Metadata Tests]]
- [[_COMMUNITY_Initial Alembic Migration|Initial Alembic Migration]]
- [[_COMMUNITY_Environment Import Check|Environment Import Check]]
- [[_COMMUNITY_UML Swimlane Diagram|UML Swimlane Diagram]]
- [[_COMMUNITY_UML Activity Swimlanes|UML Activity Swimlanes]]
- [[_COMMUNITY_Phase 2 Analytics UI|Phase 2 Analytics UI]]
- [[_COMMUNITY_Test Environment Isolation|Test Environment Isolation]]
- [[_COMMUNITY_Transaction Engine ADR|Transaction Engine ADR]]
- [[_COMMUNITY_Demo Reset Boundary|Demo Reset Boundary]]
- [[_COMMUNITY_Withdrawal Page|Withdrawal Page]]
- [[_COMMUNITY_Deposit Page|Deposit Page]]
- [[_COMMUNITY_Redis Client Boundary|Redis Client Boundary]]
- [[_COMMUNITY_Demo Identifiers|Demo Identifiers]]
- [[_COMMUNITY_Kafka Extension Boundary|Kafka Extension Boundary]]
- [[_COMMUNITY_Streamlit Entry Page|Streamlit Entry Page]]
- [[_COMMUNITY_Dashboard Page|Dashboard Page]]
- [[_COMMUNITY_History Page|History Page]]
- [[_COMMUNITY_Kafka Broker Connectivity|Kafka Broker Connectivity]]
- [[_COMMUNITY_Kafka Failure Handling|Kafka Failure Handling]]
- [[_COMMUNITY_Kafka Delivery Guarantees|Kafka Delivery Guarantees]]
- [[_COMMUNITY_Development Tooling|Development Tooling]]
- [[_COMMUNITY_Dependency Lock|Dependency Lock]]
- [[_COMMUNITY_UI Lockout Design|UI Lockout Design]]
- [[_COMMUNITY_Fictional Data Policy|Fictional Data Policy]]
- [[_COMMUNITY_Event Secret Exclusion|Event Secret Exclusion]]
- [[_COMMUNITY_Dedicated Lab Container|Dedicated Lab Container]]
- [[_COMMUNITY_Session Ending|Session Ending]]
- [[_COMMUNITY_ATM Session End|ATM Session End]]
- [[_COMMUNITY_Day 5 Scope Boundary|Day 5 Scope Boundary]]
- [[_COMMUNITY_Day 6 Kafka Deferral|Day 6 Kafka Deferral]]
- [[_COMMUNITY_Kafka Delivery Sequence|Kafka Delivery Sequence]]
- [[_COMMUNITY_Secret Masking|Secret Masking]]
- [[_COMMUNITY_Accessible Status Design|Accessible Status Design]]
- [[_COMMUNITY_Deterministic Kafka Ordering|Deterministic Kafka Ordering]]
- [[_COMMUNITY_Safe Database URL Construction|Safe Database URL Construction]]

## God Nodes (most connected - your core abstractions)
1. `Settings` - 49 edges
2. `Versioned Kafka event construction, publication, and consumption.` - 42 edges
3. `BankFlowRuntime` - 24 edges
4. `TransactionService` - 20 edges
5. `Account` - 17 edges
6. `AccountRepository` - 17 edges
7. `RepositoryNotFoundError` - 17 edges
8. `ATM` - 17 edges
9. `FakeMessage` - 17 edges
10. `FakeConsumer` - 17 edges

## Surprising Connections (you probably didn't know these)
- `Planned validated withdrawal workflow` --semantically_similar_to--> `request_withdrawal()`  [INFERRED] [semantically similar]
  docs/PRODUCT_REQUIREMENTS.md → docs/original-college-project/atm_simulation.py
- `Restrictive Financial History with Durable Audit Rows` --conceptually_related_to--> `Secret-Free Authentication Audit Events`  [INFERRED]
  docs/DAY3_VALIDATION.md → src/bankflow/services/auth_service.py
- `Atomic Expiring Failed-Attempt Counter` --locks--> `Durable PostgreSQL Card Lockout`  [EXTRACTED]
  src/bankflow/cache/redis_client.py → docs/architecture/ADR-006-authentication-state.md
- `Day 4 PostgreSQL Row-Locking Foundation` --conceptually_related_to--> `Optional Card Row Lock Lookup`  [INFERRED]
  docs/DAY4_VALIDATION.md → src/bankflow/repositories/card_repository.py
- `Day 4 Caller-Owned Repository Boundary` --rationale_for--> `Caller-Owned Authentication Transaction`  [INFERRED]
  docs/DAY4_VALIDATION.md → src/bankflow/services/auth_service.py

## Hyperedges (group relationships)
- **Transactional Card Authentication Flow** — authentication_request_contract, authentication_service, card_row_lock_lookup, constant_time_pin_verification, authentication_state_store, authentication_result_contract [EXTRACTED 1.00]
- **Opted-in migration reversal is isolated from application data by credentials, role grants and database guards** — day2_test_database, day2_test_guard, day2_role_isolation, day2_migration_validation, day2_app_protection [EXTRACTED 1.00]
- **Academic requirements/model/code/execution traceability** — academic_trace, uml_state, uml_activity, uml_sequence, prototype, manual_scenarios [EXTRACTED 1.00]
- **Schema bootstrap keeps migration bookkeeping independent while refusing destructive cascade** — migration, day2_schema, day2_public_version, day2_bootstrap_rationale, day2_no_cascade [EXTRACTED 1.00]
- **Exact Money Validation Flow** — positive_money_contract, withdrawal_request_contract, deposit_request_contract, schema_accepts_positive_decimal_cents_test, schema_rejects_unsafe_money_test, day6_exact_money_acceptance, adr007_legacy_money_defect_rationale [EXTRACTED 1.00]
- **Locked Atomic Financial Operation Flow** — authorized_account_resolution, account_row_locking, withdrawal_workflow, deposit_workflow, persisted_transaction_record, audit_event_append, caller_owned_service_uow, transaction_failure_rollback_test [EXTRACTED 1.00]
- **Redis-Backed Authentication Contract** — day7_validation_redis_authority, adr8_external_session_authority, adr8_transient_secret_handling [EXTRACTED 1.00]
- **Post-Commit Event Publication Flow** — day9_bankflow_runtime, architecture_postgresql_source_of_truth, day9_kafka_event_producer, architecture_transaction_events_topic [EXTRACTED 1.00]
- **Acknowledged Idempotent Delivery Pattern** — adr010_idempotent_all_ack_configuration, adr010_bounded_delivery_callback, day9_delivery_receipts [EXTRACTED 1.00]
- **Academic ATM Requirements-to-Evidence Traceability Chain** — secure_withdrawal_workflow, three_complementary_uml_views, numbered_artifact_traceability, four_atm_execution_scenarios [EXTRACTED 1.00]
- **Consume Validate Persist Commit Flow** — architecture_kafka_topic, validation_schema, validation_consumed_events, validation_offset_order [EXTRACTED 1.00]
- **Idempotent Replay Pattern** — adr011_at_least_once, validation_event_id_guard, validation_position_guard, adr011_safe_replay [EXTRACTED 1.00]
- **Invalid Message Progress and Privacy** — adr011_validation_policy, adr011_invalid_handling, adr011_structured_logging, adr011_no_dlt [EXTRACTED 1.00]
- **Consumed Event Store to Version 1 Analytics Marts** — adr012_consumed_events_source, dbt_readme_transaction_staging_snapshot, dbt_readme_authentication_staging_snapshot, dbt_readme_terminal_transaction_fact, adr012_daily_transaction_mart_grain, adr012_authentication_mart_grain, adr012_account_activity_mart_grain [EXTRACTED 1.00]
- **Day 11 Analytics Quality and Validation Evidence** — day11_source_contract_tests, day11_generic_model_tests, day11_singular_reconciliation_tests, day11_controlled_nine_event_fixture, day11_dual_database_build_validation, day11_generated_dbt_documentation [EXTRACTED 1.00]
- **Day 12 Analytics Orchestration Handoff** — memory_day12_handoff, task_day12_airflow_analytics_dag, task_day12_health_freshness_quality_checks, task_day12_retries_failure_logging, adr012_staging_table_materialization, adr012_table_mart_materialization [EXTRACTED 1.00]

## Communities

### Community 0 - "Kafka Consumer Implementation"
Cohesion: 0.05
Nodes (56): BaseSettings, consumer_config(), ConsumeResult, ConsumeStatus, EventPersistenceError, EventStore, from_settings(), KafkaConsumerError (+48 more)

### Community 1 - "Academic CLI Traceability"
Cohesion: 0.03
Nodes (72): Academic simulation is not production banking security, Numbered UML activities traced to executable output, Academic zero-balance closure behavior, authenticate_customer(), print_step(), ATM Simulation CSC505 - Principles of Software Engineering  This program follows, Print a numbered activity that matches the UML Activity Diagram., Authenticate the customer using a PIN with a maximum of three attempts. (+64 more)

### Community 2 - "Repository Layer"
Cohesion: 0.06
Nodes (34): AccountRepository, Account lookups and exact-balance persistence., Persist account state while the caller owns commit and rollback., CustomerRepository, Customer persistence queries., Read customers without owning the surrounding transaction., DemoDataUnavailableError, DemoResetResult (+26 more)

### Community 3 - "Post-Commit Runtime Events"
Cohesion: 0.06
Nodes (45): from_settings(), AccountSummary, _authentication_subject(), BankFlowRuntime, DemoCardOption, from_env(), Thin application runtime used by Streamlit pages., Publish committed facts without changing an already completed operation. (+37 more)

### Community 4 - "Account Services"
Cohesion: 0.11
Nodes (40): AccountBalance, A consistent balance snapshot and its persisted inquiry transaction., AccountAuthorizationError, AccountService, AccountUnavailableError, BankingServiceError, Authorized account lookup and persisted balance inquiry., Base exception for stable transaction-service failures. (+32 more)

### Community 5 - "Event Schemas and Factories"
Cohesion: 0.09
Nodes (48): balance_viewed_event(), deserialize_event(), _envelope(), event_from_authentication_result(), event_from_transaction_result(), EventFactoryError, Create and serialize schema-version-1 events from application-service results., Return compact UTF-8 JSON; Decimal values remain exact JSON strings. (+40 more)

### Community 6 - "Foundation Validation"
Cohesion: 0.05
Nodes (48): Day 1 import, lint, hash and CLI checks, Initial admin-role setup attempt could not create roles; no database resources created, Migration downgrade must never run against application database, Autogeneration inspects bankflow schema; future models require metadata registration, Base metadata targets bankflow with stable constraint names, Migration bookkeeping must survive application-schema bootstrap and downgrade, Pytest configured for concise tracebacks after connection-argument exposure, Bounded connection pool, timeout, pre-ping and hidden SQL parameters (+40 more)

### Community 7 - "Withdrawal Activity Flow"
Cohesion: 0.05
Nodes (48): Activity arrow routing disagrees with numbered PIN and bank balance flow, Increment Failed Attempt Counter, Authenticate Customer, Bank Check Balance, Bank debit amount from account, Check Account Balance, Close Account automatically at zero balance, Display Transaction Complete / Updated Balance (+40 more)

### Community 8 - "Core and Event ORM Models"
Cohesion: 0.11
Nodes (33): Account, Account-operation responses exposed by the service layer., AuditEvent, Append-oriented operational audit record with secret-free structured details., Base, Base, Shared ORM metadata for BankFlow's application schema., Card (+25 more)

### Community 9 - "PIN Authentication UML"
Cohesion: 0.08
Nodes (41): Academic PIN check and three-failure session rejection, Authenticated / show menu, Check Balance, Account Closed for zero balance, Transaction Complete for positive balance, Customer Rejected / retain card, Account Status, Update Balance by subtracting amount (+33 more)

### Community 10 - "Authentication and Redis"
Cohesion: 0.08
Nodes (38): ADR-006 Split Authentication State by Durability, Four-ASCII-Digit PIN Contract, Authentication Outcome Vocabulary, Secret-Safe Authentication Request Contract, Secret-Safe Authentication Result Contract, Transactional Authentication Service, Identifier-Only Authentication Session Payload, Redis Authentication State Store (+30 more)

### Community 11 - "Transaction Service Decisions"
Cohesion: 0.08
Nodes (36): Account Authorization Error, Account Balance Snapshot Contract, Account Row Locking For Consistent Operations, Account Unavailable Error, Audit Rows Share The Database Transaction, Caller-Owned SQLAlchemy Transaction Decision, Persist Declined Insufficient-Funds Attempts, Audit Event Append Helper (+28 more)

### Community 12 - "Kafka Producer Implementation"
Cohesion: 0.12
Nodes (23): DeliveryReceipt, EventPublicationError, KafkaDeliveryError, KafkaEventProducer, KafkaUnavailableError, _partition_key(), producer_config(), Synchronous, acknowledged Kafka publication for committed application events. (+15 more)

### Community 13 - "Database Provisioning and Tests"
Cohesion: 0.09
Nodes (26): downgrade(), create consumed event store  Revision ID: 0003 Revises: 0002, upgrade(), admin_sql(), main(), provision(), Provision or rotate local Day 2 database access without resetting data., Render one local environment file without exposing its password. (+18 more)

### Community 14 - "PIN Validation Flow"
Cohesion: 0.08
Nodes (32): ATM System, Attempts >= 3?, Authenticate Customer: access granted, Bank / Account System, Bank checks sufficient funds, Debit Amount from Account, Check Account Balance, Close Account at zero balance (+24 more)

### Community 15 - "dbt Analytics Layer"
Cohesion: 0.08
Nodes (32): Account Activity Mart Grain: Date and Known Account, Avoid Persistent View Dependencies that Block Alembic Rollback, Authentication Mart Grain: Date, Event Type, Outcome, PostgreSQL bankflow.consumed_events Source, Daily Transaction Mart Grain: Date, Currency, Transaction Type, Exact Money as numeric(18, 2), Intermediate Transaction Metrics View, Materialized Staging Snapshot Tables (+24 more)

### Community 16 - "Kafka Consumer Architecture"
Cohesion: 0.09
Nodes (23): Kafka At Least Once Delivery, Terminal Outcome Offset Policy, ADR-011 Consumer Event Store Decision, Atomic Replay Deduplication, Effectively Once Persistence, Independent Consumed Event Store, Invalid Message Rejection, No Day 10 Dead Letter Topic (+15 more)

### Community 17 - "Alembic Database Runtime"
Cohesion: 0.1
Nodes (15): create core banking domain models  Revision ID: 0002 Revises: 0001, upgrade(), database_engine(), migrated_database(), create_database_engine(), Lazy SQLAlchemy engine construction; the caller owns engine disposal., Create a pool without opening a connection until first use., run_migrations_online() (+7 more)

### Community 18 - "UML Execution Trace"
Cohesion: 0.13
Nodes (19): Numbered activity panel, Sequence ATM lifeline, Check available account balance, Sequence Bank System lifeline, Dispense Cash after debit success, Sequence Customer actor, Sequence Account Database lifeline, Debit account and update database balance (+11 more)

### Community 19 - "ATM State Machine Logic"
Cohesion: 0.15
Nodes (18): Authenticated: showMenu, Check Balance: validateAmount, Account Closed: displayClosedMsg, Transaction Complete, Final State, PIN format validation, Idle: displayWelcome / clearScreen, Increment Attempts: incrementCounter (+10 more)

### Community 20 - "Event Contract Architecture"
Cohesion: 0.11
Nodes (18): Avoid Revealing Unknown Card Existence, Authentication Subject Identifier Policy, Closed BankFlowEvent Envelope, Kafka Delivery and Database-Broker Atomicity Limit, Discriminated Transaction and Authentication Payloads, ADR-009 Versioned and Secret-Free Application Event Contract, Distinct Event and Transaction Identities, Exact Decimal Money as JSON Strings (+10 more)

### Community 21 - "ATM State Diagram"
Cohesion: 0.15
Nodes (17): Account Active / transaction complete, Authenticated Customer, Check Balance, Account Closed, ATM UML State Machine Diagram, Eject Card, Final State / End of Session, Idle / waiting for card (+9 more)

### Community 22 - "Kafka Consumer Architecture 22"
Cohesion: 0.16
Nodes (15): Day 10 Kafka Consumer Release, Dedicated bankflow Container, Kafka Endpoint 127.0.0.1:9093, Alembic Revision 0003, Operational Consumer Contract, Operational Consumer Runtime, Kafka 3.7.1 Runtime, bankflow.consumed_events (+7 more)

### Community 23 - "PIN Authentication UML 23"
Cohesion: 0.19
Nodes (14): Account Active: transaction complete; display new balance, Authenticated: showMenu, Check Balance after withdrawal, Account Closed: display closed message, Final State: end of session, Idle: waiting for card; display welcome, Increment Attempts: increase failed attempt counter, Initial State (+6 more)

### Community 24 - "Kafka Producer Architecture"
Cohesion: 0.14
Nodes (14): Acknowledged Post-Commit Kafka Publication, Committed Banking Result Remains Authoritative, Injectable EventPublisher Abstraction, Future Transactional Outbox, Non-Atomic Commit-to-Broker Gap, Runtime Commit Boundary, Aggregate UUID Partition Keys, BankFlowRuntime (+6 more)

### Community 25 - "Streamlit Interface Boundary"
Cohesion: 0.2
Nodes (11): Balance Inquiry Rerun Control, Exact-Money Service Adapter, External Redis Session Authority, Infrastructure-Only Streamlit Cache, Rationale: Preserve PostgreSQL and Redis Authority, Rationale: Prevent Duplicate Inquiry Transactions, Thin Streamlit Interface Boundary, Day 7 Live Acceptance Path (+3 more)

### Community 26 - "Software Engineering Lessons"
Cohesion: 0.18
Nodes (11): ATM System Design and Implementation Report, Classroom-to-Production ATM Security Gap, Four ATM Execution Scenarios, Numbered Design-to-Execution Traceability, Waterfall Prototyping and Agile Tradeoffs, Requirements Before Implementation, Authenticated ATM Withdrawal Workflow, Security Across the Software Lifecycle (+3 more)

### Community 27 - "Settings Validation Tests"
Cohesion: 0.25
Nodes (0): 

### Community 28 - "Core Domain Decision"
Cohesion: 0.29
Nodes (7): ADR-004 Exact and Traceable Banking Domain Model, Application-Generated UUID Identity, Exact NUMERIC and Decimal Money Policy, Restrictive Financial History Retention, Avoid Academic Prototype Floating-Point Defects, Idempotent Fixed Demo Seed, Tokenized Card and Salted PIN-Hash Persistence

### Community 29 - "Exact Money Requests"
Cohesion: 0.29
Nodes (7): Day 7 Must Convert UI Values Deliberately, Day 6 Exact Money Acceptance, Deposit Request Contract, Strict Positive Decimal Money Contract, Positive Decimal Cents Acceptance Test, Unsafe Money Rejection Test, Withdrawal Request Contract

### Community 30 - "Repository Boundary Decision"
Cohesion: 0.4
Nodes (6): ADR-005 Session-Bound Repository Boundary, Repository Preparation for Atomic Transactions, Caller-Owned Database Unit of Work, Account Row Lock and Version Check, Stable Repository Exceptions, Stable Newest-First Transaction History

### Community 31 - "Live ORM Persistence Tests"
Cohesion: 0.47
Nodes (4): _delete_graph(), Live Day 3 persistence checks, gated by BANKFLOW_RUN_DB_TESTS=1., test_demo_seed_is_complete_idempotent_and_never_stores_plain_pin(), test_tables_relationships_timestamps_and_decimal_round_trip()

### Community 32 - "Kafka Analytics Pipeline"
Cohesion: 0.33
Nodes (6): Airflow and dbt Analytics Path, Transaction Analytics Decoupling Rationale, Operational Event Store, bankflow.transaction.events Topic, Python Kafka Consumer, Version 1 Kafka Transport

### Community 33 - "V2 Lakehouse Plan"
Cohesion: 0.4
Nodes (5): Planned immutable Iceberg Bronze events, Planned Gold business metrics, Planned standardized Silver datasets, Planned synthetic event generator, Planned V2 streaming lakehouse

### Community 34 - "Foundation and Environment"
Cohesion: 0.4
Nodes (5): ADR-001 Repository and Runtime Foundation, Installable src/bankflow Package Layout, Legacy ATM Prototype Limitations, Original Academic ATM Archive, Preserved Academic Source Provenance

### Community 35 - "ORM Metadata Tests"
Cohesion: 0.4
Nodes (0): 

### Community 36 - "Initial Alembic Migration"
Cohesion: 0.5
Nodes (1): Create the application schema; domain tables follow in Day 3.  Revision ID: 0001

### Community 37 - "Environment Import Check"
Cohesion: 0.5
Nodes (3): main(), Check Day 1 imports without opening network connections or loading secrets., Return nonzero if the selected interpreter or an application import fails.

### Community 38 - "UML Swimlane Diagram"
Cohesion: 0.5
Nodes (4): ATM System swimlane, Bank / Account System swimlane, Customer swimlane, Numbered ATM UML activity diagram

### Community 39 - "UML Activity Swimlanes"
Cohesion: 0.5
Nodes (4): ATM System swimlane, Bank / Account System swimlane, Customer swimlane, Numbered ATM UML activity diagram

### Community 40 - "Phase 2 Analytics UI"
Cohesion: 0.67
Nodes (4): Event-Stream Transaction Monitoring, Phase 2 Analytics Screens, Live Platform Status, Real Service Backing Rule

### Community 41 - "Test Environment Isolation"
Cohesion: 0.67
Nodes (1): Keep external environment overrides from changing test database selection.

### Community 42 - "Transaction Engine ADR"
Cohesion: 0.67
Nodes (3): ADR-007 Exact And Atomic Service Boundary, Correct Legacy Float And Fractional-Cent Defects, Day 6 Transaction Engine Validation Evidence

### Community 43 - "Demo Reset Boundary"
Cohesion: 0.67
Nodes (3): Fixed Demo Reset Boundary, Rationale: Make Portfolio Demonstrations Repeatable, Atomic Fixed-Demo Reset

### Community 44 - "Withdrawal Page"
Cohesion: 0.67
Nodes (1): Authenticated withdrawal form.

### Community 45 - "Deposit Page"
Cohesion: 0.67
Nodes (1): Authenticated deposit form.

### Community 46 - "Redis Client Boundary"
Cohesion: 1.0
Nodes (2): Bounded-Time Authenticated Redis Client, Redis Reachability Health Check

### Community 47 - "Demo Identifiers"
Cohesion: 1.0
Nodes (1): Stable identifiers and public credentials for the fictional demo account.

### Community 48 - "Kafka Extension Boundary"
Cohesion: 1.0
Nodes (2): Future Kafka Extension Below Service Boundary, Rationale: Add Kafka Without Changing UI Forms

### Community 49 - "Streamlit Entry Page"
Cohesion: 1.0
Nodes (1): BankFlow welcome and authentication screen.

### Community 50 - "Dashboard Page"
Cohesion: 1.0
Nodes (1): Authenticated BankFlow account dashboard.

### Community 51 - "History Page"
Cohesion: 1.0
Nodes (1): Authenticated transaction-history page.

### Community 52 - "Kafka Broker Connectivity"
Cohesion: 1.0
Nodes (2): host.docker.internal Broker Advertisement Fix, Live Produce and Consume Round Trip

### Community 53 - "Kafka Failure Handling"
Cohesion: 1.0
Nodes (2): Broker Outage Commit Preservation, Stable Kafka Transport Exceptions

### Community 54 - "Kafka Delivery Guarantees"
Cohesion: 1.0
Nodes (2): Bounded Delivery Callback, Idempotent All-Acknowledgement Producer Configuration

### Community 55 - "Development Tooling"
Cohesion: 1.0
Nodes (1): pytest and Ruff development tooling

### Community 56 - "Dependency Lock"
Cohesion: 1.0
Nodes (1): Windows Python 3.14 dependency snapshot

### Community 57 - "UI Lockout Design"
Cohesion: 1.0
Nodes (1): Temporary card lockout in UI design

### Community 58 - "Fictional Data Policy"
Cohesion: 1.0
Nodes (1): Educational fictional data only

### Community 59 - "Event Secret Exclusion"
Cohesion: 1.0
Nodes (1): PINs and hashes excluded from events

### Community 60 - "Dedicated Lab Container"
Cohesion: 1.0
Nodes (1): Dedicated user-provided lab container replaces shared lab

### Community 61 - "Session Ending"
Cohesion: 1.0
Nodes (1): End ATM Session

### Community 62 - "ATM Session End"
Cohesion: 1.0
Nodes (1): End ATM Session

### Community 63 - "Day 5 Scope Boundary"
Cohesion: 1.0
Nodes (1): Day 5 Defers Banking Operations To Day 6

### Community 64 - "Day 6 Kafka Deferral"
Cohesion: 1.0
Nodes (1): Day 6 Kafka Deferral

### Community 65 - "Kafka Delivery Sequence"
Cohesion: 1.0
Nodes (1): Kafka Follows Day 8 Contract And Day 9 Integration

### Community 66 - "Secret Masking"
Cohesion: 1.0
Nodes (1): Transient Masked Secret Handling

### Community 67 - "Accessible Status Design"
Cohesion: 1.0
Nodes (1): Accessible Text-Bearing Status Design

### Community 68 - "Deterministic Kafka Ordering"
Cohesion: 1.0
Nodes (1): Deterministic Aggregate Ordering

### Community 69 - "Safe Database URL Construction"
Cohesion: 1.0
Nodes (1): Build a URL without interpolating or manually escaping credentials.

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
- **270 isolated node(s):** `ATM Simulation CSC505 - Principles of Software Engineering  This program follows`, `Print a numbered activity that matches the UML Activity Diagram.`, `Authenticate the customer using a PIN with a maximum of three attempts.`, `Request and validate a withdrawal amount.`, `Run one complete ATM session.` (+265 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Redis Client Boundary`** (2 nodes): `Bounded-Time Authenticated Redis Client`, `Redis Reachability Health Check`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Demo Identifiers`** (2 nodes): `Stable identifiers and public credentials for the fictional demo account.`, `demo.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Kafka Extension Boundary`** (2 nodes): `Future Kafka Extension Below Service Boundary`, `Rationale: Add Kafka Without Changing UI Forms`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Streamlit Entry Page`** (2 nodes): `app.py`, `BankFlow welcome and authentication screen.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Page`** (2 nodes): `Authenticated BankFlow account dashboard.`, `1_Dashboard.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `History Page`** (2 nodes): `Authenticated transaction-history page.`, `4_Transaction_History.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Kafka Broker Connectivity`** (2 nodes): `host.docker.internal Broker Advertisement Fix`, `Live Produce and Consume Round Trip`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Kafka Failure Handling`** (2 nodes): `Broker Outage Commit Preservation`, `Stable Kafka Transport Exceptions`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Kafka Delivery Guarantees`** (2 nodes): `Bounded Delivery Callback`, `Idempotent All-Acknowledgement Producer Configuration`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Development Tooling`** (1 nodes): `pytest and Ruff development tooling`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dependency Lock`** (1 nodes): `Windows Python 3.14 dependency snapshot`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `UI Lockout Design`** (1 nodes): `Temporary card lockout in UI design`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Fictional Data Policy`** (1 nodes): `Educational fictional data only`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Event Secret Exclusion`** (1 nodes): `PINs and hashes excluded from events`
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
- **Thin community `Deterministic Kafka Ordering`** (1 nodes): `Deterministic Aggregate Ordering`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Safe Database URL Construction`** (1 nodes): `Build a URL without interpolating or manually escaping credentials.`
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