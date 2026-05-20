with accounts as (
    select * from {{ ref('stg_accounts') }}
),

final as (
    select
        account_id,
        company_name,
        industry,
        company_size,
        country,
        cast(created_at as date) as account_created_date,
        datediff('day', created_at, current_date) as account_age_days
    from accounts
)

select * from final