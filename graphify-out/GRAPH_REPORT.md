# Graph Report - BankFlow  (2026-09-22)

## Dedicated container update

The user-selected `bankflow` container replaces the original shared `datalab` target. Windows endpoints are PostgreSQL 5433, Redis 6380, and Kafka 9093. PostgreSQL accepts connections and Redis requests authentication; application credentials have not been validated. Kafka metadata remained unavailable during startup checks; the cause is undiagnosed. No service configuration or data was changed by this update.

The runtime volume is `datalab-runtime-bankflow`; no other container mounted it when inspected. Container Python 3.10.12 differs from the verified Windows application Python 3.14.4. HDFS 9000 and Spark RPC 7077 are not host-published in this configuration. Copied `/medilake` paths are not adopted project storage. See [environment](../docs/ENVIRONMENT.md), [service reference](../docs/SERVICES.md), and [ADR-002](../docs/architecture/ADR-002-dedicated-container.md).

Only changed infrastructure concepts were re-extracted; unchanged academic and Day 1 evidence was reused using source hashes. The old timestamp manifest's path convention overreported changed files; it has been regenerated using Graphify's native writer. Source paths and all edge endpoints were validated. This is a knowledge map, not proof that planned services are implemented. Full directed relationships are retained in extraction.json because the simple graph collapses repeated endpoint pairs. All original archive assets remain unchanged.

## Corpus Check
- 48 files · ~31,361 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 385 nodes · 503 edges · 23 communities detected
- Extraction: 92% EXTRACTED · 6% INFERRED · 2% AMBIGUOUS · INFERRED: 30 edges (avg confidence: 0.9)
- Actual token usage and financial cost: unavailable; not zero. See cost.json.

## Community Hubs (Navigation)
- [Foundation and dedicated container](graph.html)
- [Numbered activity transaction flow](graph.html)
- [ATM sequence interactions](graph.html)
- [Academic prototype and correctness](graph.html)
- [Planned V1 application](graph.html)
- [Generated activity flow two](graph.html)
- [Generated activity flow one](graph.html)
- [Python package placeholders](graph.html)
- [Composite UML flow](graph.html)
- [Detailed state machine](graph.html)
- [State machine transitions](graph.html)
- [Academic prototype and correctness](graph.html)
- [Planned Kafka lakehouse](graph.html)
- [Alternate state machine](graph.html)
- [PIN validation across diagrams](graph.html)
- [PIN retry success screenshot](graph.html)
- [Successful withdrawal screenshot](graph.html)
- [Zero balance closure screenshot](graph.html)
- [Environment import checker](graph.html)
- [Activity diagram swimlanes](graph.html)
- [Alternate activity swimlanes](graph.html)
- [Unconnected session end one](graph.html)
- [Unconnected session end two](graph.html)

## God Nodes (most connected - your core abstractions)
1. `ATM` - 17 edges
2. `Bank System` - 15 edges
3. `Planned V1 ATM application and analytics` - 13 edges
4. `Day 1 foundation complete` - 12 edges
5. `bankflow-atm distribution / bankflow import` - 12 edges
6. `Day 1 import, lint, hash and CLI checks` - 12 edges
7. `Dedicated bankflow container: running` - 11 edges
8. `Customer` - 10 edges
9. `Direct application dependency pins` - 10 edges
10. `run_atm()` - 9 edges

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

## Communities

### Community 0 - "Foundation and dedicated container"
Cohesion: 0.07
Nodes (42): Repository bind mount at /home/datalab/bankflow changes host files, Dedicated runtime volume datalab-runtime-bankflow at /home/datalab/runtime, Proposed /bankflow/bronze and /bankflow/silver paths not created, Five canonical documents in docs/, Container default Python 3.10.12; Windows virtual environment is not portable, Copied helper defaults /medilake/bronze and /medilake/silver, Dedicated bankflow container: running, Day 1 foundation complete (+34 more)

### Community 1 - "Numbered activity transaction flow"
Cohesion: 0.08
Nodes (32): ATM System, Attempts >= 3?, Authenticate Customer: access granted, Bank / Account System, Bank checks sufficient funds, Debit Amount from Account, Check Account Balance, Close Account at zero balance (+24 more)

### Community 2 - "ATM sequence interactions"
Cohesion: 0.11
Nodes (30): Account, ATM, 15 Balance, Bank System, 12 Check Balance(amount), 5 Check PIN, Customer, 16 Debit Account(amount) (+22 more)

### Community 3 - "Academic prototype and correctness"
Cohesion: 0.09
Nodes (28): Academic zero-balance closure behavior, 18 byte-preserved academic assets, authenticate_customer(), print_step(), ATM Simulation CSC505 - Principles of Software Engineering  This program follows, Print a numbered activity that matches the UML Activity Diagram., Authenticate the customer using a PIN with a maximum of three attempts., Request and validate a withdrawal amount. (+20 more)

### Community 4 - "Planned V1 application"
Cohesion: 0.11
Nodes (27): Planned account service, Planned Airflow orchestration, Planned atomic balance and transaction write, Planned three-attempt PIN lockout, Planned authentication service, Planned configurable zero-balance closure, Planned Streamlit analytics, Planned dbt analytics marts (+19 more)

### Community 5 - "Generated activity flow two"
Cohesion: 0.09
Nodes (25): Start ATM Session, Activity arrow routing disagrees with numbered PIN and bank balance flow, Increment Failed Attempt Counter, Authenticate Customer, Bank Check Balance, Bank debit amount from account, Check Account Balance, Close Account automatically at zero balance (+17 more)

