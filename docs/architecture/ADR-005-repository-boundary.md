# ADR-005: session-bound repository boundary

Date: 2026-09-28. Status: accepted for local development.

Day 4 separates persistence mechanics from authentication and banking rules. Later services need several repository operations to participate in one atomic database transaction, so a repository cannot create or commit an independent session.

## Decisions

- Construct each repository with an existing SQLAlchemy `Session`. The service or `session_scope` caller owns commit, rollback, and close.
- Use SQLAlchemy 2.x `select()` and `Session.scalars()` for ORM reads. Do not expose SQL rows or require service code to write raw SQL.
- Return `None` from optional lookups and provide `require_by_id()` methods that raise `RepositoryNotFoundError` when absence is exceptional.
- Order account transaction history by `created_at DESC, id DESC`. The UUID tie-breaker makes pages stable when PostgreSQL transaction timestamps are equal. Limit pages to 500 records.
- Require Python `Decimal` for balance and transaction money inputs. Database `NUMERIC(18,2)` constraints remain the final persistence boundary.
- Lock an account row for a balance update and support an expected version. Flush the model so its ORM version counter advances and stale or invalid writes surface before the unit of work completes.
- Translate persistence failures into stable repository exceptions while retaining the original exception as the Python cause. Repository messages must not expose credentials or SQL parameters.
- Flush transaction creation but never commit it. Day 6 can therefore combine the account update, transaction row, and audit row in one caller-owned transaction.

## Consequences

Authentication and transaction services can operate on domain objects without duplicating persistence queries. A repository method that raises during `flush()` leaves rollback to the owning session context. The current balance-update lock and version check prepare concurrency controls; Day 6 still defines withdrawal/deposit rules and their complete atomic workflow.

References: [SQLAlchemy ORM SELECT statements](https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html), [Session API](https://docs.sqlalchemy.org/en/20/orm/session_api.html), [SELECT FOR UPDATE](https://docs.sqlalchemy.org/en/20/core/selectable.html), and [ORM exceptions](https://docs.sqlalchemy.org/en/20/orm/exceptions.html). Evidence: [Day 4 validation](../DAY4_VALIDATION.md).
