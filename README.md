# BankFlow

**An educational ATM transaction and analytics platform using fictional data.**

BankFlow is evolving from a command-line college assignment into a Python application and event-driven data platform. Day 1 establishes the repository, documentation, package layout, and development environment. The original CLI runs today; the new ATM services, Streamlit screens, database integration, and pipelines are still planned.

## Quick start — Windows PowerShell

Use Python 3.14 (64-bit). From this repository directory:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt -c requirements-lock-py314-windows.txt
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/check_environment.py
```

Calling the environment's Python directly avoids PowerShell activation-policy changes. Point your editor at `.venv/Scripts/python.exe`.

The lock file records the complete validated Windows/Python 3.14 dependency set. `requirements.txt` holds the direct application pins and is the package dependency source; `requirements-dev.txt` adds pytest and Ruff. Update the pins and lock together after validating a dependency change.

For another platform, create an environment with `python3.14 -m venv .venv`, use `.venv/bin/python -m pip install -r requirements-dev.txt`, then `.venv/bin/python -m pip install -e .`. That platform's dependency resolution and binary wheels must be validated separately; the Windows lock is not a cross-platform guarantee.

## Run the academic prototype

```powershell
.\.venv\Scripts\python.exe docs/original-college-project/atm_simulation.py
```

Fictional demo PIN: `2468`. Each run starts at $500. A $100 withdrawal leaves $400; three wrong PINs end the session; withdrawing $500 prints account closure. This archived script intentionally retains the original float-based validation bugs and process-local state. It is not the new transaction engine.

No Streamlit entry point exists yet; it is scheduled for Day 7. Installed dependencies and empty folders do not imply implemented features.

## Configuration and infrastructure

Copy `.env.example` to `.env` only if `.env` does not already exist, then fill it locally. The example selects a Windows-host application connecting to the existing `datalab` container's published ports. Settings loading and connections arrive on Day 2.

The lab container already exists and was stopped when inspected. BankFlow has no duplicate database, Redis, or Kafka containers. The proposed BankFlow database/user have not been created. Read the [environment guide](docs/ENVIRONMENT.md) before using the template.

## Project map

```text
BankFlow/
├── src/bankflow/             # importable package, separated by responsibility
│   ├── config/              # settings and constants (Day 2)
│   ├── models/              # persistent domain entities (Day 3)
│   ├── schemas/             # input and event contracts
│   ├── services/            # authentication, accounts, transactions
│   ├── repositories/        # database access
│   ├── database/            # engine, sessions, model base
│   ├── cache/               # Redis integration
│   ├── messaging/           # Kafka adapters
│   └── utils/
├── pages/                   # future Streamlit screens
├── consumers/               # future operational event consumer
├── migrations/              # future Alembic migrations
├── scripts/                 # local environment checks; later seed/reset tools
├── tests/                   # reserved for unit and integration tests
├── airflow/, dbt/           # future V1 analytics jobs
├── streaming/, spark/       # future V2 streaming and lakehouse jobs
├── docs/                    # canonical planning and handoff documents
│   ├── analysis/            # dated pre-implementation review
│   └── original-college-project/ # unchanged source assets and checksums
└── graphify-out/            # project graph and extraction audit
```

## Documents and milestones

- [Product requirements](docs/PRODUCT_REQUIREMENTS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Visual design](docs/DESIGN.md)
- [Day-by-day tasks](docs/TASK.md)
- [Current project memory](docs/MEMORY.md)
- [Day 1 decisions](docs/architecture/ADR-001-foundation.md)
- [Baseline analysis](docs/analysis/PROJECT_ANALYSIS.md)
- [Interactive project graph](graphify-out/graph.html) and [audit report](graphify-out/GRAPH_REPORT.md)

Delivery order: foundation → PostgreSQL persistence → authentication/Redis → transaction engine → Streamlit → Kafka → Airflow/dbt analytics → V1 acceptance → Spark/Iceberg V2.

## Development checks

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/check_environment.py
.\.venv\Scripts\python.exe -m ruff check src scripts
.\.venv\Scripts\python.exe -m ruff format --check src scripts
```

There is no automated application test suite yet. Add meaningful tests alongside the first services; `pytest` is installed for that work. See [Day 1 validation](docs/DAY1_VALIDATION.md) for the checks actually performed and their limits.
