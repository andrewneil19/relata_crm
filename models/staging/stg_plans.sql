with source as (
    select * from {{ source('relata_raw', 'plans') }}
),

renamed as (
    select
        plan_id,
        plan_name,
        base_price,
        price_per_seat,
        max_seats
    from source
)

select * from renamed