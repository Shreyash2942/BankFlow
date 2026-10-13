with daily_transactions as (
    select transaction_date as activity_date, account_id, count(*)::bigint as transaction_count
    from {{ ref('int_transaction_metrics') }}
    group by transaction_date, account_id
)

select
    coalesce(daily_transactions.activity_date, account_activity.activity_date) as activity_date,
    coalesce(daily_transactions.account_id, account_activity.account_id) as account_id
from daily_transactions
full outer join {{ ref('analytics_account_activity') }} as account_activity
    using (activity_date, account_id)
where
    daily_transactions.transaction_count is distinct from account_activity.transaction_count
    and coalesce(daily_transactions.transaction_count, 0) > 0
