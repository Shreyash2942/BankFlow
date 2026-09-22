# BankFlow Product Requirements Document

**Project Name:** BankFlow  
**Repository Name:** `BankFlow`  
**Document Type:** Product Requirements Document (PRD)  
**Planned Releases:** Version 1.0 and Version 2.0  
**Primary Language:** Python  

---

## 1. Product Overview

BankFlow is an event-driven ATM transaction and analytics platform designed to demonstrate how a small software-engineering prototype can evolve into a professional, portfolio-level application and data platform.

The project begins with a modern ATM simulation built with Python and Streamlit. Users interact with fictional banking data through a web interface where they can authenticate with a demo card and PIN, view an account balance, withdraw or deposit funds, review transaction history, and test common failure scenarios such as incorrect PIN attempts or insufficient funds.

Behind the user interface, BankFlow uses PostgreSQL as the primary system of record, Redis for temporary authentication and session state, and Apache Kafka for publishing transaction and authentication events.

Version 1 focuses on building a reliable transaction-processing application with event streaming and operational analytics. Version 2 expands the platform into a scalable data-engineering system using Spark Structured Streaming, Apache Iceberg, Hadoop/HDFS, Hive Metastore, Airflow, and dbt.

BankFlow is an educational and portfolio project only. It does not connect to real banks, payment networks, credit cards, or customer financial information.

---

## 2. Problem Statement

A basic ATM programming assignment can demonstrate conditional logic, loops, authentication, and balance updates, but it does not represent the architecture, persistence, testing, event processing, observability, and analytics expected in modern software and data-engineering environments.

BankFlow addresses this gap by transforming a simple ATM simulation into a multi-layer platform that demonstrates:

- professional application architecture
- persistent transactional data
- authentication and account state management
- event-driven processing
- streaming data pipelines
- analytics engineering
- automated testing
- modern data-platform design
- software and data-engineering documentation

The project should remain understandable enough to demonstrate during an interview while being technically rich enough to show progression beyond a classroom assignment.

---

## 3. Product Goals

### 3.1 Version 1 Goals

Version 1 will deliver a complete portfolio-ready ATM transaction platform.

The system should:

1. Provide a clean and modern Streamlit ATM interface.
2. Authenticate demo users through card and PIN validation.
3. Track failed PIN attempts and lock a card after the configured limit.
4. Store customers, accounts, cards, and transactions in PostgreSQL.
5. Use Redis for temporary authentication attempts, session state, and lock information.
6. Support balance inquiry, withdrawals, deposits, and transaction history.
7. Prevent invalid or insufficient-fund transactions.
8. Generate unique transaction and event identifiers.
9. Publish important application events to Apache Kafka.
10. Consume Kafka events for analytics and audit processing.
11. Use Airflow and dbt to create analytics-ready datasets.
12. Display operational and transaction analytics in Streamlit.
13. Include automated unit, integration, and event-processing tests.
14. Provide professional documentation, diagrams, and Git history.
15. Run locally through the existing Docker-based development environment.

### 3.2 Version 2 Goals

Version 2 will extend BankFlow into a data-engineering and lakehouse platform.

The system should:

1. Generate large volumes of synthetic ATM and transaction events.
2. Consume Kafka events through Spark Structured Streaming.
3. Store immutable raw events in an Apache Iceberg Bronze layer.
4. Transform and validate data into standardized Silver datasets.
5. Build Gold-level business and analytics datasets.
6. Use Hadoop/HDFS as lakehouse storage in the local data environment.
7. Use Hive Metastore for Iceberg table/catalog management.
8. Orchestrate lakehouse processing with Airflow.
9. Apply data-quality validation across Bronze, Silver, and Gold layers.
10. Load selected Gold metrics into PostgreSQL analytics-serving tables.
11. Use dbt for final analytics marts and business-facing models.
12. Present lakehouse and streaming metrics through Streamlit dashboards.

---

## 4. Product Non-Goals

The following capabilities are intentionally outside the scope of BankFlow Version 1 and Version 2:

- real banking integration
- real customer accounts
- real debit or credit card processing
- ACH, wire, or external bank transfers
- production payment processing
- storing real PINs or financial credentials
- production-grade banking compliance certification
- mobile application development
- fraud detection using machine learning
- Kubernetes deployment
- multi-region production infrastructure
- use of every technology available in the development lab

BankFlow should demonstrate deliberate architectural decisions rather than adding technologies only for portfolio keywords.

---

## 5. Target Users

### 5.1 Demo User

A portfolio reviewer, recruiter, instructor, or developer who wants to interact with the ATM application.

The demo user should be able to:

- select or insert a fictional demo card
- enter a demo PIN
- view account information
- check the available balance
- perform deposits and withdrawals
- review transaction history
- intentionally test invalid PINs and insufficient-fund scenarios
- explore transaction analytics

### 5.2 Developer

A software or data engineer reviewing the repository to understand the implementation.

The developer should be able to:

- understand the project architecture quickly
- run the application locally
- review service, repository, and data layers independently
- understand event schemas and Kafka integration
- execute automated tests
- inspect UML and architecture diagrams
- review database and lakehouse models
- understand the project evolution from Version 1 to Version 2

### 5.3 Data Engineer / Platform Reviewer

A reviewer focused on the data-engineering portion of the project.

The reviewer should be able to:

