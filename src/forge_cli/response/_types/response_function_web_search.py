# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Literal, Optional, List

from ._models import BaseModel
from .annotations import AnnotationURLCitation

__all__ = ["ResponseFunctionWebSearch"]


class ResponseFunctionWebSearch(BaseModel):
    id: str
    """The unique ID of the web search tool call."""

    status: Literal["in_progress", "searching", "completed", "failed"]
    """The status of the web search tool call."""

    type: Literal["web_search_call"]
    """The type of the web search tool call. Always `web_search_call`."""

    queries: list[str]
    """The search query used for web search."""

    annotations: Optional[List[AnnotationURLCitation]] = None
    """Annotations field exposing metadata about searched websites (no content)."""
