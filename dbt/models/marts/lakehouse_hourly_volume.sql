{{ config(alias='analytics_lakehouse_hourly_volume') }}

select
    event_hour::text || '|' || currency || '|' || transaction_type || '|' || transaction_status
        as lakehouse_hourly_key,
    event_hour,
    currency,
    transaction_type,
    transaction_status,
    transaction_event_count,
    total_transaction_amount::numeric(38, 2) as total_transaction_amount,
    average_transaction_amount::numeric(38, 2) as average_transaction_amount,
    unique_account_count,
    first_event_at,
    last_event_at,
    source_gold_processed_at,
    loaded_at as serving_loaded_at
from {{ source('bankflow_serving', 'analytics_hourly_volume') }}