- understand the event flow from the application into Kafka
- inspect Spark streaming logic
- review Bronze, Silver, and Gold data models
- examine Airflow orchestration
- inspect dbt transformations and tests
- review Iceberg/HDFS/Hive integration
- explore analytics outputs through Streamlit

---

## 6. Core Features

### 6.1 Authentication and Session Management

BankFlow will support fictional card-based authentication.

Core capabilities:

- demo card selection or card entry
- PIN validation
- secure PIN hashing
- configurable maximum authentication attempts
- failed-attempt counting
- card lockout after repeated failures
- Redis-backed temporary session state
- session expiration
- authentication success and failure events
- no plain-text PIN logging

### 6.2 Account Management

The platform will maintain persistent account data in PostgreSQL.

Core capabilities:

- customer profile
- account profile
- account type
- available balance
- account status
- associated card information
- balance updates
- account activity timestamps

A configurable demo rule will allow the system to close an account when its balance reaches zero in order to preserve behavior from the original academic project.

### 6.3 ATM Transactions

Authenticated users will be able to perform core ATM operations.

Supported transactions:

- balance inquiry
- withdrawal
- deposit
- transaction-history lookup

Transaction processing must include:

- positive-amount validation
- sufficient-funds validation
- balance-before and balance-after values
- unique transaction ID
- transaction status
- timestamp
- atomic database update
- failure handling without partial balance updates

### 6.4 Event-Driven Processing

Important application actions will generate Kafka events.

Initial event types include:

- `authentication.succeeded`
- `authentication.failed`
- `card.locked`
- `balance.viewed`
- `withdrawal.requested`
- `withdrawal.completed`
- `withdrawal.declined`
- `deposit.completed`
- `account.closed`
- `session.ended`

Kafka events must not contain PINs, PIN hashes, database credentials, or other sensitive secrets.

### 6.5 Operational Analytics

Version 1 will provide a lightweight analytics layer built from application and event data.

Initial metrics include:

- total transactions
- successful transactions
- declined transactions
- total withdrawal amount
- total deposit amount
- average transaction amount
- authentication failures
- locked cards
- transaction volume by hour
- transaction volume by type
- transaction success rate

Airflow will orchestrate scheduled analytics workflows, while dbt will create analytics-ready models and marts.

### 6.6 Streamlit User Experience

The Streamlit application should remain simple, modern, and easy to demo.

Planned pages include:

- Welcome / Demo Card
- Authentication
- Account Dashboard
- Withdrawal
- Deposit
- Transaction History
- Transaction Analytics
- Platform Status
- About BankFlow

The application should clearly identify itself as a demo environment using fictional data.

### 6.7 Version 2 Streaming Data Platform

Version 2 will add scalable streaming and lakehouse capabilities.

Core capabilities:

- synthetic transaction generator
- high-volume Kafka event generation
- Spark Structured Streaming ingestion
- Iceberg Bronze tables for raw events
- Silver tables for validated and standardized data
- Gold tables for business metrics
- HDFS-based local lakehouse storage
- Hive Metastore catalog integration
- Airflow orchestration
- data-quality checks
- PostgreSQL analytics-serving layer
- Streamlit lakehouse analytics

---

## 7. Product Success Criteria

BankFlow Version 1 will be considered complete when:

- a user can complete the full ATM workflow through Streamlit
- authentication and three-attempt lockout behave correctly
- transactions persist correctly in PostgreSQL
- Redis manages temporary authentication/session state
- Kafka receives application events
- a consumer processes those events successfully
- Airflow and dbt generate analytics models
- automated tests cover critical business logic
- documentation allows another developer to run the project
- the repository contains professional diagrams and release documentation

BankFlow Version 2 will be considered complete when:

- synthetic events can be generated at meaningful scale
- Spark Structured Streaming consumes Kafka events
- Bronze, Silver, and Gold Iceberg layers are created successfully
- data-quality checks validate the transformed datasets
- Airflow orchestrates the end-to-end data pipeline
- selected Gold metrics are available through the serving/analytics layer
- Streamlit displays analytics generated from the Version 2 pipeline
- the repository documents the complete application-to-lakehouse data flow

---

## 8. Release Scope Summary

### Version 1.0 — BankFlow Application Platform

**Focus:** Software engineering, transactions, event streaming, and operational analytics.

Primary technologies:

`Python` · `Streamlit` · `PostgreSQL` · `SQLAlchemy` · `Redis` · `Kafka` · `Airflow` · `dbt` · `pytest` · `Docker` · `GitHub Actions`

### Version 2.0 — BankFlow Data Platform

**Focus:** Streaming data engineering and lakehouse architecture.

Additional technologies:

`Spark` · `PySpark` · `Spark Structured Streaming` · `Apache Iceberg` · `Hadoop/HDFS` · `Hive Metastore`

---

## 9. Product Vision

BankFlow should demonstrate a clear engineering evolution:

**Academic ATM Prototype → Professional Web Application → Persistent Transaction Platform → Event-Driven Architecture → Analytics Platform → Streaming Lakehouse**

The final repository should tell this story through code, architecture, documentation, testing, release history, and a working demo.

BankFlow is successful when a reviewer can understand not only what the application does, but also why each technology was selected and how the system evolved from a small software-engineering exercise into a modern application and data-engineering platform.
