with source_events as (
    select *
    from {{ source('bankflow', 'consumed_events') }}
    where payload ->> 'kind' = 'authentication'
)

select
    event_id,
    event_type,
    schema_version,
    occurred_at,
    occurred_at at time zone 'UTC' as occurred_at_utc,
    consumed_at,
    source,
    topic,
    partition as kafka_partition,
    "offset" as kafka_offset,
    consumer_group,
    nullif(payload ->> 'customer_id', '')::uuid as customer_id,
    nullif(payload ->> 'account_id', '')::uuid as account_id,
    nullif(payload ->> 'card_id', '')::uuid as card_id,
    payload ->> 'outcome' as authentication_outcome,
    nullif(payload ->> 'remaining_attempts', '')::integer as remaining_attempts
from source_events
