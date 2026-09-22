# Graph Report - BankFlow  (2026-09-22)

## Day 1 interpretation and provenance

Day 1 foundation is implemented. The preserved academic CLI works for its original scenarios. The new database connection, authentication/transaction services, Streamlit screens, Redis/Kafka integrations, and all analytics pipelines remain planned. Installed dependencies and package placeholders are not service implementations.

The current snapshot includes the completed local Mermaid checks and `.streamlit/config.toml` theme. Docker is reachable, but the existing `datalab` container is stopped and live service authentication remains unverified. Historical analysis under `docs/analysis/` records the earlier baseline, not current implementation status.

- Detection: 46 supported files (12 code, 22 documents, 12 images); `pyproject.toml` and `.streamlit/config.toml` are additionally reviewed configuration sources.
- Raw detector count: 326,076 words, inflated by decoding raster bytes as text. Corrected readable-text count: 30,398 words, excluding raster bytes and duplicate original DOCX reports; their converted Markdown is counted.
- Academic reuse: 262 nodes / 328 relations from previously reviewed, unchanged images, academic reports and Python code. Source paths were remapped into the repository. The 18 original asset bytes match their preservation manifest. Editable VSDX files are preserved but not directly parsed; corresponding exported raster diagrams were previously reviewed.
- New semantic extraction: 88 nodes / 138 relations from current canonical documents, environment/ADR/validation notes, setup files and package dependencies. AST extraction adds 27 nodes / 16 relations from new code; 11 explicit package/check links join it to the semantic graph. Repeated `__init__.py` rationale identifiers were namespaced to avoid collisions; import targets received explicit nodes.
- All 377 node source paths and 493 extraction-edge source paths exist. Every edge has confidence and a score; EXTRACTED is 1.0. The simple undirected export has 491 edges because repeated endpoint pairs collapse; [extraction.json](extraction.json) retains all 493 relations.
- There are 5 connected components and 2 degree-zero nodes. Separate archival diagram/screenshot communities and two isolated session-end labels remain visible rather than fabricated into a single connected narrative.
- [source_snapshot.json](source_snapshot.json) records reviewed file SHA-256 hashes. New semantic nodes expose status fields; archived nodes are marked `archived_academic_evidence`. Current document extraction is intentionally bounded: repeated planning prose is summarized and dated analysis is not exhaustively duplicated.
- [manifest.json](manifest.json) supports incremental detection; [communities.json](communities.json) preserves labels, membership and raw cohesion values. Raw cohesion is not extraction accuracy or implementation quality.

## Retrieval size benchmark

Five BankFlow-specific questions were tested using Graphify's deterministic graph retrieval benchmark. It estimates 40,530 corpus tokens from 30,398 readable words versus 3,144 average retrieved graph-context tokens, a **12.9x text-size ratio**. This is not a measurement of answer accuracy, completeness, actual model usage, dollar savings, or latency. [Full benchmark](benchmark.json).

Actual extraction input/output tokens and dollar cost are unavailable, recorded as null in [cost.json](cost.json), never zero. No Obsidian vault was requested; navigation links point to [the local interactive graph](graph.html).

## Corpus Check
- 46 files · ~30,398 words
- The graph tracks source relationships across the implemented foundation, planned platform, and academic archive.

## Summary
- 377 nodes · 491 edges · 23 communities detected
- Extraction: 92% EXTRACTED · 6% INFERRED · 2% AMBIGUOUS · INFERRED: 30 edges (avg confidence: 0.9)
- Actual model token usage and financial cost: **unknown** (not exposed by this agent runtime). See [cost audit](cost.json).

## Community Hubs (Navigation)
- [Foundation and local environment](graph.html)
- [Academic prototype and correctness](graph.html)
- [Numbered activity transaction flow](graph.html)
- [ATM sequence interactions](graph.html)
- [Planned V1 application](graph.html)
- [Generated activity flow one](graph.html)
- [Generated activity flow two](graph.html)
- [Python package placeholders](graph.html)
- [Composite UML flow](graph.html)
- [Detailed state machine](graph.html)
- [State machine transitions](graph.html)
- [Planned Kafka lakehouse](graph.html)
- [Alternate state machine](graph.html)
- [PIN validation across diagrams](graph.html)
- [PIN retry success screenshot](graph.html)
- [Successful withdrawal screenshot](graph.html)
- [Zero balance closure screenshot](graph.html)
- [Environment import checker](graph.html)
- [PIN rejection screenshot](graph.html)
- [Activity diagram swimlanes](graph.html)
- [Alternate activity swimlanes](graph.html)
- [Unconnected session end one](graph.html)
- [Unconnected session end two](graph.html)

## Most connected concepts
1. `ATM` - 17 edges
2. `Bank System` - 15 edges
3. `Planned V1 ATM application and analytics` - 13 edges
4. `Day 1 foundation complete` - 12 edges
5. `bankflow-atm distribution / bankflow import` - 12 edges
6. `Day 1 import, lint, hash and CLI checks` - 12 edges
7. `Customer` - 10 edges
8. `Direct application dependency pins` - 10 edges
9. `run_atm()` - 9 edges
10. `Academic Python withdrawal prototype (documented existing)` - 9 edges

## Cross-file connections
- `Planned validated withdrawal workflow` --semantically_similar_to--> `request_withdrawal()`  [INFERRED 0.85] [semantically similar]
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

### Community 0 - "Foundation and local environment"
Cohesion: 0.07
Nodes (38): BankFlow: implemented foundation, planned platform, Five canonical documents in docs/, Existing datalab container: stopped, Day 1 foundation complete, Day 1 import, lint, hash and CLI checks, Day 2 configuration and PostgreSQL foundation, Dedicated bankflow database/user proposed, Alembic dependency installed (+30 more)

