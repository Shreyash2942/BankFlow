# BankFlow

**An educational ATM transaction and analytics platform using fictional data.**

BankFlow is evolving from a command-line college assignment into a Python application and event-driven data platform. Days 1–4 now provide the package foundation, PostgreSQL domain model, fictional seed data, and a tested repository boundary. The original CLI runs today; authentication, ATM services, Streamlit screens, and pipelines are still planned.

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

The Windows application connects to the dedicated `bankflow` container: PostgreSQL 5433, Redis 6380, and Kafka 9093. PostgreSQL application access is verified. Redis authentication and Kafka metadata remain future milestone checks.

On this workspace, application and test databases and ignored credentials are already provisioned. Run:

```powershell
.\.venv\Scripts\python.exe -m bankflow.database.health
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\alembic.exe current
.\.venv\Scripts\python.exe scripts/seed_database.py
```

For a fresh copy of this same lab, `scripts/provision_local_database.py` creates the two databases, restricted owner roles, and local environment files. Run it once with the dedicated container running. It deliberately refuses existing files or resources. For another PostgreSQL installation, create equivalent resources yourself, copy `.env.example` into ignored local files, and fill the connection settings. Never overwrite existing credentials to repeat setup.

Settings precedence is explicit arguments, process environment, dotenv, then defaults. Run commands from the repository root; the health command also accepts `--env-file PATH`. PostgreSQL's password is required; Redis's blank placeholder is not a verified credential. See the [environment guide](docs/ENVIRONMENT.md), [service reference](docs/SERVICES.md), and [database decision](docs/architecture/ADR-003-database-foundation.md).

## Project map

```text
BankFlow/
├── src/bankflow/             # importable package, separated by responsibility
│   ├── config/              # validated environment settings
│   ├── models/              # customer, account, card, transaction, and audit entities
│   ├── schemas/             # input and event contracts
│   ├── services/            # authentication, accounts, transactions
│   ├── repositories/        # typed lookups, balance updates, and transaction history
│   ├── database/            # engine, sessions, model base
│   ├── cache/               # Redis integration
│   ├── messaging/           # Kafka adapters
│   └── utils/
├── pages/                   # future Streamlit screens
├── consumers/               # future operational event consumer
├── migrations/              # Alembic environment and versioned schema revisions
├── scripts/                 # environment, provisioning, and idempotent demo seed tools
├── tests/                   # unit tests and opt-in PostgreSQL tests
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
- [Day 2 validation](docs/DAY2_VALIDATION.md)
- [Day 3 validation](docs/DAY3_VALIDATION.md)
- [Day 3 domain model decision](docs/architecture/ADR-004-core-domain-model.md)
- [Day 4 validation](docs/DAY4_VALIDATION.md)
- [Day 4 repository decision](docs/architecture/ADR-005-repository-boundary.md)
- [Baseline analysis](docs/analysis/PROJECT_ANALYSIS.md)
- [Interactive project graph](graphify-out/graph.html) and [audit report](graphify-out/GRAPH_REPORT.md)

Delivery order: foundation → PostgreSQL persistence → authentication/Redis → transaction engine → Streamlit → Kafka → Airflow/dbt analytics → V1 acceptance → Spark/Iceberg V2.

## Development checks

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/check_environment.py
.\.venv\Scripts\python.exe -m ruff check src scripts tests migrations
.\.venv\Scripts\python.exe -m ruff format --check src scripts tests migrations
```

Run unit tests without services, or opt into the dedicated test database:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
$env:BANKFLOW_RUN_DB_TESTS='1'
.\.venv\Scripts\python.exe -m pytest -q
Remove-Item Env:BANKFLOW_RUN_DB_TESTS
```

The live tests require `.env.test` with `APP_ENV=test`, `POSTGRES_DB=bankflow_test`, and `POSTGRES_USER=bankflow_test_user`. They exercise migration reversal and repository persistence only there. See [Day 4 validation](docs/DAY4_VALIDATION.md) for current results and limits.
