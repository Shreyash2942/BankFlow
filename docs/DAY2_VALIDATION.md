# Day 2 validation — configuration and PostgreSQL

Validated on 2026-09-24 with Windows Python 3.14.4 and PostgreSQL 14.22 in the dedicated `bankflow` container.

## Implemented and verified

- Pydantic settings load from `.env`, with environment variables taking precedence. Required credentials, ports, and pool limits are validated. Secret values are excluded from displayed settings and configuration errors.
- SQLAlchemy uses the Psycopg driver, a bounded connection pool, connection timeout, pre-ping, and hidden SQL parameters. Imports do not open database connections.
- `session_scope` commits successful work, rolls back exceptions, and closes the session. Future services own this transaction boundary; repositories must not commit independently.
- A health command executes `SELECT 1`. It exits 0 for success, 1 for connection failure, and 2 for invalid configuration.
- Alembic revision `0001` creates the `bankflow` application schema. Its version table lives in `public`; future domain tables use `Base.metadata` in `bankflow`.
- Created application database/owner `bankflow` / `bankflow_user` and test database/owner `bankflow_test` / `bankflow_test_user`. Both roles lack superuser, database-creation, and role-creation privileges. PUBLIC database access is revoked on these two databases.
- Generated passwords stay in ignored `.env` and `.env.test`. The application connects through `127.0.0.1:5433`.

The first provisioning attempt used the lab's `admin` role, which cannot create roles. No roles or databases were created by that attempt; generated credentials were retained. Setup was completed through the existing `datalab` database superuser on the local socket. The provisioning script now checks that privilege before writing files. It refuses to overwrite existing credentials or resources; re-running it was verified to stop without changes.

During the final recheck, the container was running while PostgreSQL had stopped. That negative path confirmed the health command's safe message, but pytest's detailed traceback exposed a local connection argument. Both generated passwords were rotated, pytest now uses concise tracebacks, and `scripts/provision_local_database.py --rotate-passwords` provides the same guarded recovery path without resetting data.

## Checks and results

From the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
# 12 passed, 5 skipped: no database opt-in
$env:BANKFLOW_RUN_DB_TESTS='1'
.\.venv\Scripts\python.exe -m pytest -q
# 17 passed
Remove-Item Env:BANKFLOW_RUN_DB_TESTS
.\.venv\Scripts\python.exe -m bankflow.database.health
# PostgreSQL connection is healthy.
.\.venv\Scripts\alembic.exe current
# 0001 (head)
.\.venv\Scripts\alembic.exe check
# No new upgrade operations detected.
.\.venv\Scripts\alembic.exe upgrade head --sql
# Offline SQL renders the schema and revision update.
.\.venv\Scripts\python.exe -m ruff check src scripts tests migrations
.\.venv\Scripts\python.exe -m ruff format --check src scripts tests migrations
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/check_environment.py
```

The 12 unit cases cover settings precedence, absent/blank credentials, invalid ports, unknown dotenv keys, password URL handling, redacted errors, and rotation preserving unrelated local settings. The five live tests cover role privileges and health, rejected credentials, commit/rollback, upgrade/no-op/downgrade/re-upgrade, and denial of test-role access to the application database. Migration reversal runs only against the dedicated test database after checking its environment, database, and username.

The application database was upgraded to `0001`; no downgrade was run there. Both databases finish at `0001`, with no banking domain tables. Redis authentication and Kafka metadata remain separate milestone checks. The ATM services, UI, domain constraints, concurrency, and business rules are not validated by Day 2.

Next: [Day 3 core domain models](TASK.md), building on [ADR-003](architecture/ADR-003-database-foundation.md).
