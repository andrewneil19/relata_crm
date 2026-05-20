with source as (
    select * from {{ source('relata_raw', 'accounts')}}
),

renamed as (
    select
        account_id,
        company_name,
        industry,
        company_size,
        country,
        created_at,
        updated_at
    from source
)

select * from renamed