# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Literal

from ._models import BaseModel
from .response import Response

__all__ = ["ResponseCreatedEvent"]


class ResponseCreatedEvent(BaseModel):
    response: Response
    """The response that was created."""

    type: Literal["response.created"]
    """The type of the event. Always `response.created`."""
