CREATE TABLE IF NOT EXISTS `{project}.{dataset}.{table}` (
  id INT64,
  title STRING,
  release_date DATE,
  popularity FLOAT64,
  vote_average FLOAT64,
  vote_count INT64
);

CREATE OR REPLACE EXTERNAL TABLE `{project}.{dataset}.stg_movies_latest`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://{bucket_name}/silver_movies_latest.parquet']
);


MERGE `{project}.{dataset}.{table}` T
USING `{project}.{dataset}.stg_movies_latest` S
ON T.id = S.id
WHEN MATCHED THEN
  UPDATE SET 
    T.popularity = S.popularity,
    T.vote_average = S.vote_average,
    T.vote_count = S.vote_count
WHEN NOT MATCHED THEN
  INSERT (id, title, release_date, popularity, vote_average, vote_count)
  VALUES (
    S.id, 
    S.title, 
    -- FIX: Convert the INT64/Timestamp to a DATE
    
      DATE(
        TIMESTAMP_SECONDS(
          CAST(S.release_date / 1e9 AS INT64)
        )
      )
    , 
    S.popularity, 
    S.vote_average, 
    S.vote_count
  );