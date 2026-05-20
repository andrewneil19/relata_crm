with 
source as (
    select * from {{ source('relata_raw', 'invoices') }}
),

renamed as (
    select
        invoice_id,
        subscription_id,
        account_id,
        amount,
        status,
        paid_at,
        created_at,
        invoice_date,
    from source
)

select * from renamed