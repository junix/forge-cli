# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from typing import Literal

from ._models import BaseModel

__all__ = ["ResponseReasoningItem", "Summary"]


class Summary(BaseModel):
    text: str
    """
    A short summary of the reasoning used by the model when generating the response.
    """

    type: Literal["summary_text"]
    """The type of the object. Always `summary_text`."""


class ResponseReasoningItem(BaseModel):
    id: str
    """The unique identifier of the reasoning content."""

    summary: list[Summary]
    """Reasoning text contents."""

    type: Literal["reasoning"]
    """The type of the object. Always `reasoning`."""

    encrypted_content: str | None = None
    """
    The encrypted content of the reasoning item - populated when a response is
    generated with `reasoning.encrypted_content` in the `include` parameter.
    """

    status: Literal["in_progress", "completed", "incomplete"] | None = None
    """The status of the item.

    One of `in_progress`, `completed`, or `incomplete`. Populated when items are
    returned via API.
    """
