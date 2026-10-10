# ADR-011: validating Kafka consumer and idempotent event store

Date: 2026-10-09. Status: accepted for local development.

BankFlow needs operational analytics events in PostgreSQL without allowing Kafka's at-least-once delivery model to create duplicate records. The existing `audit_events` table records domain-service decisions and has relationships to mutable banking entities, so it is not the correct persistence boundary for independently consumed envelopes.

## Decisions

- Consume `bankflow.transaction.events` with group `bankflow-operational-v1`, `read_committed` isolation, auto-commit disabled, and synchronous offset commits.
- Validate every value through the canonical `BankFlowEvent` schema before persistence. Unsupported versions, malformed JSON, unknown fields, and inconsistent payloads are invalid.
- Persist valid envelopes in the append-only `bankflow.consumed_events` table. Store the event ID, type, schema version, occurrence time, source, exact JSON payload, Kafka topic/partition/offset, consumer group, and consumption time.
- Use `event_id` as the primary duplicate guard and a unique topic/partition/offset constraint as a second transport-level guard. PostgreSQL `ON CONFLICT DO NOTHING` makes concurrent replay idempotent.
- Commit Kafka offsets only after PostgreSQL commits, after a duplicate is confirmed, or after an invalid message is deliberately rejected. A persistence failure leaves the offset uncommitted.
- Treat a database-commit/offset-commit failure as safe replay: the next delivery conflicts on `event_id`, is classified as a duplicate, and then commits its offset.
- Log structured identifiers and Kafka positions without logging message values. Invalid payloads are skipped and logged; Day 10 does not retain a raw poison-message body or create a dead-letter topic.
- Use a bounded poll interval plus SIGINT/SIGTERM shutdown requests. The consumer closes in a `finally` block.

## Consequences

The PostgreSQL event store provides effectively-once persistence over at-least-once Kafka delivery and gives Day 11 dbt models validated source data. It remains independent of banking-table foreign keys, so retained event history survives operational entity changes.

Invalid messages do not block a partition, and their potentially sensitive raw contents are not copied into logs or PostgreSQL. A future quarantine workflow must define sanitization and retention before storing rejected payloads. Consumer idempotence does not resolve ADR-010's producer-side database-to-Kafka crash gap.

Contract: [Event schema](../events/EVENT_SCHEMA.md). Evidence: [Day 10 validation](../DAY10_VALIDATION.md).
