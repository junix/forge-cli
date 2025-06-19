from __future__ import annotations

"""Document core data model for Knowledge Forge CLI.

This module defines the Document class for representing processed documents.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .document_content import DocumentContent


class Document(BaseModel):
    """Processed document with content and metadata.

    Represents a complete document in the Knowledge Forge system,
    including its original metadata and processed content.
    """

    id: str = Field(..., description="Unique document identifier (UUID4)")
    md5sum: str = Field(..., description="MD5 checksum of original content")
    mime_type: str = Field(..., description="MIME type of original file")
    title: str = Field(..., description="Document title")
    author: str | None = Field(None, description="Document author")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")
    url: str | None = Field(None, description="Original URL if applicable")
    metadata: dict[str, Any] | None = Field(default_factory=dict, description="Custom metadata")
    vector_store_ids: list[str] | None = Field(default_factory=list, description="Associated vector store IDs")
    content: DocumentContent | None = Field(None, description="Parsed document content")
