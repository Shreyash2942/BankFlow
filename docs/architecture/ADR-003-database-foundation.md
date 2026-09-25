# ADR-003: configuration and isolated PostgreSQL foundation

Date: 2026-09-24. Status: accepted for local development.

Day 2 needs persistent connectivity and migrations before Day 3 introduces banking entities. Use the dedicated container selected in ADR-002 through Windows port 5433.

## Decisions

- Provision separate `bankflow` and `bankflow_test` databases with separate non-superuser owner roles. Revoke PUBLIC database access on each. Local migrations and application code currently share their database's owner role; a separate deployment migration role is a future hardening decision.
- Keep generated credentials in ignored local environment files. The one-time script uses the container's existing `datalab` superuser through its local Unix socket. Application requests never use that role. Setup refuses existing files/resources and does not reset databases.
- Load validated settings explicitly at startup. Explicit arguments override process environment, which overrides dotenv, which overrides defaults. Build database URLs with SQLAlchemy's URL object so special characters in passwords remain valid.
- Create engines explicitly and dispose them at the owning process boundary. Services will wrap a unit of work in `session_scope`; repositories use the supplied session without committing.
- Place domain metadata in schema `bankflow`, with stable constraint names. Revision `0001` creates that schema. Keep Alembic's bookkeeping table in `public` so bootstrap and downgrade do not require the application schema to exist.
- Restrict autogeneration inspection to `bankflow`. Future model modules must be imported into Alembic's metadata registration when Day 3 adds them.
- Drop the schema without CASCADE on downgrade. Unexpected remaining objects must cause an error rather than be silently removed.
- Require explicit opt-in and dedicated test credentials before live migration tests. Never exercise downgrade against the application database.

## Consequences

Domain tables are still Day 3 work. SQLAlchemy exceptions are reduced to safe messages at health-check and migration command boundaries; secrets and raw driver details must not be logged. The owner roles are appropriate for this isolated development setup, not a production runtime privilege model.

References: [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/), [SQLAlchemy session transactions](https://docs.sqlalchemy.org/en/20/orm/session_basics.html), [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html). Evidence: [Day 2 validation](../DAY2_VALIDATION.md).
