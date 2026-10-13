{{ config(alias='analytics_daily_transactions') }}

select
    transaction_date::text || '|' || currency || '|' || transaction_type as daily_transaction_key,
    transaction_date,
    currency,
    transaction_type,
    count(*)::bigint as transaction_count,
    count(*) filter (where is_successful)::bigint as successful_count,
    count(*) filter (where is_declined)::bigint as declined_count,
    sum(amount)::numeric(18, 2) as requested_amount,
    coalesce(sum(amount) filter (where is_successful), 0)::numeric(18, 2) as completed_amount,
    avg(amount)::numeric(18, 2) as average_amount,
    round(count(*) filter (where is_successful)::numeric / nullif(count(*), 0), 4) as success_rate,
    round(count(*) filter (where is_declined)::numeric / nullif(count(*), 0), 4) as decline_rate,
    min(occurred_at) as first_event_at,
    max(occurred_at) as last_event_at
from {{ ref('int_transaction_metrics') }}
group by transaction_date, currency, transaction_type