### Community 1 - "Academic prototype and correctness"
Cohesion: 0.08
Nodes (33): Academic simulation is not production banking security, Numbered UML activities traced to executable output, Academic zero-balance closure behavior, 18 byte-preserved academic assets, authenticate_customer(), print_step(), ATM Simulation CSC505 - Principles of Software Engineering  This program follows, Print a numbered activity that matches the UML Activity Diagram. (+25 more)

### Community 2 - "Numbered activity transaction flow"
Cohesion: 0.07
Nodes (33): ATM System, Attempts >= 3?, Authenticate Customer: access granted, Bank / Account System, Bank checks sufficient funds, Debit Amount from Account, Check Account Balance, Close Account at zero balance (+25 more)

### Community 3 - "ATM sequence interactions"
Cohesion: 0.12
Nodes (29): Account, ATM, 15 Balance, Bank System, 12 Check Balance(amount), 5 Check PIN, Customer, 16 Debit Account(amount) (+21 more)

### Community 4 - "Planned V1 application"
Cohesion: 0.11
Nodes (27): Planned account service, Planned Airflow orchestration, Planned atomic balance and transaction write, Planned three-attempt PIN lockout, Planned authentication service, Planned configurable zero-balance closure, Planned Streamlit analytics, Planned dbt analytics marts (+19 more)

### Community 5 - "Generated activity flow one"
Cohesion: 0.09
Nodes (25): Activity arrow routing disagrees with numbered PIN and bank balance flow, Increment Failed Attempt Counter, Authenticate Customer, Bank Check Balance, Bank debit amount from account, Check Account Balance, Close Account automatically at zero balance, Display Transaction Complete / Updated Balance (+17 more)

### Community 6 - "Generated activity flow two"
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

### Community 11 - "Planned Kafka lakehouse"
Cohesion: 0.24
Nodes (15): Planned immutable Iceberg Bronze events, Planned Python Kafka consumer, Events decouple transactions from analytics, Planned operational event store, Planned Gold business metrics, Planned HDFS lakehouse storage, Planned Hive Metastore catalog, Planned Kafka event streaming (+7 more)

### Community 12 - "Alternate state machine"
Cohesion: 0.19
Nodes (14): Account Active: transaction complete; display new balance, Authenticated: showMenu, Check Balance after withdrawal, Account Closed: display closed message, Final State: end of session, Idle: waiting for card; display welcome, Increment Attempts: increase failed attempt counter, Initial State (+6 more)

### Community 13 - "PIN validation across diagrams"
Cohesion: 0.2
Nodes (11): Academic PIN check and three-failure session rejection, Authenticated / show menu, Check Balance, Account Closed for zero balance, Transaction Complete for positive balance, Customer Rejected / retain card, Account Status, Update Balance by subtracting amount (+3 more)

### Community 14 - "PIN retry success screenshot"
Cohesion: 0.18
Nodes (11): Account status ACTIVE, Authenticate Customer: access granted, Starting balance $500.00, Cash dispensed $100.00, Correct PIN 2468 on third input, End ATM Session and remove card, Incorrect PIN 1111: failed attempts 1/3, Updated balance $400.00 (+3 more)

### Community 15 - "Successful withdrawal screenshot"
Cohesion: 0.22
Nodes (9): Account status ACTIVE, Authenticate Customer: access granted, Starting balance $500.00, Cash dispensed $100.00, Correct PIN 2468 on first input, End ATM Session and remove card, Updated balance $400.00, Scenario 1: Successful withdrawal (+1 more)

### Community 16 - "Zero balance closure screenshot"
Cohesion: 0.22
Nodes (9): Authenticate Customer: access granted, Starting balance $500.00, Cash dispensed $500.00, Close Account: account status CLOSED, Correct PIN 2468, End ATM Session and remove card, Scenario 4: Zero balance and account closed, Withdrawal amount $500.00 (+1 more)

### Community 17 - "Environment import checker"
Cohesion: 0.29
Nodes (6): Check Day 1 imports without opening network connections or loading secrets., Return nonzero if the selected interpreter or an application import fails., importlib, main(), importlib_metadata, sys

### Community 18 - "PIN rejection screenshot"
Cohesion: 0.29
Nodes (7): End ATM Session without withdrawal, Incorrect PIN 1111: failed attempts 1/3, Reject Customer: card retained and access denied, Scenario 3: Customer rejected after three incorrect PIN attempts, Incorrect PIN 2222: failed attempts 2/3, Start ATM Session and insert card, Incorrect PIN 3333: failed attempts 3/3

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
- **95 isolated node(s):** `Check Day 1 imports without opening network connections or loading secrets.`, `Return nonzero if the selected interpreter or an application import fails.`, `importlib`, `importlib_metadata`, `sys` (+90 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Unconnected session end one`** (1 nodes): `End ATM Session`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Unconnected session end two`** (1 nodes): `End ATM Session`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Which PostgreSQL preflight checks separate the completed foundation from Day 2?**
  _Connects accepted host topology, pending service authentication, configuration, and migrations._
- **Should a card lock expire automatically or require an explicit reset?**
  _Connects the design document, Day 5 persistence tasks, Redis state, and authentication service._
- **How should the new Decimal transaction core handle the archived NaN and fractional-cent failures?**
  _Connects executable academic evidence to exact money requirements and atomic writes._
- **How will committed transactions remain consistent with Kafka events and downstream lakehouse data?**
  _Connects transaction consistency risk, optional outbox mitigation, Kafka, and V2 analytics._
The HTML graph opens without a server and loads its visualization library from a CDN; internet access is required for that library. Graph retrieval sizes are estimates, not measured model costs.
