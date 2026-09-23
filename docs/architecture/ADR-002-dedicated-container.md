# ADR-002: Dedicated BankFlow lab container

Date: 2026-09-22. Status: accepted, explicitly requested by the user.

The user created a copy of Data-Lab named `bankflow`. Use it instead of the shared `datalab` target originally recorded in ADR-001.

- Image: `shreyash42/data-lab:latest`.
- Repository bind mount: `/home/datalab/bankflow`.
- Runtime volume: `datalab-runtime-bankflow`, mounted at `/home/datalab/runtime`. No other container mounted this volume during inspection; copied data is not assumed empty.
- Windows application endpoints: PostgreSQL `127.0.0.1:5433`, Redis `127.0.0.1:6380`, Kafka `127.0.0.1:9093`.
- Keep the verified Python 3.14.4 Windows environment. The container default Python is 3.10.12; do not run the Windows virtual environment inside Linux.
- Keep BankFlow storage separate from copied `/medilake` path defaults. No existing data was renamed or deleted.

This changes the deployment target, not the PRD scope. Application database provisioning and authenticated connections remain Day 2 work. See [ENVIRONMENT.md](../ENVIRONMENT.md) and [SERVICES.md](../SERVICES.md).
