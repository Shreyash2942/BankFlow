{{ config(alias='analytics_lakehouse_authentication_metrics') }}

select
    metric_date::text as lakehouse_authentication_key,
    metric_date,
    authentication_event_count,
    authentication_attempt_count,
    successful_authentication_count,
    failed_authentication_count,
    card_lockout_count,
    session_end_count,
    known_subject_event_count,
    unknown_subject_event_count,
    unique_account_count,
    unique_card_count,
    success_rate::numeric(9, 6) as success_rate,
    failure_rate::numeric(9, 6) as failure_rate,
    first_event_at,
    last_event_at,
    source_gold_processed_at,
    loaded_at as serving_loaded_at
from {{ source('bankflow_serving', 'analytics_authentication_metrics') }}
