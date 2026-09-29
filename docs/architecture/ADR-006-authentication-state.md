# ADR-006: split authentication state across PostgreSQL and Redis

Date: 2026-09-29. Status: accepted for local development.

Day 5 needs fast expiring authentication state without making Redis the durable authority for whether a card can authenticate. It also needs to preserve the original three-attempt behavior while preventing credentials from entering state keys, responses, audit details, and validation output.

## Decisions

- Store the salted scrypt PIN hash and permanent card status in PostgreSQL. Reuse the `scrypt$16384$8$1$...` format created with the Day 3 seed so all credentials use one verifier.
- Accept only four ASCII digits as the demo PIN contract. Use random salts for hashing and constant-time digest comparison for verification.
- Lock the matching PostgreSQL card row while an authentication attempt is evaluated. The caller owns commit and rollback through `session_scope`.
- Store failed-attempt counts in Redis with a sliding expiration. Clear the count after successful authentication. On the third failure, persist `locked` and `locked_at` in PostgreSQL; an expired Redis counter never unlocks the card.
- Fail authentication closed when Redis cannot maintain the counter or session.
- Generate an opaque 256-bit URL-safe session token. Hash the token before forming the Redis key, store only subject UUIDs in the value, and require a TTL.
- Use Redis database 0 for local application state and database 1 plus unique prefixes for integration tests. Cleanup deletes only the test prefix.
- Use `SecretStr` for PIN and session-token schema fields. Authentication audit details contain outcome metadata and counts only; they exclude PINs, PIN hashes, card tokens, and session tokens.
- Record denial, permanent lock, and success in `audit_events`. Kafka authentication events remain Day 8–9 work.

## Consequences

Redis loss blocks new authentication rather than weakening attempt enforcement. A successful Redis session write is compensated if the PostgreSQL audit flush fails, although Redis and PostgreSQL do not form a distributed atomic transaction. Session TTL bounds any remaining state after process failure.

Permanent lockout follows the implementation plan and product requirements. Unlocking is an administrative workflow outside the current application scope. Session authorization consumers must resolve the opaque token through `AuthenticationStateStore`; they must not trust client-supplied subject IDs.

References: [redis-py connections](https://redis.readthedocs.io/en/stable/connections.html), [Redis production usage](https://redis.io/docs/latest/develop/clients/redis-py/produsage/), [Python `hashlib.scrypt`](https://docs.python.org/3/library/hashlib.html#hashlib.scrypt), and [Python `secrets`](https://docs.python.org/3/library/secrets.html). Evidence: [Day 5 validation](../DAY5_VALIDATION.md).
