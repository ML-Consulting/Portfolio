BEGIN

MERGE `{project}.{dataset}.{table_sold_homes}` AS a
USING (
  SELECT *
  FROM `{project}.{dataset}.{table_mls_notes}`
  -- This filters for the newest record per phone number
  QUALIFY ROW_NUMBER() OVER(PARTITION BY ListAgentDirectPhone ORDER BY ts_job DESC) = 1
) AS b
ON a.ListAgentDirectPhone = b.ListAgentDirectPhone
WHEN MATCHED THEN
  UPDATE SET a.EXCLUDE_FROM_CALLS = b.exclude_from_calls;

MERGE `{project}.{dataset}.{table_sold_homes}` AS a
USING (
  SELECT *
  FROM `{project}.{dataset}.{table_mls_notes}`
  -- Partition by both join keys to find the latest record for this specific pair
  QUALIFY ROW_NUMBER() OVER(
    PARTITION BY ListAgentDirectPhone, UnparsedAddress 
    ORDER BY ts_job DESC
  ) = 1
) AS b
ON a.ListAgentDirectPhone = b.ListAgentDirectPhone
AND a.UnparsedAddress = b.UnparsedAddress
WHEN MATCHED THEN
  UPDATE SET 
    a.EXCLUDE_FROM_CALLS = b.exclude_from_calls,
    a.ALREADY_CALLED = b.already_called,
    a.SEND_EMAIL = b.send_email,
    a.NOTES = b.notes;

DELETE
FROM `{project}.{dataset}.{table_sold_homes}`
WHERE LENGTH(EXCLUDE_FROM_CALLS)>0;

END