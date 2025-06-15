"""Chunk core data model for Knowledge Forge CLI.

This module defines the Chunk class for representing text segments.
"""

import uuid
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """Text chunk with position and metadata.
    
    A chunk represents a segment of text content from a document,
    typically used for vector search and retrieval operations.
    """
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique chunk identifier"
    )
    content: Optional[str] = Field(
        None,
        description="Text content of the chunk"
    )
    index: Optional[int] = Field(
        None,
        description="Position index in document"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Chunk-specific metadata"
    ) 