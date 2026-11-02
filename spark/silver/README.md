# BankFlow Silver transaction pipeline

Day 18 transforms immutable Bronze event values into validated, typed transaction records. It reads `bankflow.bronze.bronze_bankflow_events`, writes `bankflow.silver.silver_transactions`, and records safe rejection pointers in `bankflow.silver.silver_transaction_rejects`.

## Runtime contract

| Setting | Default |
|---|---|
| Iceberg catalog | `bankflow` (`SparkCatalog`, type `hive`) |
| Hive Metastore | `thrift://localhost:9083` |
| Warehouse | `hdfs://localhost:9000/bankflow/lakehouse` |
| Silver namespace | `silver` at `hdfs://localhost:9000/bankflow/silver` |
| Bronze source | `bankflow.bronze.bronze_bankflow_events` |
| Valid target | `bankflow.silver.silver_transactions` |
| Reject target | `bankflow.silver.silver_transaction_rejects` |

Run the driver as container user `datalab`. The container already includes the Iceberg Spark runtime, and this batch transformation does not require the Spark Kafka connector.

## Run the transformation

Create and validate the namespace/table contracts without processing data:

```powershell
docker exec --user datalab bankflow bash -lc "cd /home/datalab/bankflow && /opt/spark/bin/spark-submit --master spark://localhost:7077 spark/silver/transactions.py --create-only"
```

Transform all current Bronze transaction events:

```powershell
docker exec --user datalab bankflow bash -lc "cd /home/datalab/bankflow && /opt/spark/bin/spark-submit --master spark://localhost:7077 spark/silver/transactions.py"
```

The job is safe to rerun. It selects the earliest valid copy of each `event_id`, rejects later copies as `duplicate_event_id`, and merges accepted events by `event_id`. Rejects merge by a deterministic hash of Kafka topic, partition, and offset.

## Transformation rules

Day 18 owns these event types:

- `balance.viewed`
- `withdrawal.requested`
- `withdrawal.completed`
- `withdrawal.declined`
- `deposit.completed`

Authentication events and `account.closed` remain available in Bronze for the Day 19 authentication/account pipelines.

Silver normalizes UUIDs and controlled values, parses timestamps in a UTC Spark session, casts financial strings to `DECIMAL(18,2)`, and preserves Bronze/Kafka lineage. It validates:

- required envelope and transaction fields;
- agreement between raw JSON and Bronze metadata;
- UUID, currency, account-status, and ATM formats;
- event-type/transaction-type/status combinations;
- non-negative, cent-precision financial values; and
- balance arithmetic for inquiries, requests, completions, declines, and deposits.

Rejected records never copy `raw_payload`. The reject table stores only event identity when available, a rejection reason, Kafka coordinates, the existing payload fingerprint, and processing timestamps.

Each run prints a `bankflow_silver_transaction_quality` JSON record with source, valid, rejected, duplicate, inserted, and target counts plus rejection reasons. Persistent quality-history tables are intentionally deferred to the later observability milestone.

## Query examples

```sql
SELECT event_type, transaction_type, transaction_status, count(*)
FROM bankflow.silver.silver_transactions
GROUP BY event_type, transaction_type, transaction_status
ORDER BY event_type;

SELECT rejection_reason, count(*)
FROM bankflow.silver.silver_transaction_rejects
GROUP BY rejection_reason
ORDER BY rejection_reason;
```

