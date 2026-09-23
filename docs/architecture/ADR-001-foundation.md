# ADR-001: Day 1 repository and runtime foundation

Date: 2026-09-22. Status: accepted implementation choices within Day 1 scope.

The shared container target below is superseded by [ADR-002](ADR-002-dedicated-container.md). The repository and Windows Python choices remain in effect.

- Keep the existing repository name `BankFlow` and Git remote. Use `bankflow-atm` as the Python distribution name and `bankflow` as its import name.
- Store all five living project documents under `docs/`; normalize `ARCHITECTURE(1).md` to `ARCHITECTURE.md`. Original workspace copies remain untouched source snapshots; only the repository copies are maintained from now on.
- Preserve the academic source, reports, editable diagrams, and screenshots unchanged under `docs/original-college-project/`, with SHA-256 checksums. Keep dated analysis separate from current status.
- Use `src/bankflow/` as the installable package root. Planned paths such as `src/services/` become `src/bankflow/services/`; responsibilities are unchanged. Editable installation avoids relying on the working directory or manual `PYTHONPATH` changes.
- Use the existing Python 3.14 x64 interpreter in an isolated environment, after verifying dependency installation. Pin direct dependencies and record the full validated Windows environment. Other runtime/platform targets require their own validation.
- Run the application on the Windows host initially and connect to the existing `datalab` container through published ports. Do not duplicate shared infrastructure.
- Add business logic, database connections, and UI screens at their scheduled milestones. Empty directories are explicit placeholders, not implementations.

Lockout duration/reset, money precision policy, concurrent transactions, request deduplication, and Kafka recovery remain open implementation decisions described in the baseline review. This ADR does not silently settle them.
