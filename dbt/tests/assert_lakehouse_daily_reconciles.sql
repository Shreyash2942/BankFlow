with source_metrics as (
    select
        count(*) as row_count,
        coalesce(sum(transaction_event_count), 0) as transaction_event_count,
        coalesce(sum(monetary_attempt_count), 0) as monetary_attempt_count,
        coalesce(sum(successful_transaction_count), 0) as successful_transaction_count,
        coalesce(sum(declined_transaction_count), 0) as declined_transaction_count,
        coalesce(sum(total_deposit_amount), 0)::numeric(38, 2) as total_deposit_amount,
        coalesce(sum(total_withdrawal_amount), 0)::numeric(38, 2) as total_withdrawal_amount
    from {{ source('bankflow_serving', 'analytics_daily_transactions') }}
),

mart_metrics as (
    select
        count(*) as row_count,
        coalesce(sum(transaction_event_count), 0) as transaction_event_count,
        coalesce(sum(monetary_attempt_count), 0) as monetary_attempt_count,
        coalesce(sum(successful_transaction_count), 0) as successful_transaction_count,
        coalesce(sum(declined_transaction_count), 0) as declined_transaction_count,
        coalesce(sum(total_deposit_amount), 0)::numeric(38, 2) as total_deposit_amount,
        coalesce(sum(total_withdrawal_amount), 0)::numeric(38, 2) as total_withdrawal_amount
    from {{ ref('lakehouse_daily_transactions') }}
)

select source_metrics.*, mart_metrics.*
from source_metrics cross join mart_metrics
where source_metrics is distinct from mart_metrics
