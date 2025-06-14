"""Chunk type for file search results."""

from typing import Any

from ._models import BaseModel


class Chunk(BaseModel):
    """A chunk of content from a file search result."""

    id: str
    """Unique identifier for the chunk."""

    content: str
    """The text content of the chunk."""

    index: int | None = None
    """The index of the chunk within the document (None for non-citable chunks)."""

    metadata: dict[str, Any]
    """Metadata about the chunk including source information."""
