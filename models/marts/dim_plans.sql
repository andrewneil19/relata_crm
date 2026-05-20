with plans as (
    select * from {{ ref('stg_plans') }}
),

final as (
    select
        plan_id,
        plan_name,
        base_price,
        price_per_seat,
        max_seats,

        --Set numeric sorting order for plan tiers
        case plan_name
            when 'Starter' then 1
            when 'Pro' then 2
            when 'Enterprise' then 3
        end as plan_tier_order
    from plans
)

select * from final