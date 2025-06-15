from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class TaskStatus(BaseModel):
    """
    Represents the status and details of an asynchronous task.
    """

    id: str = Field(description="The unique identifier for the task.")
    object_field: str = Field(default="task", alias="object", description="The type of object, typically 'task'.")
    type: str = Field(
        description="The type of operation the task is performing (e.g., 'file_processing', 'vector_store_creation')."
    )
    status: Literal["pending", "in_progress", "completed", "failed", "cancelled"] = Field(
        description="The current status of the task."
    )

    created_at: datetime = Field(description="Timestamp when the task was created.")
    updated_at: datetime = Field(description="Timestamp when the task was last updated.")

    progress: float | None = Field(None, description="Task completion progress (e.g., percentage).", ge=0, le=100)
    result: dict[str, Any] | None = Field(
        None, description="The result of the task if completed successfully. Structure may vary based on task type."
    )
    error_message: str | None = Field(None, description="Error message if the task failed.")

    # Optional field to link back to the resource that initiated or is related to this task
    resource_id: str | None = Field(
        None,
        description="Identifier of the primary resource associated with this task (e.g., file_id, vector_store_id).",
    )

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
