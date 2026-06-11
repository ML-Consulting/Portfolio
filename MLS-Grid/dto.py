from typing import Optional
from pydantic import BaseModel, ValidationError, field_validator
import logging
from google.cloud import bigquery


class GridDTO(BaseModel):
    CoListAgentDirectPhone: Optional[str] = None
    CoListAgentFullName: Optional[str] = None
    CoListOfficeName: Optional[str] = None
    ListAgentDirectPhone: Optional[str] = None
    MFR_CurrentPrice: Optional[float] = None
    ListAgentEmail: Optional[str] = None
    ListAgentFullName: Optional[str] = None
    ListOfficeName: Optional[str] = None
    ListPrice: Optional[float] = None
    PostalCode: Optional[str] = None
    CountyOrParish: str = None
    UnparsedAddress: Optional[str] = None
    City: Optional[str] = None

    @field_validator('CountyOrParish')
    @classmethod
    def validate_county(cls, v) -> str:
        if v and v.strip() not in ['Seminole', 'Orange']:
            raise ValueError('Invalid county')
        return v.strip() if v else v

    @staticmethod
    def process_records_batch(records: list[dict]) -> tuple[list[dict], list[dict]]:
        """Process a batch of records, returning valid and invalid ones separately"""
        valid_records = []
        invalid_records = []
        
        for i, record in enumerate(records):
            try:
                dto = GridDTO(**record)  # Using **kwargs unpacking
                valid_records.append(dto.model_dump())
            except ValidationError as e:
                logging.warning(f"Record {i} validation failed: {e}")
                invalid_records.append({"record": record, "error": str(e)})
        return valid_records, invalid_records

    @staticmethod
    def bq_schema() -> list[bigquery.SchemaField]:
        """Return BigQuery schema based on the DTO fields"""
        return [
            bigquery.SchemaField("CoListAgentDirectPhone", "STRING"),
            bigquery.SchemaField("CoListAgentFullName", "STRING"),
            bigquery.SchemaField("CoListOfficeName", "STRING"),
            bigquery.SchemaField("ListAgentDirectPhone", "STRING"),
            bigquery.SchemaField("MFR_CurrentPrice", "FLOAT"),
            bigquery.SchemaField("ListAgentEmail", "STRING"),
            bigquery.SchemaField("ListAgentFullName", "STRING"),
            bigquery.SchemaField("ListOfficeName", "STRING"),
            bigquery.SchemaField("ListPrice", "FLOAT"),
            bigquery.SchemaField("PostalCode", "STRING"),
            bigquery.SchemaField("CountyOrParish", "STRING"),
            bigquery.SchemaField("UnparsedAddress", "STRING"),
            bigquery.SchemaField("City", "STRING"),
            bigquery.SchemaField("ingestion_ts", "TIMESTAMP")
        ]
