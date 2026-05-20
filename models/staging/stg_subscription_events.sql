with 
source as (
    select * from {{ source('relata_raw', 'subscription_events') }}
),

renamed as (
    select
        event_id,
        subscription_id,
        account_id,
        to_plan_id,
        from_plan_id,
        from_seats,
        to_seats,
        to_mrr,
        from_mrr,
        created_at,
        event_date,
        event_type,
    from source
)

select * from renamed