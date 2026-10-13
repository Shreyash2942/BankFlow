{{ config(alias='analytics_account_activity') }}

with ranked_transactions as (
    select
        *,
        row_number() over (
            partition by transaction_date, account_id
            order by occurred_at desc, event_id desc
        ) as account_event_rank
    from {{ ref('int_transaction_metrics') }}
),

transaction_activity as (
    select
        transaction_date as activity_date,
        account_id,
        max(currency) as currency,
        count(*)::bigint as transaction_count,
        count(*) filter (where transaction_type = 'balance_inquiry')::bigint as balance_view_count,
        count(*) filter (where transaction_type = 'withdrawal')::bigint as withdrawal_count,
        count(*) filter (where transaction_type = 'deposit')::bigint as deposit_count,
        count(*) filter (where is_successful)::bigint as successful_count,
        count(*) filter (where is_declined)::bigint as declined_count,
        coalesce(sum(amount) filter (where transaction_type = 'withdrawal' and is_successful), 0)::numeric(18, 2)
            as completed_withdrawal_amount,
        coalesce(sum(amount) filter (where transaction_type = 'deposit' and is_successful), 0)::numeric(18, 2)
            as completed_deposit_amount,
        max(balance_after) filter (where account_event_rank = 1)::numeric(18, 2) as latest_balance,
        max(account_status) filter (where account_event_rank = 1) as latest_account_status,
        min(occurred_at) as first_transaction_at,
        max(occurred_at) as last_transaction_at
    from ranked_transactions
    group by transaction_date, account_id
),

authentication_activity as (
    select
        occurred_at_utc::date as activity_date,
        account_id,
        count(*)::bigint as authentication_event_count,
        count(*) filter (where authentication_outcome = 'authenticated')::bigint
            as successful_authentication_count,
        count(*) filter (where authentication_outcome in ('invalid_credentials', 'card_unavailable'))::bigint
            as failed_authentication_count,
        count(*) filter (where authentication_outcome = 'card_locked')::bigint
            as card_lock_count
    from {{ ref('stg_authentication_events') }}
    where account_id is not null
    group by occurred_at_utc::date, account_id
),

activity_keys as (
    select activity_date, account_id from transaction_activity
    union
    select activity_date, account_id from authentication_activity
)

select
    activity_keys.activity_date::text || '|' || activity_keys.account_id::text as account_activity_key,
    activity_keys.activity_date,
    activity_keys.account_id,
    transaction_activity.currency,
    coalesce(transaction_activity.transaction_count, 0)::bigint as transaction_count,
    coalesce(transaction_activity.balance_view_count, 0)::bigint as balance_view_count,
    coalesce(transaction_activity.withdrawal_count, 0)::bigint as withdrawal_count,
    coalesce(transaction_activity.deposit_count, 0)::bigint as deposit_count,
    coalesce(transaction_activity.successful_count, 0)::bigint as successful_count,
    coalesce(transaction_activity.declined_count, 0)::bigint as declined_count,
    coalesce(transaction_activity.completed_withdrawal_amount, 0)::numeric(18, 2)
        as completed_withdrawal_amount,
    coalesce(transaction_activity.completed_deposit_amount, 0)::numeric(18, 2)
        as completed_deposit_amount,
    transaction_activity.latest_balance,
    transaction_activity.latest_account_status,
    transaction_activity.first_transaction_at,
    transaction_activity.last_transaction_at,
    coalesce(authentication_activity.authentication_event_count, 0)::bigint
        as authentication_event_count,
    coalesce(authentication_activity.successful_authentication_count, 0)::bigint
        as successful_authentication_count,
    coalesce(authentication_activity.failed_authentication_count, 0)::bigint
        as failed_authentication_count,
    coalesce(authentication_activity.card_lock_count, 0)::bigint as card_lock_count
from activity_keys
left join transaction_activity using (activity_date, account_id)
left join authentication_activity using (activity_date, account_id)
