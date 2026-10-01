# Day 6 validation — transaction engine

Validated on 2026-09-30 with Windows Python 3.14.4, PostgreSQL 14.22, SQLAlchemy 2.0.54, and the dedicated `bankflow` container.

## Implemented and verified

- Added immutable request/response schemas for withdrawals, deposits, balance inquiries, and paginated transaction history.
- Transaction amounts must be Python `Decimal`, positive, finite, no more precise than cents, and within `NUMERIC(18,2)` capacity. Floats, strings, zero, negatives, NaN, infinity, fractional cents, and oversized values are rejected before persistence.
- Added authenticated account resolution. The session customer, account, and card UUIDs must describe one persisted ownership graph.
- Balance inquiry locks the account long enough to persist a consistent zero-amount inquiry transaction and `balance.viewed` audit event.
- Withdrawal locks the account row, checks funds, updates the exact balance, creates a UUID transaction with before/after snapshots, and appends audit records inside the caller-owned transaction.
- Insufficient-funds withdrawals persist a declined transaction with the unchanged balance and `insufficient_funds` reason.
- Deposits update the balance and persist the transaction and audit event atomically. Deposits that would exceed the database money range are rejected without a partial write.
- The configurable academic rule closes an account when an exact withdrawal reaches zero. Disabling the setting preserves the active account at zero. Closed accounts reject later financial operations.
- Transaction history remains readable for inactive accounts and uses the repository's stable newest-first ordering and bounded pagination.
- Injected transaction persistence failure rolls back the earlier balance change, transaction history, audit events, and version increment.

## Acceptance results

| Scenario | Verified result |
|---|---|
| Positive withdrawal | Completed; exact before/after balances persisted |
| Withdrawal above balance | Declined; balance unchanged; decline persisted |
| Negative or zero withdrawal | Schema rejects request |
| Fractional-cent or non-finite money | Schema rejects request |
| Positive deposit | Completed; exact balance increased |
| Deposit overflow | Rejected with no balance, transaction, or audit change |
| Balance inquiry | Snapshot transaction and audit event persisted |
| Zero-balance closure enabled | Account becomes `closed`; closure audit appended |
| Zero-balance closure disabled | Account remains `active` at zero |
| Persistence failure | Whole unit of work rolls back |
| Transaction history | Completed and declined records returned newest first |
| Session subject mismatch | Operation denied without writes |

## Checks and results

```powershell
.\.venv\Scripts\python.exe -m pytest -q
# 51 passed, 20 skipped: no service opt-in

$env:BANKFLOW_RUN_DB_TESTS='1'
.\.venv\Scripts\python.exe -m pytest -q
# 71 passed
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

The live cases use only `bankflow_test`, create unique fictional customer/account/card graphs, and delete their transactions and audit records afterward. No schema migration is required for Day 6.

Kafka publication remains deferred until the event schema and producer milestones. Day 6 persists the operational audit records that will support later event creation without coupling database atomicity to broker availability.

Decision context: [ADR-007](architecture/ADR-007-transaction-engine.md). Next: [Day 7 Streamlit ATM interface](TASK.md).
