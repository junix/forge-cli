from datetime import datetime
from typing import Any, Optional # Added Optional

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
    status: str # e.g., "active", "creating", "failed"
    created_at: datetime
    updated_at: datetime
    bytes: int | None = None
    file_counts: FileCounts
    task_id: str | None = None # ID of the task that created/updated this vector store
    last_task_status: str | None = None # Status of the last task related to this vector store
    last_processed_at: datetime | None = None

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class VectorStoreSummary(BaseModel): # Renamed from VectorStoreSummaryResponse for brevity, as it's the content itself
    """
    Represents the summary of a vector store.
    """
    vector_store_id: str = Field(description="Identifier of the vector store being summarized.")
    summary_text: str = Field(description="The generated summary text.")
    model_used: str = Field(description="The model used to generate the summary.")
    created_at: datetime = Field(description="Timestamp when the summary was generated.")

    # Optional fields
    token_count: Optional[int] = Field(None, description="Number of tokens in the summary text.")
    duration_ms: Optional[float] = Field(None, description="Time taken to generate the summary in milliseconds.")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Example Usage (for illustration):
# summary_data = {
#     "vector_store_id": "vs_123",
#     "summary_text": "This vector store contains documents about AI and machine learning...",
#     "model_used": "qwen-max",
#     "created_at": "2023-10-27T10:00:00Z",
#     "token_count": 75
# }
# vs_summary = VectorStoreSummary(**summary_data)
