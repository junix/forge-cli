from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FileCounts(BaseModel):
    in_progress: int
    completed: int
    failed: int
    cancelled: int
    total: int


class Vectorstore(BaseModel):
    """
    Represents a vector store entity with its attributes.
    """

    id: str
    object_field: str = Field(alias="object")
    name: str
    description: str | None = None
    file_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    bytes: int | None = None
    file_counts: FileCounts
    task_id: str | None = None
    last_task_status: str | None = None
    last_processed_at: datetime | None = None

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
