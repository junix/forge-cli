# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from typing import Annotated, Literal, TypeAlias

from openai._utils import PropertyInfo

from ._models import BaseModel
from .response_output_refusal import ResponseOutputRefusal
from .response_output_text import ResponseOutputText

__all__ = ["ResponseOutputMessage", "Content"]

Content: TypeAlias = Annotated[ResponseOutputText | ResponseOutputRefusal, PropertyInfo(discriminator="type")]


class ResponseOutputMessage(BaseModel):
    id: str
    """The unique ID of the output message."""

    content: list[Content]
    """The content of the output message."""

    role: Literal["assistant"]
    """The role of the output message. Always `assistant`."""

    status: Literal["in_progress", "completed", "incomplete"]
    """The status of the message input.

    One of `in_progress`, `completed`, or `incomplete`. Populated when input items
    are returned via API.
    """

    type: Literal["message"]
    """The type of the output message. Always `message`."""
