"""Task tracking core data models for Knowledge Forge CLI.

This module defines the core data structures for tracking background tasks
and job execution status.
"""

from typing import Any

from pydantic import BaseModel, Field


class Trace(BaseModel):
    """Background task tracking.

    Represents a background task or job that is being executed
    asynchronously, with status and progress information.
    """

    id: str = Field(..., description="Unique task identifier")
    status: str | None = Field(None, description="Task status (pending, in_progress, completed, failed, cancelled)")
    progress: float = Field(default=0.0, description="Completion progress (0.0-1.0)", ge=0.0, le=1.0)
    data: str | int | float | list | dict[str, Any] | None = Field(None, description="Task-specific data")
    failure_reason: str | None = Field(None, description="Failure reason if status is 'failed'")
    created_at: int | None = Field(None, description="Task creation timestamp")
    updated_at: int | None = Field(None, description="Last update timestamp")
