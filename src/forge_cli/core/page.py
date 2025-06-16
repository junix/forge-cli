"""Page core data model for Knowledge Forge CLI.

This module defines the Page class for representing document pages.
"""

from pydantic import Field

from .chunk import Chunk


class Page(Chunk):
    """Document page (specialized chunk).

    A page represents a single page from a document, extending
    the Chunk model with page-specific attributes.
    """

    url: str = Field(..., description="Page-specific URL or reference")
