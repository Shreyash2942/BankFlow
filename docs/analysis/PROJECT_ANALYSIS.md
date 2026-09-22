# BankFlow: baseline analysis and implementation sequence

Analysis date: 2026-09-22. This is a review of the supplied project, not a claim that the planned platform has been implemented.

## Main finding

BankFlow has a working academic command-line prototype and a detailed specification for its next two releases. The immediate milestone is a reproducible repository and tested transaction core. PostgreSQL, Redis, Streamlit, Kafka, analytics, and the lakehouse are planned capabilities, not existing implementations.

The supplied roadmap already provides the right broad dependency order. Treat its 28 days as a planning estimate: finish and validate each milestone before proceeding, rather than treating a date or tag as evidence of completion.

## What was reviewed

- `atm_simulation.py`: the entire executable prototype.
- All five Markdown planning documents in `docs/`.
- Both Word reports, through their extracted text.
- Twelve raster images, including execution transcripts and UML drafts.
- Three editable Visio diagrams, through their page XML, labels, and connectors, alongside the raster diagrams.
- Local Git state of `BankFlow/`.
- Relevant PostgreSQL, Redis, Kafka documentation and Compose declarations in the neighboring `D:/GitHub/Data-Lab` repository. This was a targeted infrastructure check, not a full audit of that separate project.

The graph detector found 20 supported inputs: one code file, seven documents (including two converted Word reports), and twelve images. The three Visio sources were additionally reviewed. Readable code/document text contains approximately 18,307 words; the detector's original 313,985-word estimate included binary-format estimates and is not a meaningful reading-volume measure. Duplicate illustrations are retained as separate source artifacts, not independent corroboration.

Companion evidence: [document review](DOCUMENT_REVIEW.md), [diagram review](DIAGRAM_REVIEW.md), [screenshot review](SCREENSHOT_REVIEW.md), [prototype run results](PROTOTYPE_VALIDATION.json), and [interactive graph](../../graphify-out/graph.html).

## Actual starting point

| Area | Observed state | Implication |
|---|---|---|
| Repository | `BankFlow/` contains `.git` only; local `main` has no commits | Populate the existing repository; do not create another nested repository |
| Git tracking | Local status reports `origin/main [gone]` | Remote existence and remote content were not verified; do not infer that the remote repository was deleted |
| Project materials | Code, reports, diagrams, and `docs/` are outside `BankFlow/` | They are not versioned by that repository yet |
| Documentation | PRD, architecture, design, task plan, and memory exist | Use these as the baseline specification |
| Filename consistency | Architecture file is `ARCHITECTURE(1).md`, while documents reference `ARCHITECTURE.md` | Normalize the filename and links when organizing the repository |
| CLI prototype | Four functions; fixed demo PIN; $500 starting balance; one withdrawal per run | Preserve as academic provenance and a behavioral baseline |
| Planned platform | No service modules, persistence, UI, event pipeline, or CI files exist in the repository | Implement incrementally; do not describe planned features as completed |
| Runtime | Python 3.14 is the only interpreter reported by the local Python launcher | Verify the chosen dependency set in an isolated environment before selecting the project runtime |
| Docker | CLI exists; Docker Desktop Linux engine pipe was unavailable | No database, Redis, Kafka, or network connectivity was validated |

## Prototype behavior and defects

The existing code was executed without modification, using mocked console input and captured output. Five baseline scenarios behaved as expected: successful withdrawal, wrong PIN followed by a correct PIN, rejection after three failures, full-balance withdrawal and closure, and invalid input followed by a valid withdrawal.

Two additional cases reproduced defects:

| Finding | Evidence | Required behavior in the new core |
|---|---|---|
| Non-finite amount accepted | `float('nan')` passes both comparisons in `request_withdrawal`; the program reports `$nan` dispensed and a `$nan` balance | Reject non-finite amounts before comparing or updating money |
| Fractional cents accepted | A withdrawal of `0.001` succeeds but displays `$0.00`; hidden balance precision changes | Define a cent-precision policy and enforce it at input and storage boundaries |

