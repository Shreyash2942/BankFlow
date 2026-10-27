# BankFlow V1 Portfolio

BankFlow Version 1 is a fictional ATM transaction and operational-analytics platform. It combines an exact-money Python application, durable PostgreSQL persistence, Redis-backed authentication state, versioned Kafka events, an idempotent event store, tested dbt marts, and daily Airflow orchestration.

## Architecture

![BankFlow Version 1 architecture](images/v1/bankflow-v1-architecture.png)

The editable source for this diagram is [bankflow-v1-architecture.svg](images/v1/bankflow-v1-architecture.svg).

## Demo screens

### Authentication

![BankFlow login](images/v1/bankflow-login.png)

### Account dashboard

![BankFlow account dashboard](images/v1/bankflow-dashboard.png)

### Operational analytics

![BankFlow analytics dashboard](images/v1/bankflow-analytics.png)

### Platform health

![BankFlow platform status](images/v1/bankflow-platform-status.png)

All screenshots were captured from the running Streamlit application against fictional demo data. The platform-status evidence shows healthy PostgreSQL, Redis, Kafka, Airflow, and dbt checks at release validation time.

