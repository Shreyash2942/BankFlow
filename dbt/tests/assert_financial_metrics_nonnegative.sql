select daily_transaction_key
from {{ ref('analytics_daily_transactions') }}
where
    transaction_count < 0
    or successful_count < 0
    or declined_count < 0
    or requested_amount < 0
    or coalesce(completed_amount, 0) < 0
    or success_rate not between 0 and 1
    or decline_rate not between 0 and 1
