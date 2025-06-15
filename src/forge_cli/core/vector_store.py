"""VectorStore core data model for Knowledge Forge CLI.

This module defines the VectorStore class for semantic search collections.
"""

from typing import Optional

from pydantic import BaseModel, Field

from .file_count_stats import FileCountStats


class VectorStore(BaseModel):
    """Vector store (collection) for semantic search.
    
    Represents a collection of documents and their embeddings
    that can be searched semantically for retrieval operations.
    """
    
    id: str = Field(
        ...,
        description="Unique vector store identifier"
    )
    object: str = Field(
        default="vector_store",
        description="Object type - always 'vector_store'"
    )
    created_at: int = Field(
        ...,
        description="Creation timestamp (Unix seconds)"
    )
    name: Optional[str] = Field(
        None,
        description="Vector store name"
    )
    description: Optional[str] = Field(
        None,
        description="Vector store description"
    )
    bytes: Optional[int] = Field(
        None,
        description="Total size in bytes",
        ge=0
    )
    file_counts: Optional[FileCountStats] = Field(
        None,
        description="File processing statistics"
    )
    task_id: Optional[str] = Field(
        None,
        description="Associated task ID for creation/modification"
    ) 