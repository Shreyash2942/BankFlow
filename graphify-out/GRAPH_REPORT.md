# Graph Report - BankFlow  (2026-09-24)


## Day 2 completion update

BankFlow now has validated settings, lazy SQLAlchemy engines, transaction-scoped sessions, a safe PostgreSQL health command, isolated application/test databases, and Alembic revision `0001`. The full suite passes 17 tests. Domain tables and services remain planned for Day 3 and later. Local credential values are excluded from this graph.

The final recheck also exercised a stopped PostgreSQL service. Generated local passwords were rotated afterward, detailed pytest tracebacks were shortened, and guarded credential rotation was documented. Redis authentication and Kafka metadata remain future milestone checks.

## Corpus Check
- 63 files · ~33,379 readable words (raw detector estimate: 330,272, including binary assets)
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 547 nodes · 749 edges · 25 communities detected
- Extraction: 90% EXTRACTED · 9% INFERRED · 1% AMBIGUOUS · INFERRED: 65 edges (avg confidence: 0.83)
- Actual token usage and financial cost: unavailable; not zero. See `cost.json`.

## Community Hubs (Navigation)
- [Database Foundation Code](graph.html)
- [Planned BankFlow Platform](graph.html)
- [Day 2 Validation](graph.html)
- [Dedicated Container Databases](graph.html)
- [Academic Prototype Correctness](graph.html)
- [Numbered Transaction Flow](graph.html)
- [ATM Sequence Interactions](graph.html)
- [Composite UML Flow](graph.html)
- [Generated Activity Flow One](graph.html)
- [Generated Activity Flow Two](graph.html)
- [Python Package Foundation](graph.html)
- [Local Database Provisioning](graph.html)
- [Detailed State Machine](graph.html)
- [State Machine Transitions](graph.html)
- [Alternate State Machine](graph.html)
- [PIN Retry Screenshot](graph.html)
- [Package Layer Docstrings](graph.html)
- [Withdrawal Success Screenshot](graph.html)
- [Zero Balance Screenshot](graph.html)
- [Environment Import Checker](graph.html)
- [Activity Diagram Swimlanes](graph.html)
- [Alternate Activity Swimlanes](graph.html)
- [SQLAlchemy URL Construction](graph.html)
- [Unconnected Session End One](graph.html)
- [Unconnected Session End Two](graph.html)

## God Nodes (most connected - your core abstractions)
1. `ATM` - 17 edges
2. `Bank System` - 15 edges
3. `Planned V1 ATM application and analytics` - 13 edges
4. `Day 1 foundation complete` - 12 edges
5. `bankflow-atm distribution / bankflow import` - 12 edges
6. `Dedicated bankflow container: running` - 12 edges
7. `Day 1 import, lint, hash and CLI checks` - 11 edges
8. `Day 2 configuration and PostgreSQL foundation complete` - 11 edges
9. `Customer` - 10 edges
10. `Direct application dependency pins` - 10 edges

## Surprising Connections (you probably didn't know these)
- `Planned validated withdrawal workflow` --semantically_similar_to--> `request_withdrawal()`  [INFERRED] [semantically similar]
  docs/PRODUCT_REQUIREMENTS.md → docs/original-college-project/atm_simulation.py
- `bankflow-atm distribution / bankflow import` --contains_placeholder--> `bankflow package placeholder`  [EXTRACTED]
  pyproject.toml → src/bankflow/__init__.py
- `bankflow-atm distribution / bankflow import` --contains_placeholder--> `bankflow/cache package placeholder`  [EXTRACTED]
  pyproject.toml → src/bankflow/cache/__init__.py
- `bankflow-atm distribution / bankflow import` --contains_placeholder--> `bankflow/config package placeholder`  [EXTRACTED]
  pyproject.toml → src/bankflow/config/__init__.py
- `bankflow-atm distribution / bankflow import` --contains_placeholder--> `bankflow/database package placeholder`  [EXTRACTED]
  pyproject.toml → src/bankflow/database/__init__.py

## Hyperedges (group relationships)
- **Academic requirements/model/code/execution traceability** — academic_trace, uml_state, uml_activity, uml_sequence, prototype, manual_scenarios [EXTRACTED 1.00]
- **Validated Day 1 Windows package environment** — package, python314, pins, lock, day1checks [EXTRACTED 1.00]
- **Planned transaction correctness contract** — txn, money, atomic, postgres [EXTRACTED 1.00]
- **Unresolved lockout lifecycle** — auth, temporary, persistent, lock_conflict [EXTRACTED 1.00]
- **Opted-in migration reversal is isolated from application data by credentials, role grants and database guards** — day2_test_database, day2_test_guard, day2_role_isolation, day2_migration_validation, day2_app_protection [EXTRACTED 1.00]
- **Schema bootstrap keeps migration bookkeeping independent while refusing destructive cascade** — migration, day2_schema, day2_public_version, day2_bootstrap_rationale, day2_no_cascade [EXTRACTED 1.00]

