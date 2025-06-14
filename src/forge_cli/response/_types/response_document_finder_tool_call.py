# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Literal

from ._models import BaseModel

__all__ = ["ResponseDocumentFinderToolCall"]


class ResponseDocumentFinderToolCall(BaseModel):
    id: str
    """The unique ID of the document finder tool call."""

    queries: list[str]
    """The queries used to search for documents."""

    count: int = 10
    """The number of documents to return."""

    status: Literal["in_progress", "searching", "completed", "incomplete"]
    """The status of the document finder tool call.

    One of `in_progress`, `searching`, `completed` or `incomplete`.
    """

    type: Literal["document_finder_call"]
    """The type of the document finder tool call. Always `document_finder_call`."""
