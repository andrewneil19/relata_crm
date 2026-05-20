with subscriptions as (
    --Includes joining to plans
    select * from {{ ref('int_subscriptions_enriched') }}
),

accounts as (
    --Pull in some accounts fields
    select
        account_id,
        company_name,
        industry,
        country
    from {{ ref('stg_accounts') }}
),

final as (
    select
        --Keys
        s.subscription_id,
        s.account_id,
        s.plan_id,

        --Account context (denormalized for convenience)
        a.company_name,
        a.industry,
        a.country,

        --Plan context (already joined in int model)
        s.plan_name,
        s.seat_count,
        s.max_seats,

        --Rely on the calculated version, not monthly_amount
        s.mrr,

        --Status and boolean flags
        s.status,
        s.status = 'active'    as is_active,
        s.status = 'cancelled' as is_churned,

        --Date columns and derived time metrics (useful for cohort and aging analysis)
        s.start_date,
        s.end_date,
        datediff('day', s.start_date, current_date) as subscription_age_days,
        datediff('day', s.start_date, coalesce(s.end_date, current_date)) as subscription_lifespan_days

    from subscriptions s
    left join accounts a on s.account_id = a.account_id
)

select * from final