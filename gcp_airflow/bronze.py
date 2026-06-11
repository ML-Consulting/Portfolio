import requests
import json
import logging
from typing import List, Dict
import random
import time

from config import config

class TMDBExtractor:
    def __init__(self, api_token: str):
        self.base_url = "https://api.themoviedb.org/3"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json;charset=utf-8"
        }
        self.all_movies: list[dict] = []  # Initialize an empty list to store all movies

    def fetch_discover_movies(self, pages: int = 1) -> List[Dict]:
        """
        Extracts movies from the /discover/movie endpoint.
        """
        self.all_movies = []  # Reset for fresh call
        
        for page in range(1, pages + 1):
            params = {
                "include_adult": "false",
                "include_video": "false",
                "language": "en-US",
                "page": page,
                "sort_by": "popularity.desc"
            }
            
            retries = 3
            for attempt in range(1, retries + 1):
                try:
                    response = requests.get(
                        f"{self.base_url}/discover/movie", 
                        headers=self.headers, 
                        params=params
                    )
                    
                    status = response.status_code

                    if status == 200:
                        logging.info(f"Successfully fetched page {page}")
                        data = response.json()
                        self.all_movies.extend(data.get("results", []))
                        break  # Break out of retry loop on success
                    elif status == 401:
                        logging.error("Unauthorized access - check your API token.")
                        raise Exception("Unauthorized access - check your API token.")
                    elif status in {429, 500, 502, 503, 504}:  # Too Many Requests or Server Errors
                        
                        if attempt == retries:
                            logging.error(f"Reached max retries for page {page}. Status code: {response.status_code}")
                            raise Exception(f"Reached max retries for page {page}. Status code: {response.status_code}")
                        
                        base_delay = 2 ** (attempt - 1)          # 1, 2, 4, 8...
                        jitter = random.uniform(0, 3)          # add 0 to 3 seconds randomness
                        sleep_seconds = base_delay + jitter
                        retry_after = int(response.headers.get("Retry-After", sleep_seconds))
                        
                        logging.warning(f"Rate limit hit. Retrying after {retry_after} seconds...") #polite delay before retrying
                        time.sleep(retry_after)
                        continue  # Retry the same page after polite delay
                
                except requests.exceptions.RequestException as e:
                    logging.error(f"Error fetching page {page} (Attempt {attempt}/{retries}): {e}")
                    if attempt == retries:
                        logging.error(f"Failed to fetch page {page} after {retries} attempts.")
                        raise Exception(f"Failed to fetch page {page} after {retries} attempts.")
                    
        logging.info(f"Reached the requested number of pages: {pages}")
        return self.all_movies

    #Bronze Layer Storage
    def upload_to_gcs(self, data: List[Dict], bucket_name: str, filename: str):

        # configurations for GCS

        """
        Create JSON file and upload to GCS.
        """
        # Create the JSON file first
        try:
            json_data = json.dumps(data, indent=4)
        except Exception as e:
            logging.error(f"Error creating JSON file {filename}: {e}")
            raise
        
        try:
        # Upload to GCS
            client = config.storage_client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(filename)
            blob.upload_from_string(json_data, content_type='application/json')
        except Exception as e:
            logging.error(f"Error uploading {filename} to GCS: {e}")
            raise
        
        logging.info(f"Uploaded {filename} with {len(data)} records")

# --- Execution ---
def get_secret(project_id: str, secret_name: str) -> str:
    """
    Fetches a secret value from Google Secret Manager.
    """
    try:
        client = config.secret_manager_client()
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode("UTF-8").strip()
        
    except Exception as e:
        logging.error(f"Error fetching secret {secret_name}: {e}")
        raise
    
    return secret_value

def bronze_main(project_id: str, bucket_name: str) -> str:

    TMDB_TOKEN = get_secret(project_id, "tmdb")
    number_of_pages = 3

    extractor = TMDBExtractor(TMDB_TOKEN)
    
    # Extraction/storage (Bronze)
    raw_movies = extractor.fetch_discover_movies(pages=number_of_pages)
    extractor.upload_to_gcs(raw_movies, bucket_name, "raw_movies_latest.json")
    return 'Continue to Silver Layer...'

