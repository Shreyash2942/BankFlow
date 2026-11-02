# ADR-018: Silver authentication and account events

Date: 2026-11-02. Status: accepted for the local Version 2 platform.

## Context

Day 18 intentionally excluded authentication and `account.closed` facts from `silver_transactions`. These facts need typed datasets with their own grains and rules so authentication metrics, lockout analysis, and account lifecycle reporting do not distort financial transaction counts.

## Decisions

- Build independent, rerunnable Spark jobs for `silver_authentication_events` and `silver_account_events` from immutable Iceberg Bronze.
- Normalize dotted authentication names into `authentication_success`, `authentication_failure`, `card_lockout`, and `session_end`, while preserving `source_event_type`.
- Classify each authentication fact as success, failure, lockout, or session. Set `is_lockout=true` and `lockout_classification=pin_attempt_limit` only for a valid `card.locked` event.
- Require authentication subject identifiers to be all present and valid or all absent. Success, lockout, session end, and invalid-credential failure require known subjects; unknown-card failure requires absent subjects.
- Treat `account.closed` as an account lifecycle event, not a second financial outcome. Normalize it to `account_closed` / `closure` / `zero_balance_withdrawal` and validate closed status, completed withdrawal semantics, exact decimals, zero ending balance, and balance reconciliation.
- Deduplicate both datasets by event ID, favoring the earliest valid Kafka position. Merge accepted rows by event ID and pointer-only rejects by Kafka position.
- Preserve UTC event time, schema/source, Bronze ingestion time, payload fingerprint, and Kafka coordinates. Never copy raw JSON into Silver reject tables.

## Consequences

Gold authentication and account-activity jobs can aggregate stable classifications without reinterpreting raw event names. Financial transaction marts avoid double counting `account.closed`. Authentication failures for unknown cards retain privacy because subject IDs remain absent. The current canonical sample legitimately yields an empty account table; isolated validation supplies account-closure evidence until the source generator emits that scenario.

Runbook: [`spark/silver/README.md`](../../spark/silver/README.md). Evidence: [`docs/DAY19_VALIDATION.md`](../DAY19_VALIDATION.md).

