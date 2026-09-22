# BankFlow document review

Reviewed 2026-09-22. This review covers the five planning Markdown files, both converted academic reports, and a source-level cross-check of `atm_simulation.py`. It distinguishes documented intentions from implemented behavior. Original documents were not changed. Model token usage was not exposed; extraction JSON uses zero as an unmeasured placeholder, not a claim of zero cost.

## What exists and what is planned

The academic CLI prototype exists and implements PIN checking, a three-attempt rejection loop, withdrawal validation, a balance update, and the assignment-specific zero-balance closure message. It has no persistent account state, card store, deposit operation, history, web UI, database, or event pipeline. Each `run_atm()` starts again with $500; rejection and closure are messages within one process. Source: [prototype](../original-college-project/atm_simulation.py), functions `authenticate_customer`, `request_withdrawal`, and `run_atm`.

The final academic report describes four successful manual execution scenarios: normal withdrawal, wrong PIN then correct PIN, three wrong PINs, and full-balance withdrawal. These are historical screenshot-backed claims, not an automated regression suite. It explicitly positions the Bank System and Account Database in the sequence diagram as design participants; those are not real integrations in the supplied Python. Source: [final report](converted/CSC505_ATM_Final_Project_Report_APA7_22b0f898.md), “Sequence Diagram,” “Python Implementation,” and “Testing and Execution Results.”

The planned BankFlow v1.0 is a much larger release than the user's existing first version. The documents describe the new platform as pre-v0.1.0 and all application infrastructure as not started. Use “academic prototype” versus “planned BankFlow v1/v2” consistently to avoid implying that the new architecture is already implemented. Source: [MEMORY §4](../MEMORY.md#4-current-project-status).

## Requirements and release boundaries

| Area | Planned v1 requirement | Planned v2 addition |
|---|---|---|
| User experience | Streamlit welcome/card selection, PIN entry, dashboard, withdrawal, deposit, transaction history, analytics, platform status, About; visible demo identity | Streaming and lakehouse metrics using the same visual language |
| Authentication | Demo card lookup; hashed PIN; default three-attempt limit; session expiry; Redis counters/sessions; card lockout; no PIN or PIN hash in logs/events | Reuse v1 authentication, plus authentication-event analytics |
| Domain and money | Customer, account, card, transaction, audit event; Decimal/NUMERIC; positive amounts; sufficient funds; unique IDs; balance-before/after; atomic balance and record changes | Reconciliation through analytical datasets |
| Account rules | Persistent account status; configurable zero-balance closure retained from the academic assignment | No separately specified new transactional rules |
| Events | `bankflow.transaction.events`; ten listed authentication, card, withdrawal, deposit, balance, account, and session events; producer and validating consumer; duplicate protection | Synthetic generator, Spark streaming, restart/checkpoint recovery |
| Analytics | PostgreSQL event store; dbt staging/intermediate/marts; Airflow freshness and quality checks; counts, success/decline rates, amounts, hourly activity | Iceberg Bronze/Silver/Gold; HDFS storage; Hive catalog; idempotent Gold-to-PostgreSQL serving; extended dbt marts |
| Quality and delivery | Unit/integration/event tests, migrations, environment configuration, existing Docker lab, CI, setup/release documentation | Cross-layer reconciliation, scale benchmarks, service recovery tests |

Sources: [PRD §§3, 6–8](../PRODUCT_REQUIREMENTS.md), [Architecture §§3–6](../ARCHITECTURE.md), [MEMORY §§9–13](../MEMORY.md), [TASK Days 5–28](../TASK.md).

The stated non-goals are clear: no real banking/payment integration, real customer credentials, banking compliance certification, mobile application, machine-learning fraud detection, Kubernetes, or multi-region production system. Hudi, Delta, MongoDB, Java, Scala, and Terraform are not part of the accepted v1/v2 design. Source: PRD §4; MEMORY §§6, 13, 20.

## Architecture assessment

The component boundaries are coherent: Streamlit handles interaction; services enforce business rules; repositories isolate persistence; PostgreSQL owns permanent state; Redis holds temporary state; Kafka decouples downstream analytics. The v2 path can run beside the v1 Python consumer, sharing an event contract. Reusing the existing Docker lab is an explicit decision, with its actual addresses, networks, and versions still unconfirmed. Sources: Architecture §§2–5, 10–12; MEMORY ISSUE-001 and ADR-MEM-006.

The design system is sufficiently specific to begin UI work: navy `#0F172A`, blue `#2563EB`, emerald `#059669`, background `#F8FAFC`, readable sans-serif type, restrained CSS around native Streamlit widgets, clear form/status states, and keyboard/readability requirements. Its visual examples are mock values, not seeded balances or measured pipeline statistics. Source: [DESIGN §§4–9, 17–18, 22–27](../DESIGN.md).

