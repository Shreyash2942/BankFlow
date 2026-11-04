# BankFlow Gold analytics layer

Day 20 turns the typed Silver facts into business-ready Iceberg aggregates. Gold reads only validated Silver tables; it never reparses Bronze JSON.

## Runtime contract

| Setting | Default |
|---|---|
| Iceberg catalog | `bankflow` (`SparkCatalog`, type `hive`) |
| Hive Metastore | `thrift://localhost:9083` |
| Warehouse | `hdfs://localhost:9000/bankflow/lakehouse` |
| Gold namespace | `gold` at `hdfs://localhost:9000/bankflow/gold` |
| Transaction source | `bankflow.silver.silver_transactions` |
| Authentication source | `bankflow.silver.silver_authentication_events` |
| Account source | `bankflow.silver.silver_account_events` |

All sessions use UTC. Money is aggregated as `DECIMAL(38,2)`, balances remain `DECIMAL(18,2)`, and rates use `DECIMAL(9,6)`.

## Tables and grains

| Table | Grain | Purpose |
|---|---|---|
| `gold_daily_transaction_metrics` | date, currency | Daily attempts, outcomes, money, rates, and average successful transaction value |
| `gold_hourly_transaction_volume` | hour, currency, type, status | Operational event volume without collapsing lifecycle states |
| `gold_account_activity` | date, account, currency | Account activity, distinct transactions, money, balances, and closure state |
| `gold_authentication_metrics` | date | Authentication attempts, success/failure/lockout/session counts, and rates |
| `gold_declined_transactions` | date, currency, decline reason | Decline volume, value, average, accounts, and time range |

`withdrawal.requested` and balance inquiries remain visible in event-volume metrics but do not count as monetary attempts. A successful monetary transaction is a completed deposit or withdrawal. A decline is a terminal declined transaction. Therefore:

```text
monetary_attempt_count = successful_transaction_count + declined_transaction_count
success_rate = successful_transaction_count / monetary_attempt_count
decline_rate = declined_transaction_count / monetary_attempt_count
```

Authentication attempts include successes, ordinary failures, and card lockouts. Session-end events remain visible but are excluded from the attempt denominator. Authentication `failure_rate` includes both ordinary failures and lockouts.

## Run the jobs

Create and validate the table contracts without processing data:

```powershell
docker exec --user datalab bankflow bash -lc "cd /home/datalab/bankflow && /opt/spark/bin/spark-submit --master spark://localhost:7077 spark/gold/daily_metrics.py --create-only"
docker exec --user datalab bankflow bash -lc "cd /home/datalab/bankflow && /opt/spark/bin/spark-submit --master spark://localhost:7077 spark/gold/hourly_metrics.py --create-only"
docker exec --user datalab bankflow bash -lc "cd /home/datalab/bankflow && /opt/spark/bin/spark-submit --master spark://localhost:7077 spark/gold/account_metrics.py --create-only"
```

Build or refresh every Gold aggregate:

```powershell
docker exec --user datalab bankflow bash -lc "cd /home/datalab/bankflow && /opt/spark/bin/spark-submit --master spark://localhost:7077 spark/gold/daily_metrics.py"
docker exec --user datalab bankflow bash -lc "cd /home/datalab/bankflow && /opt/spark/bin/spark-submit --master spark://localhost:7077 spark/gold/hourly_metrics.py"
docker exec --user datalab bankflow bash -lc "cd /home/datalab/bankflow && /opt/spark/bin/spark-submit --master spark://localhost:7077 spark/gold/account_metrics.py"
```

The jobs aggregate the complete current Silver state and merge by their documented grains. Existing groups are updated and new groups are inserted, making a rerun stable while still incorporating later Silver facts.

## Quality gates

Each driver validates its output before the Iceberg merge and fails on:

- null grain fields, empty aggregate groups, negative counts, money, or balances;
- daily attempt/outcome or authentication event reconciliation errors;
- rates outside zero to one or success/failure rates that do not reconcile to one;
- account activity/closure reconciliation errors; or
- invalid first/last event ranges.

Each successful run prints one structured JSON quality record with input rows, output groups, per-rule violation counts, and final target rows.

## Query examples

```sql
SELECT metric_date, currency, monetary_attempt_count,
       successful_transaction_count, declined_transaction_count,
       total_deposit_amount, total_withdrawal_amount,
       average_transaction_value, success_rate, decline_rate
FROM hive.gold.gold_daily_transaction_metrics
ORDER BY metric_date, currency;

SELECT metric_date, authentication_attempt_count,
       successful_authentication_count, failed_authentication_count,
       card_lockout_count, success_rate, failure_rate
FROM hive.gold.gold_authentication_metrics
ORDER BY metric_date;

SELECT metric_date, account_id, transaction_event_count,
       distinct_transaction_count, opening_balance, closing_balance,
       account_closed
FROM hive.gold.gold_account_activity
ORDER BY metric_date, account_id;
```
