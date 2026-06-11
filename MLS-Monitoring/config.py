
from dateutil import parser
from zoneinfo import ZoneInfo
from pydantic_settings import BaseSettings
import ssl
import json

from google.cloud import secretmanager


import logging

class Config(BaseSettings):
    project_id: str
    pubsub_id: str
    smtp_server: str
    smtp_port: int
    secret_name: str
    context: ssl.SSLContext = ssl.create_default_context()

    def get_gmail_creds(self) -> tuple[str, str]:
        """
        Fetches a secret value from Google Secret Manager.
        """
        try:
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{self.project_id}/secrets/{self.secret_name}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            secret_value = response.payload.data.decode("UTF-8").strip()

            email = json.loads(secret_value).get("email")
            password = json.loads(secret_value).get("password")

            return email, password
        except Exception as e:
            logging.error(f"Error fetching secret {self.secret_name}: {e}")
            raise

    @staticmethod
    def time_util_now(ts: str) -> str:
        """
        Converts a timestamp string to ISO format.
        """
        try:
            dt = parser.parse(ts)

            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo("America/New_York"))
            return dt.strftime("%Y-%m-%dT%H:%M")
        except Exception as e:
            logging.error(f"Error parsing timestamp {ts}: {e}")
            raise

config = Config() #module level singleton instance for easy access across modules