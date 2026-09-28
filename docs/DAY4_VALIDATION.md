# Day 4 validation — repository layer

Validated on 2026-09-28 with Windows Python 3.14.4, SQLAlchemy 2.0.54, Psycopg 3.3.6, and PostgreSQL 14.22 in the dedicated `bankflow` container.

## Implemented and verified

- Added session-bound repositories for customers, accounts, cards, and transactions. Repositories accept the caller's SQLAlchemy `Session` and never commit or roll back it.
- Customer lookups support UUID and unique email. Account lookups support UUID, account number, and stable account-number ordering per customer. Card lookups support UUID, fictional token, and stable per-account ordering.
- Transaction history is ordered newest first by `created_at`, with UUID as a deterministic tie-breaker. Pagination rejects limits outside 1–500 and negative offsets.
- Transaction creation accepts only `Decimal` money values, flushes the record so database failures surface inside the unit of work, and leaves the final commit to the caller.
- Balance updates accept only `Decimal`, acquire a PostgreSQL row lock, optionally check the caller's account version, flush the versioned row, and translate stale writes.
- Added stable repository exceptions for missing records, concurrent/conflicting state, invalid queries, and rejected writes. Messages contain identifiers and domain context without credentials or raw SQL.
- Repository integration coverage verifies lookups, ordering, pagination, exact money, version increments, missing records, database constraint translation, and rollback ownership.

## Checks and results

```powershell
.\.venv\Scripts\python.exe -m pytest -q
# 15 passed, 11 skipped: no database opt-in
$env:BANKFLOW_RUN_DB_TESTS='1'
.\.venv\Scripts\python.exe -m pytest -q
# 26 passed
Remove-Item Env:BANKFLOW_RUN_DB_TESTS
.\.venv\Scripts\python.exe -m ruff check src scripts tests migrations
.\.venv\Scripts\python.exe -m ruff format --check src scripts tests migrations
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m bankflow.database.health
.\.venv\Scripts\alembic.exe current
# 0002 (head)
.\.venv\Scripts\alembic.exe check
# No new upgrade operations detected.
```

The live repository tests run only against `bankflow_test`. They create unique fictional records and remove them after each case. The application database and its demo graph are not mutated by the repository tests.

Day 4 does not implement PIN verification, Redis counters/sessions, authentication lockout, banking business rules, audit orchestration, or Kafka publication. Repositories expose the persistence operations those later services need while keeping multi-record transaction ownership with the service caller.

Next: [Day 5 authentication and Redis](TASK.md), building on [ADR-005](architecture/ADR-005-repository-boundary.md).
