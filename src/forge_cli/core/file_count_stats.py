from __future__ import annotations

"""FileCountStats core data model for Knowledge Forge CLI.

This module defines the FileCountStats class for tracking file processing statistics.
"""

from pydantic import BaseModel, Field


class FileCountStats(BaseModel):
    """File processing statistics.

    Tracks the status of files within a vector store,
    including processing progress and completion status.
    """

    in_progress: int = Field(default=0, description="Files being processed", ge=0)
    completed: int = Field(default=0, description="Successfully processed files", ge=0)
    failed: int = Field(default=0, description="Failed processing files", ge=0)
    cancelled: int = Field(default=0, description="Cancelled processing files", ge=0)
    total: int = Field(default=0, description="Total files in vector store", ge=0)
