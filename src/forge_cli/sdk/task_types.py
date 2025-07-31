from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class TaskStatus(BaseModel):
    """
    Represents the status and details of an asynchronous task.
    """

    id: str = Field(description="The unique identifier for the task.")
    object_field: str = Field(default="task", alias="object", description="The type of object, typically 'task'.")
    type: str | None = Field(
        None, description="The type of operation the task is performing (e.g., 'file_processing', 'vector_store_creation')."
    )
    status: str = Field(description="The current status of the task.")

    created_at: datetime | None = Field(None, description="Timestamp when the task was created.")
    updated_at: datetime | None = Field(None, description="Timestamp when the task was last updated.")

    progress: float | None = Field(None, description="Task completion progress (e.g., percentage).", ge=0, le=100)
    result: dict[str, Any] | None = Field(
        None, description="The result of the task if completed successfully. Structure may vary based on task type."
    )
    error_message: str | None = Field(None, description="Error message if the task failed.")
    
    # Additional fields from the actual server response
    data: dict[str, Any] | None = Field(None, description="Additional task data from server.")
    failure_reason: str | None = Field(None, description="Detailed failure reason if task failed.")

    # Optional field to link back to the resource that initiated or is related to this task
    resource_id: str | None = Field(
        None,
        description="Identifier of the primary resource associated with this task (e.g., file_id, vector_store_id).",
    )

    @field_validator('created_at', mode='before')
    @classmethod
    def parse_created_at(cls, v):
        """Convert Unix timestamp to datetime if needed."""
        if v is None:
            return None
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
        allow_population_by_field_name = True  # Alias for 'object_field'
        json_encoders = {datetime: lambda v: v.isoformat()}


# Example usage (not part of the file, just for illustration):
# task_data = {
#     "id": "task_123",
#     "object": "task",
#     "type": "file_processing",
#     "status": "completed",
#     "created_at": "2023-01-01T12:00:00Z",
#     "updated_at": "2023-01-01T12:05:00Z",
#     "result": {"file_id": "file_abc", "details": "Processing successful"},
#     "resource_id": "file_abc"
# }
# task_status_obj = TaskStatus(**task_data)
