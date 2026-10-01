# ADR-007: exact and atomic transaction service boundary

Date: 2026-09-30. Status: accepted for local development.

Day 6 must correct the academic prototype's float, non-finite, and fractional-cent defects while keeping the caller-owned transaction boundary established on Day 4. Financial results must remain auditable even when a request is declined, and a persistence error must never leave a partially updated balance.

## Decisions

- Accept financial amounts only as Python `Decimal` with at most two decimal places. Reject floats and strings at the service schema boundary so callers must make conversion policy explicit.
- Require positive withdrawal and deposit amounts. Reject NaN, infinity, fractional cents, values beyond `NUMERIC(18,2)`, and deposits whose resulting balance exceeds that range.
- Derive the account, customer, and card from the Redis authentication-session subjects. Confirm that those UUIDs form one persisted ownership graph before every operation.
- Acquire a PostgreSQL row lock for balance inquiry, withdrawal, and deposit. Combine the account update, transaction record, account version increment, and audit rows in one caller-owned SQLAlchemy transaction.
- Generate a UUID for every balance inquiry, withdrawal, deposit, and declined insufficient-funds request.
- Persist insufficient-funds attempts as `declined` transactions with identical before/after balances and a stable `insufficient_funds` reason.
- Persist balance inquiries as completed zero-amount transactions so operational history and later analytics see the action.
- Retain the legacy zero-balance account closure only when `AUTO_CLOSE_ZERO_BALANCE` is enabled. This is a configurable demonstration rule rather than a general banking claim.
- Allow transaction history for inactive accounts while rejecting new balance-changing operations on non-active accounts.
- Append operational audit events in the same database transaction. Kafka publication begins after the Day 8 event contract and Day 9 producer integration.

## Consequences

The service returns completed or declined results with exact balance snapshots and stable identifiers. Repository or audit failures roll back every mutation through `session_scope`; services never call `commit()` or `rollback()` themselves.

Strict `Decimal` request schemas require Day 7 UI code to convert display inputs deliberately, such as `Decimal(str(value))`, before calling the services. This prevents binary floating-point values from entering financial rules implicitly.

References: [SQLAlchemy session transactions](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html), [SQLAlchemy `with_for_update`](https://docs.sqlalchemy.org/en/20/core/selectable.html), and [Python `Decimal`](https://docs.python.org/3/library/decimal.html). Evidence: [Day 6 validation](../DAY6_VALIDATION.md).
