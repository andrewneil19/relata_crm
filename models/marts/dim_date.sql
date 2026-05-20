--Date spine generates date_day, e.g., 2022-01-01
--Get beginning of time by min(start_date)
--Grain is daily
with date_spine as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="(select date_trunc('month', min(start_date)) from " ~ ref('int_subscriptions_enriched') ~ ")",
        end_date="dateadd('month', 1, date_trunc('month', current_date))"
    ) }}
),

final as (
    select
        --Generated from date spine
        date_day,

        --Year and month attributes
        year(date_day) as year,
        month(date_day) as month_number,
        monthname(date_day) as month_name,
        date_trunc('month', date_day) as first_day_of_month,
        last_day(date_day) as last_day_of_month,

        --Quarter attributes
        quarter(date_day) as quarter_number,
        --Snowflake concatenation. e.g., Q1 2022
        'Q' || quarter(date_day) || ' ' || year(date_day)  as year_quarter,

        --Week and day attributes
        dayofweek(date_day) as day_of_week,
        dayname(date_day) as day_name,
        dayofyear(date_day) as day_of_year,

        --Boolean flag: Sat/Sun - True
        dayofweek(date_day) in (0, 6) as is_weekend

    from date_spine
)

select * from final