## Communities

### Community 0 - "Database Foundation Code"
Cohesion: 0.04
Nodes (71): downgrade(), Create the application schema; domain tables follow in Day 3.  Revision ID: 0001, upgrade(), alembic, alembic.config, alembic.util, argparse, bankflow.config.settings (+63 more)

### Community 1 - "Planned BankFlow Platform"
Cohesion: 0.07
Nodes (47): Planned account service, Planned Airflow orchestration, Planned atomic balance and transaction write, Planned three-attempt PIN lockout, Planned authentication service, BankFlow: implemented database foundation, planned ATM platform, Planned immutable Iceberg Bronze events, Planned configurable zero-balance closure (+39 more)

### Community 2 - "Day 2 Validation"
Cohesion: 0.06
Nodes (43): Day 1 import, lint, hash and CLI checks, Day 2 configuration and PostgreSQL foundation complete, Autogeneration inspects bankflow schema; future models require metadata registration, Base metadata targets bankflow with stable constraint names, Migration bookkeeping must survive application-schema bootstrap and downgrade, Bounded connection pool, timeout, pre-ping and hidden SQL parameters, Explicit engine creation/disposal and no connections during imports, Settings and health/migration errors hide credentials and raw driver details (+35 more)

### Community 3 - "Dedicated Container Databases"
Cohesion: 0.06
Nodes (41): Repository bind mount at /home/datalab/bankflow changes host files, Dedicated runtime volume datalab-runtime-bankflow at /home/datalab/runtime, Proposed /bankflow/bronze and /bankflow/silver paths not created, Five canonical documents in docs/, Container default Python 3.10.12; Windows virtual environment is not portable, Copied helper defaults /medilake/bronze and /medilake/silver, Dedicated bankflow container: running, Day 1 foundation complete (+33 more)

### Community 4 - "Academic Prototype Correctness"
Cohesion: 0.07
Nodes (39): Academic simulation is not production banking security, Numbered UML activities traced to executable output, Academic zero-balance closure behavior, 18 byte-preserved academic assets, authenticate_customer(), print_step(), ATM Simulation CSC505 - Principles of Software Engineering  This program follows, Print a numbered activity that matches the UML Activity Diagram. (+31 more)

### Community 5 - "Numbered Transaction Flow"
Cohesion: 0.07
Nodes (33): ATM System, Attempts >= 3?, Authenticate Customer: access granted, Bank / Account System, Bank checks sufficient funds, Debit Amount from Account, Check Account Balance, Close Account at zero balance (+25 more)

### Community 6 - "ATM Sequence Interactions"
Cohesion: 0.11
Nodes (31): Academic PIN check and three-failure session rejection, Account, ATM, 15 Balance, Bank System, 12 Check Balance(amount), 5 Check PIN, Customer (+23 more)

### Community 7 - "Composite UML Flow"
Cohesion: 0.09
Nodes (28): Numbered activity panel, Sequence ATM lifeline, Authenticated / show menu, Check available account balance, Sequence Bank System lifeline, Dispense Cash after debit success, Check Balance, Account Closed for zero balance (+20 more)

### Community 8 - "Generated Activity Flow One"
Cohesion: 0.09
Nodes (24): Activity arrow routing disagrees with numbered PIN and bank balance flow, Increment Failed Attempt Counter, Authenticate Customer, Bank Check Balance, Bank debit amount from account, Check Account Balance, Close Account automatically at zero balance, Display Transaction Complete / Updated Balance (+16 more)

### Community 9 - "Generated Activity Flow Two"
Cohesion: 0.09
Nodes (24): Activity arrow routing disagrees with numbered PIN and bank balance flow, Increment Failed Attempt Counter, Authenticate Customer, Bank Check Balance, Bank debit amount from account, Check Account Balance, Close Account automatically at zero balance, Display Transaction Complete / Updated Balance (+16 more)

