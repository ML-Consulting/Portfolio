
from google.cloud import bigquery
from google.oauth2.service_account import Credentials
import pandas as pd
import os
import json

import gspread
from gspread_dataframe import set_with_dataframe
import logging

from config import config
    
def call_sproc(client: bigquery.Client):

    params = {
        "project": config.project_id,
        "dataset": config.dataset,
        "table_sold_homes": config.sold_homes_table,
        "table_mls_notes": config.mls_notes_table,
    }

    li_sql = ["sync_sold_homes_notes.sql", "delete_no_notes_prior_days.sql"]

    for li in li_sql:
        sql_path = os.path.join(os.path.dirname(__file__), li)

        with open(sql_path, 'r') as f:
            raw_sql = f.read()

        formatted_sql = raw_sql.format(**params)

        try:
            query_job = client.query(formatted_sql)
            query_job.result() # Wait for the job to complete
            logging.info(f"Procedure {li} executed successfully.")
        except Exception as e:
            logging.error(f"An error occurred executing {li}: {e}")
            raise
    
    

def bq_table_df(client: bigquery.Client) -> pd.DataFrame:
    
    query = f"""
        SELECT 
            CoListAgentDirectPhone,
            CoListAgentFullName,
            CoListOfficeName,
            ListAgentDirectPhone,
            MFR_CurrentPrice,
            ListAgentEmail,
            ListAgentFullName,
            ListOfficeName,
            ListPrice,
            PostalCode,
            CountyOrParish,
            UnparsedAddress,
            City,
            EXCLUDE_FROM_CALLS,
            ALREADY_CALLED,
            SEND_EMAIL,
            NOTES
        FROM `{config.project_id}.{config.dataset}.{config.sold_homes_table}`
        -- This filter finds the single latest record for each address
        QUALIFY ROW_NUMBER() OVER(PARTITION BY UnparsedAddress ORDER BY ingestion_ts DESC) = 1
    """
    return client.query(query).to_dataframe()

def write_df_to_sheet(
    start_row: int = 1,
    start_col: int = 1,
    include_header: bool = True,
    clear_before: bool = True,
    ) -> tuple[str, int]:

    sheet_id = config.sheet_id
    sheet_name = config.sheet_name
    
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    secret = config.get_secret_gsheet()
    secret_json = json.loads(secret)
    creds = Credentials.from_service_account_info(secret_json, scopes=scopes)
    gc = gspread.Client(auth=creds)

    try:
         sh = gc.open_by_key(sheet_id)   
         ws = sh.worksheet(sheet_name)
    except Exception as e:
        logging.error(f"Error accessing Google Sheet: {e}")
        raise

    df = bq_table_df(client = config.bq_client())

    if clear_before:
        ws.clear()

    set_with_dataframe(
        ws,
        df,
        row=start_row,
        col=start_col,
        include_column_header=include_header,
        resize=True,
    )

    logging.info(f"Wrote {len(df)} rows to '{sheet_name}'")
    return ("OK", 200)




