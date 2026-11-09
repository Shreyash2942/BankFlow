with source_metrics as (
    select
        count(*) as row_count,
        coalesce(sum(activity_event_count), 0) as activity_event_count,
        coalesce(sum(transaction_event_count), 0) as transaction_event_count,
        coalesce(sum(total_deposit_amount), 0)::numeric(38, 2) as total_deposit_amount,
        coalesce(sum(total_withdrawal_amount), 0)::numeric(38, 2) as total_withdrawal_amount
    from {{ source('bankflow_serving', 'analytics_account_activity') }}
),

mart_metrics as (
    select
        count(*) as row_count,
        coalesce(sum(activity_event_count), 0) as activity_event_count,
        coalesce(sum(transaction_event_count), 0) as transaction_event_count,
        coalesce(sum(total_deposit_amount), 0)::numeric(38, 2) as total_deposit_amount,
        coalesce(sum(total_withdrawal_amount), 0)::numeric(38, 2) as total_withdrawal_amount
    from {{ ref('lakehouse_account_activity') }}
)

select source_metrics.*, mart_metrics.*
from source_metrics cross join mart_metrics
where source_metrics is distinct from mart_metrics
