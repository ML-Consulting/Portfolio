
from google.cloud import secretmanager
from google.cloud import bigquery
import logging
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    project_id: str
    dataset: str
    table: str
    secret_name: str
    sheet_id: str
    sheet_name: str
    sold_homes_table: str
    mls_notes_table: str

    def get_secret_gsheet(self) -> str:
        """
        Fetches a secret value from Google Secret Manager.
        """
        try:
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{self.project_id}/secrets/{self.secret_name}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            secret_value = response.payload.data.decode("UTF-8").strip()
            return secret_value
        except Exception as e:
            logging.error(f"Error fetching secret {self.secret_name}: {e}")
            raise

    def get_secret_mls(self) -> str:
        """
        Fetches a secret value from Google Secret Manager.
        """
        try:
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{self.project_id}/secrets/{self.secret_name}/versions/1"
            response = client.access_secret_version(request={"name": name})
            secret_value = response.payload.data.decode("UTF-8").strip()
            return secret_value
        except Exception as e:
            logging.error(f"Error fetching secret {self.secret_name}: {e}")
            raise

    def bq_client(self) -> bigquery.Client:
        """
        Creates and returns a BigQuery client.
        """
        try:
            client = bigquery.Client(project=self.project_id)
            return client
        except Exception as e:
            logging.error(f"Error creating BigQuery client: {e}")
            raise

config = Config() #module level singleton instance for easy access across modules