{{ config(alias='analytics_lakehouse_daily_transactions') }}

select
    metric_date::text || '|' || currency as lakehouse_daily_key,
    metric_date,
    currency,
    transaction_event_count,
    monetary_attempt_count,
    successful_transaction_count,
    declined_transaction_count,
    balance_inquiry_count,
    deposit_count,
    successful_withdrawal_count,
    declined_withdrawal_count,
    total_deposit_amount::numeric(38, 2) as total_deposit_amount,
    total_withdrawal_amount::numeric(38, 2) as total_withdrawal_amount,
    total_declined_amount::numeric(38, 2) as total_declined_amount,
    average_transaction_value::numeric(38, 2) as average_transaction_value,
    success_rate::numeric(9, 6) as success_rate,
    decline_rate::numeric(9, 6) as decline_rate,
    unique_account_count,
    first_event_at,
    last_event_at,
    source_gold_processed_at,
    loaded_at as serving_loaded_at
from {{ source('bankflow_serving', 'analytics_daily_transactions') }}
