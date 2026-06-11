from pydantic import BaseModel, ValidationError
import logging
from typing import Optional
from datetime import date


class DtoGrid(BaseModel):
    adult: Optional[bool] = None
    backdrop_path: Optional[str] = None
    genre_ids: Optional[list[int]] = None
    id: int
    original_language: Optional[str] = None
    original_title: Optional[str] = None
    overview: Optional[str] = None
    popularity: Optional[float] = None
    poster_path: Optional[str] = None
    release_date: Optional[date] = None
    title: Optional[str] = None
    video: Optional[bool] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    

    @staticmethod
    def validation(records: list[dict]) -> tuple[list[dict], list[dict]]:
        """Process a batch of records, returning valid and invalid ones separately"""
        valid_records = []
        invalid_records = []
        
        for i, record in enumerate(records):
            try:
                dto = DtoGrid(**record)  # Using **kwargs unpacking
                valid_records.append(dto.model_dump())
            except ValidationError as e:
                logging.warning(f"Record {i} validation failed: {e}")
                invalid_records.append({"record": record, "error": str(e)})
        return valid_records, invalid_records
