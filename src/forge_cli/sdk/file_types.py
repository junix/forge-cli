from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class File(BaseModel):
    """
    Represents a file entity with its attributes.
    """

    id: str
    object_field: str = Field(alias="object")
    custom_id: str | None = None
    filename: str
    bytes: int
    content_type: str
    md5: str | None = None
    purpose: str
    status: str
    created_at: datetime
    updated_at: datetime
    task_id: str | None = None
    processing_error_message: str | None = None
    metadata: dict[str, Any] | None = None

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
