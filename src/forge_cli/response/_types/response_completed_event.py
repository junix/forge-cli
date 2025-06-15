# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Literal

from ._models import BaseModel
from .response import Response

__all__ = ["ResponseCompletedEvent"]


class ResponseCompletedEvent(BaseModel):
    response: Response
    """Properties of the completed response."""

    type: Literal["response.completed"]
    """The type of the event. Always `response.completed`."""
