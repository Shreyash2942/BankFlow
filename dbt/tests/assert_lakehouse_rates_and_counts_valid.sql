select *
from {{ ref('lakehouse_daily_transactions') }}
where
    monetary_attempt_count <> successful_transaction_count + declined_transaction_count
    or success_rate < 0
    or success_rate > 1
    or decline_rate < 0
    or decline_rate > 1
    or (
        monetary_attempt_count > 0
        and abs(success_rate + decline_rate - 1) > 0.000001
    )

union all

select
    lakehouse_authentication_key as lakehouse_daily_key,
    metric_date,
    'AUTH' as currency,
    authentication_event_count as transaction_event_count,
    authentication_attempt_count as monetary_attempt_count,
    successful_authentication_count as successful_transaction_count,
    failed_authentication_count + card_lockout_count as declined_transaction_count,
    0 as balance_inquiry_count,
    0 as deposit_count,
    0 as successful_withdrawal_count,
    0 as declined_withdrawal_count,
    0::numeric as total_deposit_amount,
    0::numeric as total_withdrawal_amount,
    0::numeric as total_declined_amount,
    0::numeric as average_transaction_value,
    success_rate,
    failure_rate as decline_rate,
    unique_account_count,
    first_event_at,
    last_event_at,
    source_gold_processed_at,
    serving_loaded_at
from {{ ref('lakehouse_authentication_metrics') }}
where
    authentication_attempt_count
        <> successful_authentication_count + failed_authentication_count + card_lockout_count
    or authentication_event_count <> authentication_attempt_count + session_end_count
    or success_rate < 0
    or success_rate > 1
    or failure_rate < 0
    or failure_rate > 1
    or (
        authentication_attempt_count > 0
        and abs(success_rate + failure_rate - 1) > 0.000001
    )
