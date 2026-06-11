BEGIN


DELETE
FROM `{project}.{dataset}.{table_sold_homes}`
WHERE
  LENGTH(COALESCE(ALREADY_CALLED, '')) +
  LENGTH(COALESCE(SEND_EMAIL, '')) +
  LENGTH(COALESCE(NOTES, '')) = 0
  AND DATE(ingestion_ts) < CURRENT_DATE();


END