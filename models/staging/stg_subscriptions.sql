with 
source as (
    select * from {{ source('relata_raw', 'subscriptions') }}
),

renamed as (
    select
        subscription_id,
        account_id,
        plan_id,
        status,
        end_date,
        created_at,
        seat_count,
        start_date,
        monthly_amount,
    from source

)

select * from renamed