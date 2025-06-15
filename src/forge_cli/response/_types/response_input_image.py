# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from typing import Literal

from ._models import BaseModel

__all__ = ["ResponseInputImage"]


class ResponseInputImage(BaseModel):
    detail: Literal["low", "high", "auto"]
    """The detail level of the image to be sent to the model.

    One of `high`, `low`, or `auto`. Defaults to `auto`.
    """

    type: Literal["input_image"]
    """The type of the input item. Always `input_image`."""

    file_id: str | None = None
    """The ID of the file to be sent to the model."""

    image_url: str | None = None
    """The URL of the image to be sent to the model.

    A fully qualified URL or base64 encoded image in a data URL.
    """