The academic reports offer a useful traceability method: link each requirement to a model, implementation location, and test. Preserve the original numbered activity trace as historical evidence, then extend that traceability to new service tests and event contracts. The lessons-learned report argues for requirements-first work, small feedback cycles, maintainability, and security throughout development; it does not establish additional BankFlow runtime features. Sources: final report “Project Requirements and Objectives”; [lessons report](converted/CSC505_Lessons_Learned_Principles_of_Software_Engineering_29d511e9.md), “Requirements Engineering and Analysis Modeling” and “Software Quality, Security Engineering, and Testing.”

## Contradictions and decisions to resolve

1. **Temporary versus permanent lockout.** TASK Day 5 requires persisting permanent locked status in PostgreSQL. DESIGN §13 tells users their card is temporarily locked. Architecture §§3.2–3.4 and MEMORY ADR-MEM-003 distinguish temporary Redis state from permanent PostgreSQL status but do not define how these interact. Specify lock duration, unlock/reset actor, attempt TTL, and restart behavior before implementing authentication. A temporary expiry and an indefinite persistent lock cannot silently represent the same condition.
2. **Documentation names and locations.** The actual architecture file is `docs/ARCHITECTURE(1).md`, while links and planned deliverables call it `ARCHITECTURE.md`. Architecture §7 places planning docs under `docs/`; TASK Day 1 and MEMORY §15 also show root copies. Pick one canonical location and repair references when establishing the repository; avoid divergent copies.
3. **Status statements need a narrower scope.** MEMORY §§17, 19, 27 say no implementation, bugs, technical debt, or runtime exists. That fits the new platform but overlooks the existing academic code. Record the prototype separately, including its limitations; do not treat those statements as proof that the source needs no review.
4. **Service-status colors conflict.** DESIGN §6 labels “unavailable” neutral gray; §16 labels unavailable red and demo/not-required gray. The latter distinction is clearer: an optional unstarted v2 service should not look like an outage, while a required failed service should.
5. **The four-week plan is a planning target, not demonstrated capacity.** Most tasks are unchecked and infrastructure versions/resources are unknown. Keep its release order and quality gates; estimate timing after the first running slice and Docker audit rather than promising both releases in 28 calendar days.

## Important specification gaps

These are recommendations from the review, not requirements silently added to the project.

| Gap | Why it matters | Concrete decision or acceptance check |
|---|---|---|
| Concurrent withdrawals | Architecture §8.2 reads and validates before its illustrated transaction boundary; atomic writes alone do not prevent two requests spending the same balance | Read/validate/update under a row lock or conditional atomic update; verify competing withdrawals cannot overdraw |
| Duplicate user submissions | MEMORY RISK-004 identifies Streamlit reruns but defines no operation deduplication | Idempotency key or equivalent request guard; replaying the same request produces one balance change and one transaction |
| Exact money policy | Decimal/NUMERIC is specified, but currency, scale, rounding, maximum amount, and nonfinite input policy are not | Reject NaN/infinity and excess precision; choose fixed currency/scale; verify stored and displayed amounts agree |
| Database/Kafka consistency | Commit then publish can leave a successful transaction absent from analytics; MEMORY RISK-003 explicitly postpones outbox consideration | Decide a documented recovery/reconciliation mechanism or transactional outbox before claiming reliable delivery; failed publishing must never rerun the financial debit |
| Event ordering and payloads | MEMORY §10 lists an envelope but not partition keys, final JSON field types, money encoding, cause/reason fields, or schema evolution rules | Freeze typed examples for every event, account ordering key, UTC timestamp representation, and event/transaction/correlation IDs |
| Metrics grain | `withdrawal.requested` and `withdrawal.completed` can describe one operation; event counts are not transaction counts | Define each metric's grain, success/decline denominator, timezone, and included statuses; reconcile totals to operational transaction records |
| Consumer recovery | Duplicate protection and invalid-message handling are requested without commit-order or quarantine policy | Persist before offset acknowledgement; unique event-ID constraint; invalid events retained with reason; retry/restart test |
| Account/card/session state machine | No definitive behavior for closed accounts, expired sessions, card locks across existing sessions, reopen/reset, or deposit into closed account | Write allowed transitions and service-side authorization checks; direct page access must not bypass authentication |
| Session failure behavior | Redis expiry is specified but duration, idle versus absolute timeout, and Redis outage behavior are not | Set explicit TTLs, invalidate sessions on logout, and define deny/recover behavior when session state is unavailable |
| Synthetic truth versus transactional truth | Generator makes synthetic IDs; application and generator share Kafka | Identify synthetic source/run IDs; decide whether synthetic accounts are seeded or isolated; do not reconcile fictional generator accounts as missing production transactions |
| Lakehouse replay semantics | Checkpoints and deduplication are planned, but watermark, lateness, dedup horizon, rerun overwrite/upsert policy, and backfill are not | Prove restart and replay preserve analytical totals; define Bronze preservation and Silver quarantine/count reconciliation |
| V1/V2 serving ownership | Both pipelines may write analytics-serving tables | Separate schemas/versions or select an explicit active source so metrics are not doubled or overwritten by competing pipelines |
| Runtime reproducibility | Existing lab details and dependency compatibility are blank | Record actual service/network/version matrix and host-versus-container endpoints; validate setup on a clean application environment |
| Measurable performance | PRD says meaningful scale; TASK Day 25 proposes 10K/100K and optional 1M | Record hardware, input count/rate, output counts, latency, errors, and recovery behavior; do not infer benchmark results from design mockups |

