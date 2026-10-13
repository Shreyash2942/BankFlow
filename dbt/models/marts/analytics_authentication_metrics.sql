{{ config(alias='analytics_authentication_metrics') }}

select
    occurred_at_utc::date::text || '|' || event_type || '|' || authentication_outcome
        as authentication_metric_key,
    occurred_at_utc::date as authentication_date,
    event_type,
    authentication_outcome,
    count(*)::bigint as event_count,
    count(*) filter (where card_id is not null)::bigint as known_card_event_count,
    count(*) filter (where card_id is null)::bigint as unknown_card_event_count,
    avg(remaining_attempts)::numeric(10, 2) as average_remaining_attempts,
    min(occurred_at) as first_event_at,
    max(occurred_at) as last_event_at
from {{ ref('stg_authentication_events') }}
group by occurred_at_utc::date, event_type, authentication_outcome
