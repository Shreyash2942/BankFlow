# Day 1 validation

Date: 2026-09-22. Environment: Windows x64, CPython 3.14.4.

| Check | Result |
|---|---|
| Isolated `.venv` creation and dependency installation | Passed |
| Editable `bankflow-atm` package build/install | Passed |
| `python -m pip check` | Passed: no broken requirements |
| `python scripts/check_environment.py` | Passed: package and all eight direct application dependencies import |
| `python -m ruff check src scripts` | Passed |
| `python -m ruff format --check src scripts` | Passed: 11 files formatted |
| Academic asset SHA-256 verification | Passed: all 18 original files match imported bytes |
| Archived CLI smoke check | Passed: fictional PIN 2468, withdraw 100, balance 400, ACTIVE |
| Git ignore behavior | `.env`, `.env.local`, virtual environment and bytecode ignored; `.env.example` included |
| Remote read-only inspection | Origin reachable; `git ls-remote origin` returned no refs |
| Docker topology inspection | Engine reachable; existing `datalab` stopped; host mappings recorded |
| Canonical Markdown links and code fences | Passed locally; generated graph links checked after export |
| Mermaid diagrams | All four architecture diagrams rendered successfully with Mermaid CLI 11.17.0 and local Chrome |
| Pinned setup recipe | Clean-resolution dry run with `--ignore-installed`, dev requirements and Windows constraints passed |

The archived script intentionally retains the bugs documented by the baseline review. This smoke run is not a new transaction-engine test suite. No service health query, migration, Redis login, Kafka metadata call, or end-to-end web flow was run. No application release was tagged or pushed.

## Reproduce environment checks

Run from the repository root using `.venv/Scripts/python.exe` on Windows:

```text
python -m pip check
python scripts/check_environment.py
python -m ruff check src scripts
python -m ruff format --check src scripts
```

The initial installation used the direct pins; `requirements-lock-py314-windows.txt` captures the full resolved dependency set. It deliberately excludes the editable local package entry and is scoped to the validated interpreter/platform.

The Mermaid renderer and generated SVGs were kept in the system temporary directory; they are not application dependencies. GitHub-hosted rendering was not inspected, but all four Mermaid source blocks rendered locally. The Streamlit theme TOML matches the existing design palette; there is no application screen yet.

## Remaining gates

Day 2 must establish live PostgreSQL authentication and connectivity before database-dependent work can be validated. Redis and Kafka live checks belong to their respective milestones. GitHub-hosted Markdown rendering cannot be claimed from local checks alone.
