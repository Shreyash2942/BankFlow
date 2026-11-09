with source_metrics as (
    select
        count(*) as row_count,
        coalesce(sum(authentication_event_count), 0) as authentication_event_count,
        coalesce(sum(authentication_attempt_count), 0) as authentication_attempt_count,
        coalesce(sum(successful_authentication_count), 0) as successful_count,
        coalesce(sum(failed_authentication_count), 0) as failed_count,
        coalesce(sum(card_lockout_count), 0) as lockout_count
    from {{ source('bankflow_serving', 'analytics_authentication_metrics') }}
),

mart_metrics as (
    select
        count(*) as row_count,
        coalesce(sum(authentication_event_count), 0) as authentication_event_count,
        coalesce(sum(authentication_attempt_count), 0) as authentication_attempt_count,
        coalesce(sum(successful_authentication_count), 0) as successful_count,
        coalesce(sum(failed_authentication_count), 0) as failed_count,
        coalesce(sum(card_lockout_count), 0) as lockout_count
    from {{ ref('lakehouse_authentication_metrics') }}
)

select source_metrics.*, mart_metrics.*
from source_metrics cross join mart_metrics
where source_metrics is distinct from mart_metrics
