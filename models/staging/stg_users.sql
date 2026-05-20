with source as (
    select * from {{ source('relata_raw', 'users') }}
),

renamed as (
    select
        user_id,
        account_id,
        email,
        first_name,
        last_name,
        role,
        created_at,
        is_active
    from source
)

select * from renamed