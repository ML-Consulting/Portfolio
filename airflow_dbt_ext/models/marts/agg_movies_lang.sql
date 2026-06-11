select *
from (select 
    id,
    title,
    original_title,
    original_language,
    yr_mos_release,
    popularity,
    popularity_tier,
    vote_average,
    rating_bucket,
    vote_count,
    adult,
    video,
    poster_path,
    backdrop_path 
    from {{ ref('int_movies_enriched') }} 
    where id is not null -- date limier for incremental load
    Group by    
        id,
        title,
        original_title,
        original_language,
        yr_mos_release,
        popularity,
        popularity_tier,
        vote_average,
        rating_bucket,
        vote_count,
        adult,
        video,
        poster_path,
        backdrop_path
    ) as sub