Source: `atm_simulation.py:52-76` and [captured executions](PROTOTYPE_VALIDATION.json). These were characterization checks, not a new automated project test suite.

Other limitations are expected for the academic version: balances and failed attempts reset each process, the PIN is a constant, account closure is printed rather than persisted, and there are no deposits, history, multiple accounts, or session records. These should become explicit requirements for the replacement modules, not accidental behavior inherited from the old script.

## Preserve the intent, revise the implementation

Keep the numbered academic flow, demonstration scenarios, original reports, editable diagrams, and screenshots in an archive with clear provenance. Reuse the behavioral ideas: authenticate before accessing an account, limit failed attempts, reject invalid withdrawals, maintain a balance, and optionally close an account at zero.

The new application should separate UI, business services, repositories, and infrastructure adapters as specified in the architecture. Preserve zero-balance closure as `AUTO_CLOSE_ZERO_BALANCE`, not a universal account rule. The prototype's printed cash-dispensing action is a simulation; no hardware integration is in scope.

The existing diagrams need correction before becoming implementation references. Findings include debit-versus-dispense ordering differences, contradictory retained/ejected-card outcomes, and incorrect retry/rejection connectors. The dedicated diagram reviews distinguish those defects by source. Generated draft images and execution screenshots serve different purposes: a screenshot can illustrate an example, but cannot establish persistence, concurrency safety, or complete test coverage.

## Decisions to resolve at the relevant milestone

These are analysis recommendations, not newly approved architecture decisions.

1. **Lockout lifetime.** `TASK.md` Day 5 requires persistent PostgreSQL card lock status, while `DESIGN.md` section 13 says the lock is temporary. Define duration, reset authority, attempt-counter expiry, and behavior when Redis is unavailable. A proposed interpretation is persistent card status until explicit demo reset, with Redis providing temporary counters and session state; align the UI copy before implementation.
2. **Money contract.** The documents already require Decimal and exact SQL numerics. Also define currency, scale, bounds, non-finite rejection, and handling of more than two decimal places. Proposed initial policy: reject excess precision instead of silently rounding a submitted withdrawal.
3. **Atomicity and concurrency.** Balance update and transaction insertion must share one commit. The architecture's illustrative withdrawal sequence reads/checks the balance before beginning that transaction; implementation must protect the read/check/update operation against competing withdrawals. Require a concurrency test that prevents overspending and preserves transaction history consistency.
4. **Request idempotency.** A transaction ID identifies a transaction; by itself it does not prevent a repeated UI submission from creating another transaction. Define a request identifier and duplicate-submission outcome before completing the Streamlit transaction flow.
5. **Post-commit Kafka failure.** The memory explicitly acknowledges this gap. A committed withdrawal must not be presented as a failed withdrawal that encourages a second debit. Define publication status, retry/reconciliation behavior, and the UI result. The outbox is currently a possible future improvement, not an adopted requirement.
6. **Analytics grain.** A withdrawal can create both requested and completed events. Define metrics at transaction grain, specify successful/declined denominators, and deduplicate replayed events. Otherwise dashboards can count one withdrawal twice. The task plan already calls for consumer duplicate protection and idempotent serving loads; specify keys and acceptance tests.
7. **Sessions and closed accounts.** Define expiry enforcement, server-side authorization for every operation, treatment of deposits into closed accounts, and demo reset behavior. UI navigation alone must not authorize account access.
8. **Synthetic data isolation (V2).** Define how generated events are distinguished from application-backed transactions so reconciliation and portfolio metrics do not mix simulated balances with committed operational records.

## Infrastructure findings

