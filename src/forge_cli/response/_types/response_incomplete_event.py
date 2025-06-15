# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Literal

from ._models import BaseModel
from .response import Response

__all__ = ["ResponseIncompleteEvent"]


class ResponseIncompleteEvent(BaseModel):
    response: Response
    """The response that was incomplete."""

    type: Literal["response.incomplete"]
    """The type of the event. Always `response.incomplete`."""
