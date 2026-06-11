import pandas as pd
import io
import logging
import json
from config import config
from dto import DtoGrid

def clean_movie_data(raw_json_path: str) -> pd.DataFrame:
    """
    Read raw JSON from GCS, clean it, and return a DataFrame.
    """
    bucket = config.storage_client().bucket(config.bucket_name)

    try:
        blob = bucket.blob(raw_json_path)
        content = blob.download_as_text()
        data = json.loads(content)
    except Exception as e:
        logging.error(f"Error reading raw JSON from GCS: {e}")
        raise
    
###########################################################################################
#validate and keep only valid records, using DTOs for schema enforcement and type safety, 
#invalid records are logged and can be prepared for downstream analysis of data quality issues
###########################################################################################
    data_valid, data_invalid = DtoGrid.validation(data) 

    if len(data) == 0 or len(data_invalid) / len(data) > 0.05: #if more than 5% of records are invalid, log a warning
         logging.warning(f"Validated data: {len(data_valid)} valid records, {len(data_invalid)} invalid records")
         raise Exception("Too many invalid records in the dataset. Check logs for details.")
    
    logging.info(f"Validated data: {len(data_valid)} valid records, {len(data_invalid)} invalid records")
    
    df = pd.DataFrame(data_valid)

    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['title'] = df['title'].fillna('Unknown Title')
    df['popularity'] = df['popularity'].fillna(0.0)

    df = df.drop_duplicates(subset='id')
    df = df.dropna(subset=['release_date'])

    logging.info(f"Cleaned data: {len(df)} records after dropping duplicates and missing release dates")

    return df

def save_to_silver(df: pd.DataFrame, output_path: str):
    """
    Save the cleaned DataFrame back to GCS as a Parquet file.
    Parquet is chosen for it's efficiency and data type preservation.
    """
    try:
        output_buffer = io.BytesIO()
        df.to_parquet(output_buffer, index=False)
        output_buffer.seek(0)

        blob = config.storage_client().bucket(config.bucket_name).blob(output_path)
        blob.upload_from_file(output_buffer, content_type='application/octet-stream')
    except Exception as e:
        logging.error(f"Error saving cleaned data to GCS: {e}")
        raise

    logging.info(f"Saved cleaned data to {output_path}")

# if __name__ == "__main__":
def silver_main(bucket_name: str, raw_json_path: str, output_path: str) -> str:

    cleaned_df = clean_movie_data(raw_json_path)
    save_to_silver(cleaned_df, output_path)
    return 'Continue to Gold Layer...'