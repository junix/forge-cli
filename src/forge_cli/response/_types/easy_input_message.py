# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from typing import Literal

from ._models import BaseModel
from .response_input_message_content_list import ResponseInputMessageContentList

__all__ = ["EasyInputMessage"]


class EasyInputMessage(BaseModel):
    content: str | ResponseInputMessageContentList
    """
    Text, image, or audio input to the model, used to generate a response. Can also
    contain previous assistant responses.
    """

    role: Literal["user", "assistant", "system", "developer"]
    """The role of the message input.

    One of `user`, `assistant`, `system`, or `developer`.
    """

    type: Literal["message"] | None = None
    """The type of the message input. Always `message`."""
