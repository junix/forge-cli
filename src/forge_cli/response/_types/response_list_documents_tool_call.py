# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Literal

from ._models import BaseModel

__all__ = ["ResponseListDocumentsToolCall"]


class ResponseListDocumentsToolCall(BaseModel):
    id: str
    """The unique ID of the list documents tool call."""

    queries: list[str]
    """The queries used to search for documents."""

    count: int = 10
    """The number of documents to return."""

    status: Literal["in_progress", "searching", "completed", "incomplete"]
    """The status of the list documents tool call.

    One of `in_progress`, `searching`, `completed` or `incomplete`.
    """

    type: Literal["list_documents_call"]
    """The type of the list documents tool call. Always `list_documents_call`."""
