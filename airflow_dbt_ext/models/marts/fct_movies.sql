with enriched as (
    select * from {{ ref('int_movies_enriched') }}
),

final as (
    select
        id,
        title,
        original_title,
        original_language,
        release_date,
        popularity,
        popularity_tier,
        vote_average,
        rating_bucket,
        vote_count,
        adult,
        video,
        poster_path,
        backdrop_path,
        genre_ids
    from enriched
)

select * from final
