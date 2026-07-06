
from google.cloud import bigquery
from datetime import datetime, timedelta
import time
import random

from dto import GridDTO
import requests
import logging

from config import config



def fetch_mls_data_recursive(url: str, headers: dict, payload: dict, all_items=None) -> list:
    retries = 3
    
    if all_items is None:
        all_items = []
    
    # Make the API request
    for attempt in range(1, retries + 1):
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                break  # Success, exit retry loop
            elif response.status_code == 401:
                logging.error("Unauthorized access - check your API token.")
                raise Exception("Unauthorized access - check your API token.")
            elif response.status_code in {429, 500, 502, 503, 504}:  # Too Many Requests or Server Errors
                if attempt == retries:
                    logging.error(f"Reached max retries for URL {url}. Status code: {response.status_code}")
                    raise Exception(f"Reached max retries for URL {url}. Status code: {response.status_code}")
                base_delay = 2 ** (attempt - 1)          # Exponential backoff: 1, 2, 4, 8...
                jitter = random.uniform(0, 3)          # Add some randomness to avoid thundering herd
                delay = base_delay + jitter
                logging.warning(f"Request failed with status {response.status_code}. Retrying in {delay:.2f} seconds...")
                time.sleep(delay) # polite delay before retrying
            else:
                logging.error(f"Error fetching data from MLS API: {response.status_code} - {response.text}")
                raise Exception(f"MLS API request failed with status code {response.status_code}")
        except requests.RequestException as e:
            logging.error(f"Request error: {e}")
            if attempt == retries:
                raise
        
  
    resp = response.json()
    try:
    # Extract and process items from current page
        for item in resp.get('value', []):            
            processed_item = {
                "CoListAgentDirectPhone": item.get("CoListAgentDirectPhone", ""),
                "CoListAgentFullName": item.get("CoListAgentFullName", ""),
                "CoListOfficeName": item.get("CoListOfficeName", ""),
                "ListAgentDirectPhone": item.get("ListAgentDirectPhone", ""),
                "MFR_CurrentPrice": item.get("MFR_CurrentPrice", None),
                "ListAgentEmail": item.get("ListAgentEmail", ""),
                "ListAgentFullName": item.get("ListAgentFullName", ""),
                "ListOfficeName": item.get("ListOfficeName", ""),
                "ListPrice": item.get("ListPrice", None),
                "PostalCode": item.get("PostalCode", ""),
                "CountyOrParish": item.get("CountyOrParish", ""),
                "UnparsedAddress": item.get("UnparsedAddress", ""),
                "City": item.get("City", "")
            }
            all_items.append(processed_item)

    except Exception as e:
        logging.error(f"Error processing response: {e}")
        raise

    # Base case: no more pages
    if '@odata.nextLink' not in resp:
        all_valid_items, all_invalid_items = GridDTO.process_records_batch(all_items)  # Validate each item and log any issues
        if len(all_items) != (len(all_invalid_items) + len(all_valid_items)):
            raise Exception(f"Total records mismatch - total records: {len(all_items)}, invalid records: {len(all_invalid_items)}, valid records: {len(all_valid_items)}")
        if len(all_valid_items) == 0:
            raise Exception("No valid records returned from MLS API.")
        logging.info(f"Total valid records: {len(all_valid_items)}, Total invalid records: {len(all_invalid_items)}") # checking invalid items count
        return all_valid_items
    
    # Recursive case: fetch next page
    next_url = resp['@odata.nextLink']
    return fetch_mls_data_recursive(next_url, headers, payload, all_items)

def write_to_bigquery(data: list[dict]) -> bigquery.LoadJob:
    """Write data to BigQuery table"""
    client = config.bq_client()
    table_ref = f"{config.project_id}.{config.dataset}.{config.sold_homes_table}"
    
    # Define schema
    schema = GridDTO.bq_schema()
    
    # Add processed timestamp to each record
    processed_time = datetime.utcnow()
    for record in data:
        record['ingestion_ts'] = processed_time.isoformat()
    
    # Configure job to append data
    try:
        job_config = bigquery.LoadJobConfig(
            schema=schema,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        )
        
        # Load data
        job = client.load_table_from_json(data, table_ref, job_config=job_config)
        job.result()  # Wait for the job to complete
        logging.info(f"Loaded {len(data)} rows to {table_ref}")
    except Exception as e:
        logging.error(f"Error loading data to BigQuery: {e}")
        raise
    
    return job

def get_previous_day() -> str:
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime('%Y-%m-%d')


def main():
    
    """Main function to orchestrate the data fetching"""
    key = config.get_secret_mls()
    previous_day = get_previous_day()
    url = (f"https://api.mlsgrid.com/v2/Property?$filter=OriginatingSystemName%20eq%20'mfrmls'%20"
           f"and%20ModificationTimestamp%20ge%20{previous_day}T00:00:00Z%20"
           f"and%20StandardStatus%20eq%20'Pending'")
    
    payload = {}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Bearer {key}',
        'Accept': 'application/json'
    }
    
    # Fetch all data using recursive function
    try:
        all_properties = fetch_mls_data_recursive(url, headers, payload)
        logging.info(f"Properties in target counties (Seminole, Orange): {len(all_properties)}")
    except Exception as e:
        logging.error(f"Error fetching MLS data: {e}")
        return ("ERROR", 500)
    try:
        write_to_bigquery(all_properties)
        return ("OK", 200)
    except Exception as e:
        logging.error(f"Error writing to BigQuery: {e}")
        return ("ERROR", 500)