Source anchors: Architecture §§5.4, 8.2; MEMORY §§10, 18, 23, 26; TASK Days 8–10, 15–26; PRD §§6–7.

The current prototype's `float()` accepts `nan`, for which both `amount <= 0` and `amount > balance` are false. That can produce a NaN balance; arbitrary sub-cent amounts also pass. This source-level finding illustrates why the upgraded amount schema needs explicit finite/precision rules. It is not a claim that the new platform already contains the same bug. Source: prototype `request_withdrawal`, lines 52 onward.

## Dependency-ordered implementation roadmap

| Stage | Work | Exit evidence |
|---|---|---|
| 0. Establish the baseline | Verify actual BankFlow Git root/status; archive/reference academic assets; reconcile canonical docs/status; inspect existing Docker services without duplicating them; record lockout and money decisions | One project inventory, dependency matrix, and first-slice acceptance checklist |
| 1. Foundation | Package/configuration, reproducible dependencies, `.env.example`, migrations, narrow CI from the beginning | Clean environment imports package; configuration errors are readable; initial migration/rollback tested |
| 2. Persistent core | Customer/account/card/transaction/audit models, exact amounts, repositories, repeatable fictional seed/reset | Repeated seed safe; transaction history ordered; constraints reject invalid stored values |
| 3. Auth and transactions | Hash demo PINs; three-attempt policy; Redis sessions/expiry; service authorization; atomic and concurrent-safe deposit/withdrawal; configurable closure; operation idempotency | Positive/invalid/insufficient-funds/concurrent/repeated-request tests; lock/expiry/restart tests |
| 4. First usable web slice | Streamlit card/PIN → balance → withdrawal → history, then deposit and session ending; adopt DESIGN tokens | One end-to-end demo updates persistent data and survives reruns; protected pages reject expired sessions |
| 5. Event platform | Freeze contract; resolve commit/publish recovery; Kafka producer; idempotent validating consumer; event store/quarantine | Kafka outage does not duplicate debit; retries/restarts reconcile transaction and event records |
| 6. V1 analytics/release | Define metric grain; dbt marts/tests; Airflow freshness/retries; Streamlit analytics/status; full setup/release docs | All V1 PRD completion criteria and TASK Gate 2 pass; v1 evidence recorded before v2 work |
| 7. V2 ingestion | Version compatibility check; deterministic synthetic generator; Spark Kafka stream; Iceberg/Hive/HDFS Bronze | Known generated count arrives; raw payload preserved; restart/checkpoint evidence recorded |
| 8. V2 transformations/serving | Silver validation/dedup/quarantine; Gold metrics; idempotent serving; dbt/dashboard source switch; Airflow orchestration | Cross-layer count and amount reconciliation; rerun and late-event behavior documented |
| 9. V2 hardening/release | 10K/100K benchmark with resource limits, selected outage/recovery cases, observability, documentation/demo | TASK Gate 4 and V2 PRD success criteria pass with measured evidence |

This order preserves the accepted technology choices. CI, core logging, and critical failure tests should grow with each stage instead of first appearing at the late “testing” or “security review” day. The next implementation session should begin at Stage 0 and target the smallest complete persistent ATM flow; starting Spark before that would skip dependencies already stated in the documents.

## Extraction provenance

The companion `.graphify_chunk_01.json` encodes document concepts, relationships, and rationale with explicit source headings. All future components are labeled planned; academic behavior and report claims are separate. `EXTRACTED` means explicit in local source, `INFERRED` means an analytical connection, and `AMBIGUOUS` flags a conflict rather than asserting a settled rule. Academic references are extracted as citations only; their external contents were not fetched or independently verified.


Snapshot note: this report records the pre-Day-1 review. For current implementation status, read [project memory](../MEMORY.md). Historical source paths refer to the supplied workspace; original assets now live under `docs/original-college-project/`.
