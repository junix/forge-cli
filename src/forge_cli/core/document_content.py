from __future__ import annotations

"""DocumentContent core data model for Knowledge Forge CLI.

This module defines the DocumentContent class for detailed document content.
"""

from typing import Any

from pydantic import BaseModel, Field

from .chunk import Chunk
from .page import Page


class DocumentContent(BaseModel):
    """Detailed parsed content of a document.

    Contains the processed and structured content of a document,
    including segments, analysis results, and metadata.
    """

    id: str = Field(..., description="Content identifier (MD5 of binary content)")
    abstract: str | None = Field(None, description="Generated abstract")
    summary: str | None = Field(None, description="Generated summary")
    outline: str | None = Field(None, description="Generated outline")
    keywords: list[str] = Field(default_factory=list, description="Extracted keywords")
    language: str | None = Field(None, description="Detected language")
    page_count: int | None = Field(None, description="Number of pages")
    file_type: str | None = Field(None, description="File format type")
    encoding: str | None = Field(None, description="Text encoding")
    metadata: dict[str, Any] | None = Field(default_factory=dict, description="Content-specific metadata")
    segments: list[Page | Chunk] | None = Field(default_factory=list, description="Content segments (pages/chunks)")