### Community 6 - "Generated activity flow one"
Cohesion: 0.1
Nodes (23): Activity arrow routing disagrees with numbered PIN and bank balance flow, Increment Failed Attempt Counter, Authenticate Customer, Bank Check Balance, Bank debit amount from account, Check Account Balance, Close Account automatically at zero balance, Display Transaction Complete / Updated Balance (+15 more)

### Community 7 - "Python package placeholders"
Cohesion: 0.1
Nodes (21): bankflow-atm distribution / bankflow import, BankFlow application package. Domain services arrive in later milestones., bankflow package placeholder, BankFlow cache layer; implementation follows the task plan., bankflow/cache package placeholder, BankFlow config layer; implementation follows the task plan., bankflow/config package placeholder, BankFlow database layer; implementation follows the task plan. (+13 more)

### Community 8 - "Composite UML flow"
Cohesion: 0.13
Nodes (19): Numbered activity panel, Sequence ATM lifeline, Check available account balance, Sequence Bank System lifeline, Dispense Cash after debit success, Sequence Customer actor, Sequence Account Database lifeline, Debit account and update database balance (+11 more)

### Community 9 - "Detailed state machine"
Cohesion: 0.15
Nodes (18): Authenticated: showMenu, Check Balance: validateAmount, Account Closed: displayClosedMsg, Transaction Complete, Final State, PIN format validation, Idle: displayWelcome / clearScreen, Increment Attempts: incrementCounter (+10 more)

### Community 10 - "State machine transitions"
Cohesion: 0.15
Nodes (17): Account Active / transaction complete, Authenticated Customer, Check Balance, Account Closed, ATM UML State Machine Diagram, Eject Card, Final State / End of Session, Idle / waiting for card (+9 more)

### Community 11 - "Academic prototype and correctness"
Cohesion: 0.15
Nodes (16): Academic simulation is not production banking security, Numbered UML activities traced to executable output, Prototypes and short cycles reduce uncertainty, Software engineering lessons from eight course modules, Four reported manual execution scenarios, NIST SP 800-63B-4 cited reference, NIST SSDF SP 800-218 cited reference, Pressman and Maxim software engineering cited reference (+8 more)

### Community 12 - "Planned Kafka lakehouse"
Cohesion: 0.24
Nodes (15): Planned immutable Iceberg Bronze events, Planned Python Kafka consumer, Events decouple transactions from analytics, Planned operational event store, Planned Gold business metrics, Planned HDFS lakehouse storage, Planned Hive Metastore catalog, Planned Kafka event streaming (+7 more)

### Community 13 - "Alternate state machine"
Cohesion: 0.19
Nodes (14): Account Active: transaction complete; display new balance, Authenticated: showMenu, Check Balance after withdrawal, Account Closed: display closed message, Final State: end of session, Idle: waiting for card; display welcome, Increment Attempts: increase failed attempt counter, Initial State (+6 more)

### Community 14 - "PIN validation across diagrams"
Cohesion: 0.2
Nodes (11): Academic PIN check and three-failure session rejection, Authenticated / show menu, Check Balance, Account Closed for zero balance, Transaction Complete for positive balance, Customer Rejected / retain card, Account Status, Update Balance by subtracting amount (+3 more)

### Community 15 - "PIN retry success screenshot"
Cohesion: 0.18
Nodes (11): Account status ACTIVE, Authenticate Customer: access granted, Starting balance $500.00, Cash dispensed $100.00, Correct PIN 2468 on third input, End ATM Session and remove card, Incorrect PIN 1111: failed attempts 1/3, Updated balance $400.00 (+3 more)

### Community 16 - "Successful withdrawal screenshot"
Cohesion: 0.22
Nodes (9): Account status ACTIVE, Authenticate Customer: access granted, Starting balance $500.00, Cash dispensed $100.00, Correct PIN 2468 on first input, End ATM Session and remove card, Updated balance $400.00, Scenario 1: Successful withdrawal (+1 more)

### Community 17 - "Zero balance closure screenshot"
Cohesion: 0.22
Nodes (9): Authenticate Customer: access granted, Starting balance $500.00, Cash dispensed $500.00, Close Account: account status CLOSED, Correct PIN 2468, End ATM Session and remove card, Scenario 4: Zero balance and account closed, Withdrawal amount $500.00 (+1 more)

### Community 18 - "Environment import checker"
Cohesion: 0.29
Nodes (6): Check Day 1 imports without opening network connections or loading secrets., Return nonzero if the selected interpreter or an application import fails., importlib, main(), importlib_metadata, sys

### Community 19 - "Activity diagram swimlanes"
Cohesion: 0.5
Nodes (4): ATM System swimlane, Bank / Account System swimlane, Customer swimlane, Numbered ATM UML activity diagram

### Community 20 - "Alternate activity swimlanes"
Cohesion: 0.5
Nodes (4): ATM System swimlane, Bank / Account System swimlane, Customer swimlane, Numbered ATM UML activity diagram

### Community 21 - "Unconnected session end one"
Cohesion: 1.0
Nodes (1): End ATM Session

### Community 22 - "Unconnected session end two"
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
- **98 isolated node(s):** `Check Day 1 imports without opening network connections or loading secrets.`, `Return nonzero if the selected interpreter or an application import fails.`, `importlib`, `importlib_metadata`, `sys` (+93 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Unconnected session end one`** (1 nodes): `End ATM Session`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Unconnected session end two`** (1 nodes): `End ATM Session`
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
HTML loads its visualization library from a CDN. Cohesion is not accuracy; retrieval ratios are text-size estimates, not measured token costs or answer-quality results.