The local Data-Lab README files describe PostgreSQL, Redis, and Kafka running inside a single `data-lab` container. Both inspected Compose variants declare a `data-lab` service/container and publish the usual 5432, 6379, and 9092 ports. The PostgreSQL guide also describes a standalone variant with a different mapped host port. These are configuration declarations, not proof of the active deployment.

BankFlow's example environment values (`postgres`, `redis`, and `kafka` as separate hosts) must therefore not be copied blindly. Resolve whether the application runs on Windows, inside the lab, or in its own container, then verify reachable endpoints and Kafka advertised listeners. The Redis guide also documents authenticated connections, while BankFlow's example currently omits a Redis authentication setting. Record settings names and non-secret service metadata; keep credentials out of analysis and Git.

Sources: `D:/GitHub/Data-Lab/stacks/{postgres,redis,kafka}/README.md` and `datalabcontainer/docker-compose*.yml`. Docker checks failed because the engine pipe was unavailable. No services were started, reset, or reconfigured.

## Step-by-step delivery plan

| Step | Scope | Completion evidence |
|---|---|---|
| 1 — Foundation, v0.1 | Populate `BankFlow/`; choose one canonical `docs/` location; normalize architecture filename; archive originals; add README, ignore rules, environment template, and verified Python dependency setup | Repository contains the agreed source files; prototype is runnable; environment setup is repeatable; actual infrastructure configuration is recorded or explicitly pending |
| 2 — Persistence, v0.2 | Settings, SQLAlchemy, Alembic, customer/account/card/transaction/audit models, demo seed data | Migration and seed run against the intended PostgreSQL database; exact money values survive restart |
| 3 — Authentication, v0.3 | PIN hashing, card status, Redis counters, sessions, expiry, explicit reset behavior | Correct/incorrect/locked/expired-session cases pass, including the chosen Redis-failure behavior |
| 4 — Transaction core, v0.4 | Balance inquiry, withdrawal, deposit, history, Decimal validation, atomic updates, concurrency and request deduplication | Invalid/non-finite/fractional amounts fail correctly; rollback, concurrent withdrawals, and duplicate submissions preserve balances |
| 5 — Streamlit, v0.5 | Demo entry, authentication, dashboard, withdraw/deposit/history, session end; apply the existing design tokens | Full ATM flow works across reruns; every protected operation checks session authorization; demo labeling is visible |
| 6 — Events, v0.6–v0.7 | Versioned event envelope, producer, consumer, operational event store, explicit delivery-failure behavior | Event payloads exclude secrets; duplicate delivery does not duplicate stored events; post-commit publication failures do not repeat debits |
| 7 — Analytics and V1, v0.8–v1.0 | dbt, Airflow, transaction/authentication dashboards, platform status, CI, release documentation | Metrics reconcile to source transactions; pipelines rerun safely; another developer can run the documented demo |
| 8 — V2 platform, v1.1–v2.0 | Synthetic generator, Spark, Iceberg Bronze/Silver/Gold, serving, quality checks, scale validation | Restart/replay and duplicate handling pass; metrics reconcile; performance claims include measured workload and environment |

Introduce useful unit tests with the first business logic and CI once runnable checks exist. The later testing milestone should broaden coverage, rather than postpone all automated checking until the platform is complete.

## Concrete next session

Begin Day 1 in the existing `BankFlow/` repository. Establish the canonical file layout and preserve the academic materials first. Reconcile documentation names and record the decisions needed for the first implementation slice. Validate the Python environment and inspect the live Data-Lab once its Docker engine is available. Then implement configuration and PostgreSQL persistence before moving to authentication or UI work.

This historical analysis session did not implement Day 1, alter the original prototype, correct original diagrams, publish anything, or create commits. Its deliverables are the evidence, graph, gap analysis, and an updated project handoff.


Snapshot note: this report records the pre-Day-1 review. For current implementation status, read [project memory](../MEMORY.md). Historical source paths refer to the supplied workspace; original assets now live under `docs/original-college-project/`.
