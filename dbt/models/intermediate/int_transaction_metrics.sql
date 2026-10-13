with terminal_events as (
    select
        *,
        row_number() over (
            partition by transaction_id
            order by occurred_at desc, consumed_at desc, event_id desc
        ) as transaction_rank
    from {{ ref('stg_transaction_events') }}
    where event_type in (
        'balance.viewed',
        'withdrawal.completed',
        'withdrawal.declined',
        'deposit.completed'
    )
)

select
    event_id,
    transaction_id,
    customer_id,
    account_id,
    card_id,
    event_type,
    transaction_type,
    transaction_status,
    amount,
    balance_before,
    balance_after,
    currency,
    account_status,
    decline_reason,
    occurred_at,
    occurred_at_utc,
    consumed_at,
    occurred_at_utc::date as transaction_date,
    date_trunc('hour', occurred_at_utc) as transaction_hour,
    transaction_status = 'completed' as is_successful,
    transaction_status = 'declined' as is_declined
from terminal_events
where transaction_rank = 1
