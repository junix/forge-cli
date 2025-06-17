# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from typing import Literal

from ._models import BaseModel
from .response_input_message_content_list import ResponseInputMessageContentList

__all__ = ["ResponseInputMessageItem"]


class ResponseInputMessageItem(BaseModel):
    id: str
    """The unique ID of the message input."""

    content: ResponseInputMessageContentList
    """
    A list of one or many input items to the model, containing different content
    types.
    """

    role: Literal["user", "system", "developer", "assistant"]
    """The role of the message input. One of `user`, `system`, `developer`, or `assistant`."""

    status: Literal["in_progress", "completed", "incomplete"] | None = None
    """The status of item.

    One of `in_progress`, `completed`, or `incomplete`. Populated when items are
    returned via API.
    """

    type: Literal["message"] | None = None
    """The type of the message input. Always set to `message`."""
