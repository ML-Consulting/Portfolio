with source as (
    select * from {{ source('stg_movies_latest', 'stg_movies_latest') }}
),

renamed as (
    select
        id,
        title,
        original_title,
        original_language,
        overview,
        safe.parse_date('%Y-%m-%d', release_date)           as release_date,
        format_date('%Y-%m', safe.parse_date('%Y-%m-%d', release_date)) as yr_mo,
        cast(popularity as float64)       as popularity,
        cast(vote_average as float64)     as vote_average,
        cast(vote_count as int64)         as vote_count,
        adult,
        video,
        poster_path,
        backdrop_path,
        genre_ids
    from source
)

select * from renamed
