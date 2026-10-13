with expected as (
    select transaction_date, currency, transaction_type, count(*)::bigint as transaction_count
    from {{ ref('int_transaction_metrics') }}
    group by transaction_date, currency, transaction_type
),

actual as (
    select transaction_date, currency, transaction_type, transaction_count
    from {{ ref('analytics_daily_transactions') }}
)

select
    coalesce(expected.transaction_date, actual.transaction_date) as transaction_date,
    coalesce(expected.currency, actual.currency) as currency,
    coalesce(expected.transaction_type, actual.transaction_type) as transaction_type
from expected
full outer join actual using (transaction_date, currency, transaction_type)
where expected.transaction_count is distinct from actual.transaction_count
