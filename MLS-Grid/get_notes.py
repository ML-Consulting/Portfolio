import json
from datetime import datetime, timezone
import pandas as pd
import pandas_gbq


import gspread
from google.oauth2.service_account import Credentials
import logging

from config import config

def get_sheet() -> pd.DataFrame:
    
    #--------Google Sheets Config-------------
    sheet_id = config.sheet_id
    sheet_name = config.sheet_name
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    secret = config.get_secret_gsheet()
    secret_json = json.loads(secret)
    creds = Credentials.from_service_account_info(
        secret_json, 
        scopes=scopes
    )

    client = gspread.Client(auth=creds)

    try:
        sh = client.open_by_key(sheet_id)   
        ws = sh.worksheet(sheet_name)                

        data = ws.get_all_values()
                
        df = pd.DataFrame(data[1:], columns=data[0])

        filter_df = (
            df["EXCLUDE_FROM_CALLS"].replace("",pd.NA).notna()   |
            df["ALREADY_CALLED"].replace("",pd.NA).notna()       |
            df["SEND_EMAIL"].replace("",pd.NA).notna()           |
            df["NOTES"].replace("",pd.NA).notna()
        )
    except Exception as e:
        logging.error(f"Error fetching data from Google Sheets: {e}")
        raise


    keep_cols = [
        "ListAgentDirectPhone",
        "UnparsedAddress",
        "EXCLUDE_FROM_CALLS",
        "ALREADY_CALLED",
        "SEND_EMAIL",
        "NOTES",

        # plus any extras you want
    ]

    return df.loc[filter_df, keep_cols].copy()

def write_to_bq():

    # ------- BQ Config --------------------------
    project_id = config.project_id
    dataset = config.dataset
    table = config.mls_notes_table

    destination_table = f"{dataset}.{table}" 

    # ------- Extract ----------------------------
    df = get_sheet()


    df["ts_job"] = pd.Timestamp.now(tz="UTC")

    # ------- Load -------------------------------
    try:
        pandas_gbq.to_gbq(
            dataframe=df,
            destination_table=destination_table,
            project_id=project_id,
            if_exists="append",
        )
    except Exception as e:
        logging.error(f"Error writing to BigQuery: {e}")
        raise

    logging.info(f"Uploaded {len(df)} rows to {project_id}.{destination_table}")
    return ("OK", 200)

