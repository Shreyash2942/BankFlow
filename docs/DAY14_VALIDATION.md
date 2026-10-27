# Day 14 Testing, CI, and V1 Release Validation

Validated on 2026-10-26 against Python 3.14.4 on Windows and the dedicated `bankflow` data-lab container.

## Release result

BankFlow's Version 1 application, event platform, operational analytics, automated checks, release documentation, and portfolio screenshots are complete. Package metadata and the Streamlit footer report `v1.0.0`.

## Automated validation

| Check | Result |
|---|---|
| Dependency consistency | `pip check`: no broken requirements |
| Environment imports | Python 3.14 check passed for package and all direct runtime dependencies |
| Ruff lint | Passed |
| Ruff format | Passed |
| Service-free pytest | 92 passed, 29 integration cases skipped by explicit opt-in |
| Full pytest | 121 passed with database and Kafka opt-ins |
| dbt | 6 models built; all 67 data tests passed; documentation generated |
| Airflow | Zero import errors; all 5 DAG tasks passed for logical date 2026-10-26 |
| Live platform snapshot | PostgreSQL, Redis, Kafka, Airflow, and dbt healthy |

Kafka tests now share a fixture that assigns unique topic, group, producer-client, and consumer-client names per test. This keeps producer and consumer integration cases isolated in local and CI runs.

## Critical-scenario evidence

| Scenario | Primary automated evidence |
|---|---|
| Successful authentication | `tests/integration/test_authentication.py` and Streamlit acceptance flow |
| Three failed PIN attempts | Authentication integration lockout sequence |
| Card lockout | Durable PostgreSQL card-state and locked-card denial assertions |
| Balance inquiry | Transaction-service and Streamlit acceptance tests |
| Successful withdrawal | Exact balance snapshots and event publication assertions |
| Insufficient funds | Declined transaction persistence with unchanged balance |
| Successful deposit | Exact-money service, repository, and UI assertions |
| Zero-balance rule | Configurable account-closure transaction test |
| Kafka publication | Acknowledged unique-topic producer round trip |
| Kafka consumption | PostgreSQL persistence, replay deduplication, and invalid-message handling |
| dbt tests | 67 live source/model/reconciliation tests |
| Airflow DAG | Service-free DAG contract test plus successful five-task live DAG run |

## GitHub Actions

`.github/workflows/quality.yml` contains three bounded jobs:

1. Python 3.14 installation, package/environment validation, Ruff, and service-free pytest.
2. Isolated PostgreSQL roles/databases plus Redis and Kafka services for all 121 application tests.
3. Python 3.11 dbt installation, a minimal event-source contract, full dbt build, tests, and documentation.

Local parsing confirmed the workflow is valid YAML, and the equivalent release commands passed locally. The first pushed workflow run remains the authoritative GitHub-hosted execution result.

## Visual evidence

The release architecture and four application screenshots are version-controlled under `docs/images/v1/` and presented in [V1_PORTFOLIO.md](V1_PORTFOLIO.md). Screens contain fictional demo data only.

## Container note

Starting the copied Kafka service regenerated its runtime properties with an internal advertised listener. Release validation restored `host.docker.internal:9093`, retained a pre-Day-14 runtime backup, restarted only Kafka, and verified broker metadata plus the live producer/consumer tests from Windows.

