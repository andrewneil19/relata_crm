with subscriptions as (
    select * from {{ ref('stg_subscriptions') }}
),

plans as (
    select * from {{ ref('stg_plans') }}
),

enriched as (
    select
        --sub identifiers
        s.subscription_id,
        s.account_id,

        --plan details joined in from stg_plans
        s.plan_id,
        p.plan_name,
        p.base_price,
        p.price_per_seat,
        p.max_seats,

        --subscription details
        s.status,
        s.seat_count,

        --derived MRR calculation: base price + (seats × price per seat)
        p.base_price + (s.seat_count * p.price_per_seat) as mrr,

        --keep monthly_amount from source as cross-check field
        s.monthly_amount as source_mrr,

        s.start_date,
        s.end_date,
        s.created_at
    from subscriptions s left join plans p on s.plan_id = p.plan_id
)

select * from enriched