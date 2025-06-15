"""DocumentContent core data model for Knowledge Forge CLI.

This module defines the DocumentContent class for detailed document content.
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .chunk import Chunk
from .page import Page


class DocumentContent(BaseModel):
    """Detailed parsed content of a document.
    
    Contains the processed and structured content of a document,
    including segments, analysis results, and metadata.
    """
    
    id: str = Field(
        ...,
        description="Content identifier (MD5 of binary content)"
    )
    abstract: Optional[str] = Field(
        None,
        description="Generated abstract"
    )
    summary: Optional[str] = Field(
        None,
        description="Generated summary"
    )
    outline: Optional[str] = Field(
        None,
        description="Generated outline"
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="Extracted keywords"
    )
    language: Optional[str] = Field(
        None,
        description="Detected language"
    )
    page_count: Optional[int] = Field(
        None,
        description="Number of pages"
    )
    file_type: Optional[str] = Field(
        None,
        description="File format type"
    )
    encoding: Optional[str] = Field(
        None,
        description="Text encoding"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Content-specific metadata"
    )
    segments: Optional[List[Union[Page, Chunk]]] = Field(
        default_factory=list,
        description="Content segments (pages/chunks)"
    ) 