# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from typing import Literal

from ._models import BaseModel

__all__ = ["ResponseComputerToolCallOutputScreenshot"]


class ResponseComputerToolCallOutputScreenshot(BaseModel):
    type: Literal["computer_screenshot"]
    """Specifies the event type.

    For a computer screenshot, this property is always set to `computer_screenshot`.
    """

    file_id: str | None = None
    """The identifier of an uploaded file that contains the screenshot."""

    image_url: str | None = None
    """The URL of the screenshot image."""
