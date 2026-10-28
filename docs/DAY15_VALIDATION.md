# Day 15 Validation — Synthetic Transaction Generator

**Validated:** 2026-10-27  
**Environment:** Windows Python 3.14.4 and the dedicated `bankflow` container  
**Result:** Complete

## Delivered behavior

- Creates a configurable population of unique fictional customer, account, and card UUIDs.
- Generates balance inquiries, deposits, withdrawal requests/completions/declines, authentication successes/failures, card locks, and session endings.
- Maintains exact `Decimal` balances and never emits a successful withdrawal with a negative result.
- Adds optional, validated `ATM-...` provenance to the version-1 transaction and authentication payloads.
- Reproduces identifiers, timestamps, event order, amounts, and outcomes when `--seed` is supplied.
- Streams events lazily, supports an exact `--count`, and applies a maximum `--rate` before acknowledged Kafka publication.
- Round-trips every generated message through the canonical version-1 serializer and deserializer before acceptance or publication.

## Automated checks

```powershell
.\.venv\Scripts\python.exe -m ruff check src scripts tests
.\.venv\Scripts\python.exe -m ruff format --check src scripts tests
.\.venv\Scripts\python.exe -m pytest -q
```

Result: Ruff passed, all 94 checked files were formatted, and 105 service-free tests passed with 29 opt-in integration cases skipped.

With PostgreSQL, Redis, Streamlit, and Kafka opt-ins enabled against the dedicated container:

```text
134 passed in 9.49s
```

Generator coverage verifies deterministic replay, different-seed divergence, unique synthetic identities, event-type and decline coverage, request/completion correlation, exact balance arithmetic, unknown-card privacy, rate pacing, invalid configuration, CLI dry-run isolation, schema round trips, and a 10,000-event regression stream.

## High-volume dry run

```powershell
.\.venv\Scripts\python.exe scripts\transaction_generator.py `
  --count 10000 --rate 0 --seed 15 --customers 1000 --atms 100 --dry-run
```

Result: exactly 10,000 events validated without Kafka:

| Event type | Count |
|---|---:|
| `authentication.failed` | 1,000 |
| `authentication.succeeded` | 500 |
| `balance.viewed` | 1,500 |
| `card.locked` | 500 |
| `deposit.completed` | 2,000 |
| `session.ended` | 500 |
| `withdrawal.completed` | 2,000 |
| `withdrawal.declined` | 1,000 |
| `withdrawal.requested` | 1,000 |

The initial stress attempt exposed selection of an exhausted account during a later successful withdrawal. The generator was corrected to choose only accounts that can fund at least one configured withdrawal amount, and the 10,000-event case was added permanently to the tests.

## Live Kafka proof

The dedicated broker was healthy at `localhost:9093` and advertised the host-reachable `host.docker.internal:9093` listener. The final deterministic validation stream used the isolated topic `bankflow.day15.validation.20261027.ratefinal`:

```powershell
$env:KAFKA_TRANSACTION_TOPIC='bankflow.day15.validation.20261027.ratefinal'
.\.venv\Scripts\python.exe scripts\transaction_generator.py `
  --count 40 --rate 50 --seed 15 --customers 10 --atms 4
```

Result: 40 events were acknowledged at an observed 49.73 events/second against a configured maximum of 50. An independent consumer read all 40 records from the beginning, deserialized every complete envelope, confirmed 40 unique event IDs, and confirmed an ATM ID on every payload. The produced and consumed event-type counts matched exactly.

The validation topic is intentionally separate from the operational application topic, so the test did not add synthetic facts to the Version 1 operational event store.

## Compatibility decision

`atm_id` is optional in both version-1 payload variants. This follows the published compatibility policy permitting an optional field with a safe default: all existing messages that omit the field remain valid, while Day 15 synthetic events always populate it. No schema-version increment is required.
