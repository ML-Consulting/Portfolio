from google.cloud import storage
from google.cloud import secretmanager
from google.cloud import bigquery

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    project_id: str
    dataset_id: str
    bucket_name: str
    raw_json_path: str
    output_path: str
    dbt_project_dir: str
    dbt_dataset: str
    bq_location: str

    def storage_client(self):
        return storage.Client()

    def secret_manager_client(self):
        return secretmanager.SecretManagerServiceClient()
    
    def bq_client(self):
        return bigquery.Client()

config = Config() #module level singleton instance for easy access across modules