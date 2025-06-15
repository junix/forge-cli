# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Literal

from ._models import BaseModel
from .response import Response

__all__ = ["ResponseFailedEvent"]


class ResponseFailedEvent(BaseModel):
    response: Response
    """The response that failed."""

    type: Literal["response.failed"]
    """The type of the event. Always `response.failed`."""
