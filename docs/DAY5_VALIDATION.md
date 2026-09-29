# Day 5 validation — authentication and Redis

Validated on 2026-09-29 with Windows Python 3.14.4, Redis 6.0.16, PostgreSQL 14.22, redis-py 7.4.1, SQLAlchemy 2.0.54, and the dedicated `bankflow` container.

## Implemented and verified

- Added a bounded-time authenticated Redis client. The application uses Redis database 0 and integration tests use database 1 with unique key prefixes.
- Added a shared scrypt PIN utility. Hashes use a random 16-byte salt and the existing `scrypt$16384$8$1$...` storage format; verification uses constant-time digest comparison and rejects malformed hashes without exposing inputs.
- Added request/result/session schemas. PINs and returned session tokens use Pydantic `SecretStr`; validation errors hide submitted values.
- Added atomic failed-attempt increments with an expiration. A correct PIN clears the counter.
- Added 256-bit URL-safe session tokens. Redis keys contain a SHA-256 digest of each token, session payloads contain only customer/account/card UUIDs, and all sessions expire.
- Added authentication orchestration inside the caller-owned SQLAlchemy transaction. The card row is locked during evaluation so concurrent attempts serialize for one card.
- The third failed attempt persists `cards.status=locked` and `locked_at` in PostgreSQL. A later correct PIN remains denied because PostgreSQL is the permanent authority.
- Added secret-free `authentication.denied`, `authentication.card_locked`, and `authentication.succeeded` audit events.
- Refactored demo seeding to use the shared PIN hashing implementation.

## Acceptance results

| Scenario | Verified result |
|---|---|
| Correct PIN | Authenticated; expiring Redis session created |
| First wrong PIN | Denied; 2 attempts remain |
| Second wrong PIN | Denied; 1 attempt remains |
| Third wrong PIN | Denied; card permanently locked |
| Correct PIN after lock | Denied as `card_locked` |
| Success after two failures | Failed-attempt key removed |
| Session expiry | Session becomes unavailable after its Redis TTL |
| Audit secrecy | PIN, card token, and session token absent from details |

## Checks and results

```powershell
.\.venv\Scripts\python.exe -m pytest -q
# 30 passed, 14 skipped: no service opt-in

$env:BANKFLOW_RUN_DB_TESTS='1'
.\.venv\Scripts\python.exe -m pytest -q
# 44 passed
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

Live tests require `APP_ENV=test`, the dedicated `bankflow_test` PostgreSQL database, and Redis database 1. They create unique fictional database rows and Redis prefixes, then remove only those resources. They never flush a shared Redis database.

The application and test Redis passwords remain only in ignored environment files. The validation output and committed documentation do not contain them. A failed Redis operation causes authentication to fail closed with a stable error rather than bypassing counters or session state.

Day 5 does not implement account balance, withdrawal, deposit, transaction history orchestration, Streamlit, or Kafka publication. Those begin on Day 6 and later days.

Decision context: [ADR-006](architecture/ADR-006-authentication-state.md). Next: [Day 6 transaction engine](TASK.md).
