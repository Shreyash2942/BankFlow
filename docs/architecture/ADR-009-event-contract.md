# ADR-009: versioned and secret-free application event contract

Date: 2026-10-05. Status: accepted for local development.

Day 8 must define a stable consumer contract before Kafka producer and consumer code exists. The contract needs exact financial values, sufficient analytics context, deterministic validation, and a hard boundary against authentication secrets.

## Decisions

- Use one closed `BankFlowEvent` envelope with a UUIDv4 `event_id`, dotted `event_type`, integer `schema_version`, timezone-aware `occurred_at`, fixed `source`, and discriminated `payload`.
- Set the initial schema version to integer `1`. Treat semantic changes as breaking even when the JSON shape remains compatible.
- Normalize timestamps to UTC and produce exact `Decimal` money as JSON strings.
- Use `kind` to discriminate transaction and authentication payloads. Reject unknown fields and reject event-type/payload combinations that do not describe the same domain fact.
- Include customer, account, card, and transaction UUIDs only where required for traceability and analytics. Do not include display names, email addresses, raw card tokens, PINs, PIN hashes, session tokens, credentials, or secret-bearing connection data.
- Allow authentication subject identifiers to be entirely absent for an unknown-card failure. Require the complete customer/account/card identifier set whenever the subject is known.
- Give each emitted fact its own `event_id`. Related lifecycle facts retain the same `transaction_id`, allowing consumers to group them while deduplicating deliveries by event ID.
- Keep event construction pure. Day 8 factories perform validation and serialization without database or broker I/O. Day 9 decides post-commit publication behavior.

## Consequences

Producers and consumers share one Pydantic-generated JSON Schema vocabulary, and invalid combinations fail before publication. Exact money survives JSON serialization without binary floating-point conversion. Analytics can correlate operational facts while authentication secrets remain outside the event boundary.

The contract does not guarantee Kafka delivery or database-and-broker atomicity. Those concerns remain Day 9 work; the existing PostgreSQL transaction stays the system of record.

Contract: [Event schema](../events/EVENT_SCHEMA.md). Evidence: [Day 8 validation](../DAY8_VALIDATION.md).
