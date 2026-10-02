# ADR-008: thin Streamlit interface and external session authority

Date: 2026-10-01. Status: accepted for local development.

Day 7 needs a complete interactive demo without moving financial rules or durable authentication state into Streamlit reruns. The interface must also remain safe to reset repeatedly for portfolio demonstrations.

## Decisions

- Keep `app.py` and `pages/` presentation-focused. A small `bankflow.ui.runtime` adapter owns shared clients and opens a fresh caller-owned database transaction for each UI action.
- Continue using the Day 5 authentication service and Redis session record as the authority. Streamlit session state stores only the opaque session token and presentation flags; every authenticated page resolves the token again before reading account data.
- Keep PIN input masked and transient. The interface never writes the PIN, raw card token, or session token to URLs, logs, tables, or audit details.
- Call the Day 6 services for balance inquiry, withdrawal, deposit, and history. Convert number-widget values explicitly through `Decimal(str(value))` before constructing strict request schemas.
- Record a balance inquiry once when a dashboard session first loads and again only after a user refresh or a completed balance-changing action. This prevents routine Streamlit widget reruns from creating duplicate inquiry transactions.
- Provide one reset operation restricted to the fixed fictional demo identifiers. It locks the demo account and card, restores the exact `$500.00` balance, reactivates and unlocks them, clears operational transaction rows, appends a `demo.reset` audit event, clears the failed-attempt counter, and ends the current session.
- Cache only infrastructure objects with `st.cache_resource`. Database sessions remain short-lived units of work and domain state remains in PostgreSQL and Redis.
- Use native labeled Streamlit controls, text-bearing status messages, and the colors and spacing from `DESIGN.md`. Status never depends on color alone.

## Consequences

Streamlit reruns cannot become an alternate source of account truth. Multiple pages share one Redis-backed authentication contract, while an expired or removed session returns the user to sign-in. The reset feature is intentionally unsuitable for arbitrary accounts and raises an error if the fixed demo graph is absent or conflicts with stored identifiers.

The live acceptance test drives the same pages and services used by the browser against `bankflow_test` and Redis database 1. Later Kafka work can attach below the service boundary without changing the UI forms.

Evidence: [Day 7 validation](../DAY7_VALIDATION.md). Design reference: [BankFlow design system](../DESIGN.md).
