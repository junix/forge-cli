# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass
from typing import Literal

from ._models import BaseModel

__all__ = ["ResponseFileSearchToolCall"]


class ResponseFileSearchToolCall(BaseModel):
    id: str
    """The unique ID of the file search tool call."""

    queries: list[str]
    """The queries used to search for files."""

    status: Literal["in_progress", "searching", "completed", "incomplete", "failed"]
    """The status of the file search tool call.

    One of `in_progress`, `searching`, `completed`, `incomplete` or `failed`"""

    type: Literal["file_search_call"]
    """The type of the file search tool call. Always `file_search_call`."""

    file_id: str | None = None
    """The ID of the specific file being searched, if filtered to a single document."""
