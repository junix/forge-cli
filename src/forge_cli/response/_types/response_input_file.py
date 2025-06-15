# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from typing import Literal

from ._models import BaseModel

__all__ = ["ResponseInputFile"]


class ResponseInputFile(BaseModel):
    type: Literal["input_file"]
    """The type of the input item. Always `input_file`."""

    file_data: str | None = None
    """The content of the file to be sent to the model."""

    file_id: str | None = None
    """The ID of the file to be sent to the model."""

    filename: str | None = None
    """The name of the file to be sent to the model."""