### Community 10 - "Python Package Foundation"
Cohesion: 0.1
Nodes (21): bankflow-atm distribution / bankflow import, BankFlow application package. Domain services arrive in later milestones., bankflow package placeholder, BankFlow cache layer; implementation follows the task plan., bankflow/cache package placeholder, BankFlow config layer; implementation follows the task plan., bankflow/config package placeholder, BankFlow database layer; implementation follows the task plan. (+13 more)

### Community 11 - "Local Database Provisioning"
Cohesion: 0.14
Nodes (19): json, os, admin_sql(), main(), provision(), Provision or rotate local Day 2 database access without resetting data., Render one local environment file without exposing its password., Replace exactly one setting while preserving every other local choice. (+11 more)

### Community 12 - "Detailed State Machine"
Cohesion: 0.15
Nodes (18): Authenticated: showMenu, Check Balance: validateAmount, Account Closed: displayClosedMsg, Transaction Complete, Final State, PIN format validation, Idle: displayWelcome / clearScreen, Increment Attempts: incrementCounter (+10 more)

### Community 13 - "State Machine Transitions"
Cohesion: 0.15
Nodes (17): Account Active / transaction complete, Authenticated Customer, Check Balance, Account Closed, ATM UML State Machine Diagram, Eject Card, Final State / End of Session, Idle / waiting for card (+9 more)

### Community 14 - "Alternate State Machine"
Cohesion: 0.19
Nodes (14): Account Active: transaction complete; display new balance, Authenticated: showMenu, Check Balance after withdrawal, Account Closed: display closed message, Final State: end of session, Idle: waiting for card; display welcome, Increment Attempts: increase failed attempt counter, Initial State (+6 more)

### Community 15 - "PIN Retry Screenshot"
Cohesion: 0.18
Nodes (11): Account status ACTIVE, Authenticate Customer: access granted, Starting balance $500.00, Cash dispensed $100.00, Correct PIN 2468 on third input, End ATM Session and remove card, Incorrect PIN 1111: failed attempts 1/3, Updated balance $400.00 (+3 more)

### Community 16 - "Package Layer Docstrings"
Cohesion: 0.18
Nodes (1): BankFlow utils layer; implementation follows the task plan.

### Community 17 - "Withdrawal Success Screenshot"
Cohesion: 0.22
Nodes (9): Account status ACTIVE, Authenticate Customer: access granted, Starting balance $500.00, Cash dispensed $100.00, Correct PIN 2468 on first input, End ATM Session and remove card, Updated balance $400.00, Scenario 1: Successful withdrawal (+1 more)

### Community 18 - "Zero Balance Screenshot"
Cohesion: 0.22
Nodes (9): Authenticate Customer: access granted, Starting balance $500.00, Cash dispensed $500.00, Close Account: account status CLOSED, Correct PIN 2468, End ATM Session and remove card, Scenario 4: Zero balance and account closed, Withdrawal amount $500.00 (+1 more)

### Community 19 - "Environment Import Checker"
Cohesion: 0.29
Nodes (6): main(), Check Day 1 imports without opening network connections or loading secrets., Return nonzero if the selected interpreter or an application import fails., importlib, importlib.metadata, sys

### Community 20 - "Activity Diagram Swimlanes"
Cohesion: 0.5
Nodes (4): ATM System swimlane, Bank / Account System swimlane, Customer swimlane, Numbered ATM UML activity diagram

### Community 21 - "Alternate Activity Swimlanes"
Cohesion: 0.5
Nodes (4): ATM System swimlane, Bank / Account System swimlane, Customer swimlane, Numbered ATM UML activity diagram

### Community 22 - "SQLAlchemy URL Construction"
Cohesion: 1.0
Nodes (2): Build a URL without interpolating or manually escaping credentials., settings.settings.database.url

### Community 23 - "Unconnected Session End One"
Cohesion: 1.0
Nodes (1): End ATM Session

### Community 24 - "Unconnected Session End Two"
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
- `Temporary card lockout in UI design` → `Persistent PostgreSQL card lock in Day 5`  [AMBIGUOUS]
  docs/analysis/DOCUMENT_REVIEW.md · relation: same_lock_policy_unclear

## Knowledge Gaps
- **144 isolated node(s):** `Check Day 1 imports without opening network connections or loading secrets.`, `Return nonzero if the selected interpreter or an application import fails.`, `importlib`, `importlib_metadata`, `sys` (+139 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `SQLAlchemy URL Construction`** (2 nodes): `Build a URL without interpolating or manually escaping credentials.`, `settings.settings.database.url`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Unconnected Session End One`** (1 nodes): `End ATM Session`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Unconnected Session End Two`** (1 nodes): `End ATM Session`
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
