# BankFlow event contract — schema version 1

BankFlow publishes application facts as UTF-8 JSON after the related PostgreSQL work has committed. Day 8 defined the contract; Day 9 added acknowledged Kafka transport, delivery callbacks, and post-commit publication.

## Canonical envelope

Every message uses the same closed envelope. Unknown fields are rejected.

| Field | Type | Rule |
|---|---|---|
| `event_id` | UUIDv4 | Unique identity for deduplication; distinct from a transaction ID |
| `event_type` | string enum | Stable dotted business-event name |
| `schema_version` | integer literal | `1` for this contract |
| `occurred_at` | RFC 3339 timestamp | Timezone required; normalized to UTC |
| `source` | string literal | `bankflow.application` |
| `payload` | discriminated object | `kind` is `transaction` or `authentication` |

Example:

```json
{
  "event_id": "88888888-8888-4888-8888-888888888888",
  "event_type": "withdrawal.completed",
  "schema_version": 1,
  "occurred_at": "2026-10-05T16:00:00Z",
  "source": "bankflow.application",
  "payload": {
    "kind": "transaction",
    "transaction_id": "77777777-7777-4777-8777-777777777777",
    "customer_id": "11111111-1111-4111-8111-111111111111",
    "account_id": "22222222-2222-4222-8222-222222222222",
    "card_id": "33333333-3333-4333-8333-333333333333",
    "transaction_type": "withdrawal",
    "status": "completed",
    "amount": "25.00",
    "balance_before": "100.00",
    "balance_after": "75.00",
    "currency": "USD",
    "account_status": "active"
  }
}
```

Money uses exact decimal strings in produced JSON. Consumers must parse these fields as decimals, never binary floating-point values.

## Event types and required payload states

| Event type | Payload | Required domain state |
|---|---|---|
| `authentication.succeeded` | authentication | `authenticated`; known subject IDs |
| `authentication.failed` | authentication | `invalid_credentials` or `card_unavailable`; subject IDs may be absent for an unknown card |
| `card.locked` | authentication | `card_locked`; known subject IDs |
| `session.ended` | authentication | `session_ended`; known subject IDs |
| `balance.viewed` | transaction | balance inquiry, completed, zero amount |
| `withdrawal.requested` | transaction | withdrawal, pending, positive amount |
| `withdrawal.completed` | transaction | withdrawal, completed, positive amount |
| `withdrawal.declined` | transaction | withdrawal, declined, positive amount and decline reason |
| `deposit.completed` | transaction | deposit, completed, positive amount |
| `account.closed` | transaction | completed withdrawal with account status `closed` |

The schema rejects a payload whose transaction type, status, authentication outcome, or account status conflicts with its event type.

## Transaction payload

The transaction payload contains UUID subjects, exact financial snapshots, ISO-style currency, account status, and an optional decline reason. A decline reason is required only for a declined event. Balance inquiries require a zero amount; every balance-changing event requires a positive amount.

`transaction_id` identifies the financial operation. `event_id` identifies one emitted fact about it. A zero-balance withdrawal can therefore produce both `withdrawal.completed` and `account.closed` using the same transaction ID and different event IDs.

## Authentication payload

The authentication payload contains an outcome, optional remaining-attempt count, and either all three subject UUIDs or none. Unknown-card failures omit the identifiers so the event does not reveal whether submitted card material exists. Known-card success, lock, and session-end events require customer, account, and card UUIDs.

Authentication events never copy an `AuthenticationResult.session_token` into the payload.

## Prohibited sensitive fields

Events must never contain these fields or values:

- PIN or PIN hash
- raw fictional card token
- Redis session token
- passwords or database credentials
- Redis credentials
- connection strings containing secrets
- customer email, customer name, or other unnecessary personal data

The schemas use `extra="forbid"`, hide rejected input values in validation errors, and expose only identifiers required for operational analytics. The automated contract test recursively checks generated JSON Schema property names against the prohibited-field list.

## Versioning policy

Schema version `1` is immutable once a producer publishes it.

Compatible changes may add a new event type or an optional field with a safe default. Removing or renaming fields, changing meanings or types, tightening an already published value domain, or changing money/timestamp encoding requires a new integer schema version. Consumers must validate the full envelope and route unsupported versions to invalid-message handling rather than guessing.

Event-type behavior is part of the contract. Reusing an existing event name for a different fact is a breaking change even if the JSON shape remains valid.

## Python API

The canonical models live in `bankflow.schemas.events`. `bankflow.messaging.event_factory` maps existing service results into safe payloads and provides serialization helpers:

```python
encoded: bytes = serialize_event(event)
validated: BankFlowEvent = deserialize_event(encoded)
schema: dict = BankFlowEvent.model_json_schema()
```

Factories perform no Kafka or database I/O. The application runtime calls them only after the relevant database transaction succeeds, preserving PostgreSQL as the transactional source of truth.

## Kafka transport

All schema-version-1 facts currently use `bankflow.transaction.events`. The producer enables idempotent delivery, requires acknowledgements from all in-sync replicas, compresses payloads with gzip, and waits for a bounded delivery callback before returning.

Transaction events use `transaction_id` as their Kafka key. Authentication events use `card_id` when the card is known and `event_id` for unknown-card failures. Headers repeat only safe routing metadata: `event_type`, `schema_version`, and `source`.

Business data commits before publication begins. A broker outage is logged and does not reverse an already committed PostgreSQL operation. V1 therefore has an explicit delivery gap between the database commit and Kafka acknowledgement; an outbox is the planned reliability upgrade if recovery and replay requirements increase. See [ADR-010](../architecture/ADR-010-kafka-producer.md).
