with source_events as (
    select *
    from {{ source('bankflow', 'consumed_events') }}
    where payload ->> 'kind' = 'transaction'
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
    (payload ->> 'transaction_id')::uuid as transaction_id,
    (payload ->> 'customer_id')::uuid as customer_id,
    (payload ->> 'account_id')::uuid as account_id,
    nullif(payload ->> 'card_id', '')::uuid as card_id,
    payload ->> 'transaction_type' as transaction_type,
    payload ->> 'status' as transaction_status,
    (payload ->> 'amount')::numeric(18, 2) as amount,
    (payload ->> 'balance_before')::numeric(18, 2) as balance_before,
    (payload ->> 'balance_after')::numeric(18, 2) as balance_after,
    payload ->> 'currency' as currency,
    payload ->> 'account_status' as account_status,
    nullif(payload ->> 'decline_reason', '') as decline_reason
from source_events
