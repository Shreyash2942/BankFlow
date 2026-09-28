# Day 3 validation — core domain models

Validated on 2026-09-27 with Windows Python 3.14.4, SQLAlchemy 2.0.54, Alembic 1.20.0, Psycopg 3.3.6, and PostgreSQL 14.22 in the dedicated `bankflow` container.

## Implemented and verified

- Added `Customer`, `Account`, `Card`, `Transaction`, and `AuditEvent` ORM models in schema `bankflow`.
- Added UUID primary keys, named foreign keys/checks, indexed lookup fields, checked string enums, and timezone-aware created/updated timestamps.
- Financial columns use `NUMERIC(18,2)` and return Python `Decimal`. Account balances and balance snapshots cannot be negative. Withdrawals and deposits must be positive; a balance inquiry may use exactly zero.
- Customer → account → card/transaction relationships load through the ORM. Financial foreign keys use restrictive deletion; audit references use `SET NULL` so the audit row survives entity removal.
- Account rows carry an ORM version counter for later lost-update protection. Day 6 still owns atomic transaction-service behavior.
- Cards contain a fictional unique token, last four digits, permanent status, and a salted one-way PIN hash. No real card number or plaintext PIN is stored.
- Alembic revision `0002` creates all five tables and their constraints/indexes. Autogeneration reports no metadata drift.
- Added an idempotent demo seed with fixed fictional identifiers, a $500.00 checking balance, and one active demo card. Partial fixed-ID state is rejected instead of silently repaired.

The seed currently creates an encoded scrypt hash so the database never receives the documented fictional PIN as plaintext. Day 5 will centralize hash creation and verification in the authentication utility while preserving compatibility with seeded records.

## Checks and results

```powershell
.\.venv\Scripts\python.exe -m pytest -q
# 15 passed, 8 skipped: no database opt-in
$env:BANKFLOW_RUN_DB_TESTS='1'
.\.venv\Scripts\python.exe -m pytest -q
# 23 passed
Remove-Item Env:BANKFLOW_RUN_DB_TESTS
.\.venv\Scripts\python.exe -m ruff check src scripts tests migrations
.\.venv\Scripts\python.exe -m ruff format --check src scripts tests migrations
.\.venv\Scripts\python.exe -m bankflow.database.health
.\.venv\Scripts\alembic.exe current
# 0002 (head)
.\.venv\Scripts\alembic.exe check
# No new upgrade operations detected.
.\.venv\Scripts\python.exe scripts/seed_database.py
# Demo data already present.
```

Live tests validate the full migration downgrade/re-upgrade chain only in `bankflow_test`, table creation, relationships, timezone-aware timestamps, exact cent round trips, database rejection of negative balances and zero withdrawals, role isolation, sessions, and seed idempotency. The application database was upgraded forward to `0002`; it was not downgraded. Running the seed twice created one customer/account/card graph and reported the second run as already present.

The Day 3 slice does not implement repositories, authentication, Redis state, withdrawals/deposits, or UI behavior. Those remain Days 4–7.

Next: [Day 4 repository layer](TASK.md), building on [ADR-004](architecture/ADR-004-core-domain-model.md).
