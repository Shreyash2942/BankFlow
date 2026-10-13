with expected as (
    select
        occurred_at_utc::date as authentication_date,
        event_type,
        authentication_outcome,
        count(*)::bigint as event_count
    from {{ ref('stg_authentication_events') }}
    group by occurred_at_utc::date, event_type, authentication_outcome
),

actual as (
    select authentication_date, event_type, authentication_outcome, event_count
    from {{ ref('analytics_authentication_metrics') }}
)

select
    coalesce(expected.authentication_date, actual.authentication_date) as authentication_date,
    coalesce(expected.event_type, actual.event_type) as event_type,
    coalesce(expected.authentication_outcome, actual.authentication_outcome) as authentication_outcome
from expected
full outer join actual using (authentication_date, event_type, authentication_outcome)
where expected.event_count is distinct from actual.event_count
