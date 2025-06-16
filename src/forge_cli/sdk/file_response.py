"""FileResponse core data model for Knowledge Forge CLI.

This module defines the FileResponse class for file upload responses.
"""

from pydantic import BaseModel, Field


class FileResponse(BaseModel):
    """Response from file upload.

    Represents the result of a file upload operation,
    including metadata and processing task information.
    """

    id: str = Field(..., description="Unique file identifier")
    object: str = Field(default="file", description="Object type - always 'file'")
    bytes: int = Field(..., description="File size in bytes", ge=0)
    created_at: int = Field(..., description="Upload timestamp (Unix seconds)")
    filename: str = Field(..., description="Original filename")
    purpose: str = Field(..., description="File purpose (e.g., 'qa', 'general')")
    task_id: str = Field(..., description="Background processing task ID")
