--Date spine generates 1st day of month as date_month, e.g., 2022-01-01
--Get beginning of time by min(start_date)
--Grain is monthly
with date_spine as (
    {{ dbt_utils.date_spine(
        datepart="month",
        start_date="(select date_trunc('month', min(start_date)) from " ~ ref('int_subscriptions_enriched') ~ ")",
        end_date="date_trunc('month', current_date)"
    ) }}
),

--Enable cross join
subscriptions as (
    select * from {{ ref('int_subscriptions_enriched') }}
),

subscription_months as (
    select
        --1st day of month and last day of month
        d.date_month as month_start,
        last_day(d.date_month) as month_end,
        
        s.subscription_id,
        s.account_id,
        s.plan_id,
        s.plan_name,
        s.mrr

    from date_spine d
    cross join subscriptions s

    where
        --Sub started by last day of this month
        s.start_date <= month_end
        --Sub not ended before first day of this month
        --Null end_date means sub still active
        and (s.end_date is null or s.end_date >= month_start)
),

final as (
    select
        month_start,
        month_end,

        --Core MRR metrics. Add ARR, annualized run rate (estimate if MRR flat)
        sum(mrr) as total_mrr,
        sum(mrr) * 12 as arr,

        --Sub and account counts
        count(distinct subscription_id) as active_subscriptions,
        count(distinct account_id)      as active_accounts,

    from subscription_months
    group by month_start, month_end
)

select * from final
order by month_start
