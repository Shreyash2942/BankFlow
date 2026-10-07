# ADR-010: acknowledged post-commit Kafka publication

Date: 2026-10-06. Status: accepted for local development.

BankFlow needs to publish the Day 8 event contract without allowing Kafka availability to control the outcome of PostgreSQL banking transactions. Existing domain services flush but do not commit; `BankFlowRuntime` owns the caller transaction and is therefore the first boundary that can know a commit completed.

## Decisions

- Publish from `BankFlowRuntime` only after its `session_scope` exits successfully. A failed database transaction produces no application event.
- Publish requested and terminal withdrawal facts after commit, in that order. A completed zero-balance withdrawal additionally publishes `account.closed` with the same transaction ID and a distinct event ID.
- Publish authentication success, failure, card-lock, balance-viewed, deposit-completed, and session-ended facts through the same version-1 topic.
- Use `bankflow.transaction.events` for the initial event family. Use transaction UUIDs as keys for transaction ordering, known card UUIDs for authentication ordering, and event UUIDs when an unknown card has no safe aggregate identifier.
- Configure librdkafka with idempotence, `acks=all`, gzip compression, at most five in-flight requests, and a configurable bounded delivery timeout.
- Wait for the delivery callback and return topic, partition, and offset as a receipt. Convert queue, timeout, and callback failures into stable publication errors that do not include payloads or credentials.
- Log and stop the current publication batch when Kafka is unavailable. Return the already committed banking result to the caller.
- Keep the producer injectable behind `EventPublisher` so post-commit behavior and outages can be verified without a broker.

## Consequences

Consumers receive validated, secret-free envelopes with deterministic aggregate keys and delivery acknowledgement. Tests can prove a transaction row is visible from an independent PostgreSQL session at publication time. A broker outage cannot roll back or misreport a completed withdrawal or deposit.

This is not atomic database-and-Kafka delivery. The process can stop after commit and before acknowledgement, and V1 has no durable replay queue for that gap. An outbox should replace direct post-commit publication if guaranteed recovery becomes a release requirement.

The dedicated local broker uses one partition and replication factor one, so `acks=all` confirms the single in-sync broker rather than multi-node durability.

Contract: [Event schema](../events/EVENT_SCHEMA.md). Evidence: [Day 9 validation](../DAY9_VALIDATION.md).
