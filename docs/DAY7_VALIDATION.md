# Day 7 validation — Streamlit ATM interface

Validated on 2026-10-01 with Windows Python 3.14.4, Streamlit 1.64.0, PostgreSQL 14.22, Redis 7.4.1 client, and the dedicated `bankflow` container.

## Implemented and verified

- Added the light BankFlow theme and fixed local app port `8501`.
- Added a welcome screen with a persistent demo-mode badge, fictional-data notice, demo-card selection, masked PIN field, remaining-attempt feedback, and locked/unavailable-card states.
- Added Redis-authoritative authentication across Streamlit pages. Only the opaque session token and presentation flags enter `st.session_state`; every protected page resolves the session again.
- Added an account dashboard with an exact available balance, account/card summary, explicit balance refresh, action navigation, and recent transaction history.
- Added withdrawal and deposit pages with quick amounts, cent-formatted input, explicit `Decimal(str(value))` conversion, service-layer validation, transaction IDs, and completed/declined feedback.
- Added a bounded transaction-history table with UTC timestamps, UUIDs, types, currency amounts, and text statuses.
- Added end-session behavior that removes the Redis session and returns to sign-in.
- Added an atomic reset restricted to the fixed fictional demo graph. It restores `$500.00`, reactivates the account, unlocks the card, clears transaction history and failed attempts, appends a reset audit event, and ends the current session.
- Kept database sessions scoped to one UI action and avoided duplicate balance-inquiry writes during ordinary widget reruns.

## Acceptance results

| Scenario | Verified result |
|---|---|
| Start demo | Welcome screen loads the fixed fictional card |
| Authenticate | PIN `2468` creates a Redis-backed session and opens the dashboard |
| View balance | Dashboard records an inquiry and displays `$500.00` |
| Withdraw `$100.00` | Completed with a `$400.00` balance |
| Deposit `$25.00` | Completed with a `$425.00` balance |
| View history | Deposit and withdrawal appear newest first with UUIDs and statuses |
| Reset demo | Balance returns to `$500.00`, transactions clear, card/account reactivate |
| End session | Redis session is deleted and the welcome screen returns |
| Missing/expired session | Protected page stops and links back to sign-in |

## Checks and results

```powershell
.\.venv\Scripts\python.exe -m pytest -q
# 51 passed, 22 skipped: no service opt-in

$env:BANKFLOW_RUN_DB_TESTS='1'
.\.venv\Scripts\python.exe -m pytest -q
# 73 passed
Remove-Item Env:BANKFLOW_RUN_DB_TESTS

.\.venv\Scripts\python.exe -m ruff check app.py pages src scripts tests migrations
.\.venv\Scripts\python.exe -m ruff format --check app.py pages src scripts tests migrations
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m bankflow.database.health
.\.venv\Scripts\alembic.exe current
# 0002 (head)
.\.venv\Scripts\alembic.exe check
# No new upgrade operations detected.
```

The live Streamlit cases use only `bankflow_test` and Redis database 1. Each case recreates the fixed fictional graph, clears the default authentication prefix, and removes its database and Redis state afterward. No schema migration is required for Day 7.

Decision context: [ADR-008](architecture/ADR-008-streamlit-interface.md). Next: [Day 8 event schema](TASK.md).
