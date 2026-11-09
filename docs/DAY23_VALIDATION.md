# Day 23 Validation — Data Quality Framework

Date: 2026-11-09

## Delivered

- 17 version-controlled rules across Bronze, Silver, Gold, and cross-layer reconciliation
- null, duplicate, transaction-status, amount-range, and balance-consistency checks
- Bronze-to-Silver and five Silver-to-Gold event-count reconciliations
- Alembic revision `0005` with `bankflow_quality.quality_runs` and `quality_results`
- secret-safe CLI summaries and strict/report-only exit behavior
- Streamlit latest-status, pass-count, violation-count, and freshness indicators

## Commands

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe scripts/run_data_quality.py --triggered-by day23-validation --report-only
.\.venv\Scripts\python.exe -m ruff check airflow src pages consumers scripts streaming spark tests migrations
.\.venv\Scripts\python.exe -m ruff format --check airflow src pages consumers scripts streaming spark tests migrations
.\.venv\Scripts\python.exe -m pytest -q
$env:BANKFLOW_RUN_DB_TESTS='1'
$env:BANKFLOW_RUN_KAFKA_TESTS='1'
.\.venv\Scripts\python.exe -m pytest -q
```

## Evidence

| Validation | Result |
|---|---|
| Alembic application database revision | `0005 (head)` |
| Live lakehouse rules | 17 passed, 0 failed, 0 errors, 0 violations |
| Service-free suite | 244 passed, 30 skipped |
| PostgreSQL/Redis/Kafka opt-in suite | 274 passed |

One later diagnostic run recorded a transient Trino transport error on the first Bronze rule while the remaining 16 rules passed. This is intentionally stored as `error`, not misclassified as a data violation, demonstrating fail-safe behavior. The preceding complete live run passed all 17 rules with zero violations.

## Operational contract

Run the strict command after Gold is refreshed and before serving/dbt publication. A strict run returns `1` on either data violations or unevaluated rules. Day 22 may call the same CLI with `--triggered-by airflow`; it must not use `--report-only` for its quality gate.
