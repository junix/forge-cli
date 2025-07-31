from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class File(BaseModel):
    """
    Represents a file entity with its attributes.
    """

    id: str
    object_field: str = Field(alias="object")
    custom_id: str | None = None
    filename: str
    bytes: int
    content_type: str | None = None
    md5: str | None = None
    purpose: str
    status: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    task_id: str | None = None
    processing_error_message: str | None = None
    metadata: dict[str, Any] | None = None

    @field_validator('created_at', mode='before')
    @classmethod
    def parse_created_at(cls, v):
        """Convert Unix timestamp to datetime if needed."""
        if isinstance(v, int):
            return datetime.fromtimestamp(v)
        return v
    
    @field_validator('updated_at', mode='before')
    @classmethod
    def parse_updated_at(cls, v):
        """Convert Unix timestamp to datetime if needed."""
        if v is None:
            return None
        if isinstance(v, int):
            return datetime.fromtimestamp(v)
        return v

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
