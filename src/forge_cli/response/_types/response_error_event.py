# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from typing import Literal

from ._models import BaseModel

__all__ = ["ResponseErrorEvent"]


class ResponseErrorEvent(BaseModel):
    code: str | None = None
    """The error code."""

    message: str
    """The error message."""

    param: str | None = None
    """The error parameter."""

    type: Literal["error"]
    """The type of the event. Always `error`."""
