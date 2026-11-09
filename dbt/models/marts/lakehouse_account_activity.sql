{{ config(alias='analytics_lakehouse_account_activity') }}

select
    metric_date::text || '|' || account_id::text || '|' || currency
        as lakehouse_account_activity_key,
    metric_date,
    account_id,
    currency,
    activity_event_count,
    transaction_event_count,
    distinct_transaction_count,
    completed_monetary_transaction_count,
    declined_transaction_count,
    balance_inquiry_count,
    deposit_count,
    successful_withdrawal_count,
    closure_event_count,
    total_deposit_amount::numeric(38, 2) as total_deposit_amount,
    total_withdrawal_amount::numeric(38, 2) as total_withdrawal_amount,
    total_declined_amount::numeric(38, 2) as total_declined_amount,
    opening_balance::numeric(18, 2) as opening_balance,
    closing_balance::numeric(18, 2) as closing_balance,
    account_status,
    account_closed,
    first_activity_at,
    last_activity_at,
    source_gold_processed_at,
    loaded_at as serving_loaded_at
from {{ source('bankflow_serving', 'analytics_account_activity') }}
