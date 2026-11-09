with source_metrics as (
    select
        count(*) as row_count,
        coalesce(sum(transaction_event_count), 0) as transaction_event_count,
        coalesce(sum(total_transaction_amount), 0)::numeric(38, 2) as total_transaction_amount
    from {{ source('bankflow_serving', 'analytics_hourly_volume') }}
),

mart_metrics as (
    select
        count(*) as row_count,
        coalesce(sum(transaction_event_count), 0) as transaction_event_count,
        coalesce(sum(total_transaction_amount), 0)::numeric(38, 2) as total_transaction_amount
    from {{ ref('lakehouse_hourly_volume') }}
)

select source_metrics.*, mart_metrics.*
from source_metrics cross join mart_metrics
where source_metrics is distinct from mart_metrics
