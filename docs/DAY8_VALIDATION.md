# Day 8 Validation — Kafka Event Design

**Date:** 2026-10-05  
**Environment:** Windows, Python 3.14.4, Pydantic 2.13.5

## Scope completed

- Defined one immutable, closed event envelope with a UUID4 event ID, typed event name, schema version, UTC timestamp, and fixed application source.
- Added discriminated transaction and authentication payloads for all ten initial event types.
- Preserved money as finite, non-negative, two-decimal `Decimal` values and serialized it as JSON strings.
- Added event factories for transaction results, balance views, withdrawal requests, authentication results, and session termination.
- Kept PINs, PIN hashes, session tokens, card tokens, passwords, and database credentials outside event models and serialization output.
- Documented compatibility rules, event-to-payload mappings, and the Day 9 post-commit publication boundary.

## Acceptance evidence

The contract rejects unknown fields, naive timestamps, non-UUID4 event IDs, invalid money, mismatched event and payload families, incorrect transaction types or statuses, contradictory authentication results, and incomplete authentication subjects. Schema inspection also confirms that prohibited property names are absent from the generated JSON Schema.

Serialization tests verify UTF-8 JSON round trips, stable schema metadata, UTC normalization, exact decimal text, completed and declined transactions, account closure, authentication success/failure/lock outcomes, balance views, withdrawal requests, and session termination. Authentication factories consume a service result but never copy its session token into an event.

## Validation results

| Check | Result |
|---|---|
| Focused event schema/factory tests | 17 passed |
| Service-free suite | 68 passed, 22 skipped |
| Live PostgreSQL/Redis/Streamlit suite | 90 passed |
| Ruff lint | Passed |
| Ruff format check | Passed (67 files) |
| Dependency consistency (`pip check`) | No broken requirements |
| PostgreSQL health command | Passed on isolated rerun |
| Alembic current/check | `0002 (head)`; no new operations |
| Generated JSON Schema audit | 7 definitions, 21 property names, no prohibited-field overlap |

The live suite requires the dedicated `bankflow` container and `.env.test`. A concurrent Windows process-launch policy caused one transient PostgreSQL health-command failure; running that command by itself immediately passed. No application code or database state changed during the retry.

## Boundaries and next step

Day 8 defines and tests in-process contracts only. It does not open a Kafka connection, select delivery settings, or publish an event. Day 9 will configure the producer and topic, publish only after a successful database transaction, add delivery callbacks and unavailable-broker behavior, and validate the running broker.

See [the event contract](events/EVENT_SCHEMA.md) and [ADR-009](architecture/ADR-009-event-contract.md).
