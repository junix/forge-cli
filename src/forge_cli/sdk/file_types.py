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


class DocumentSegment(BaseModel):
    """Represents a document segment/chunk."""
    id: str
    content: str
    index: int
    metadata: dict[str, Any] = Field(default_factory=dict)
    url: str = ""


class DocumentContent(BaseModel):
    """Represents processed document content with segments."""
    id: str
    abstract: str = ""
    summary: str = ""
    outline: str = ""
    keywords: list[str] = Field(default_factory=list)
    language: str = ""
    url: str | None = None
    page_count: int = 0
    file_type: str = ""
    encoding: str | None = None
    status: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    vector_store_ids: list[str] = Field(default_factory=list)
    segments: list[DocumentSegment] = Field(default_factory=list)
    contexts: list[str] = Field(default_factory=list)
    images: list[Any] = Field(default_factory=list)
    graph: Any | None = None


class DocumentResponse(BaseModel):
    """Represents the full document response from the API."""
    id: str
    md5sum: str = ""
    mime_type: str = ""
    content: DocumentContent | None = None
    title: str = ""
    author: str | None = None
    created_at: str | datetime
    updated_at: str | datetime
    read_progress: Any | None = None
    bookmarks: list[Any] = Field(default_factory=list)
    highlights: list[Any] = Field(default_factory=list)
    notes: list[Any] = Field(default_factory=list)
    related_docs: list[Any] = Field(default_factory=list)
    is_favorite: bool = False
    last_read_at: str | None = None
    owner: Any | None = None
    permissions: list[Any] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    vector_store_ids: list[str] = Field(default_factory=list)
    url: str | None = None
    is_delete: bool = False

    @field_validator('created_at', 'updated_at', mode='before')
    @classmethod
    def parse_datetime_fields(cls, v):
        """Parse datetime fields from various formats."""
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                return v
        return v
