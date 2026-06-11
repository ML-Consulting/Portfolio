with stg as (
    select * from {{ ref('stg_movies') }}
),

enriched as (
    select
        *,
        {{ popularity_tier('popularity') }} as popularity_tier,
        {{ rating_bucket('vote_average') }} as rating_bucket,
        {{ yr_mos('release_date') }} as yr_mos_release
    from stg
    where id is not null
)

select * from enriched
