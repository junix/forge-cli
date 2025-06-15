# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Literal, Required

from typing_extensions import TypedDict

__all__ = ["ResponseInputFileParam"]


class ResponseInputFileParam(TypedDict, total=False):
    type: Required[Literal["input_file"]]
    """The type of the input item. Always `input_file`."""

    file_data: str
    """The content of the file to be sent to the model."""

    file_id: str | None
    """The ID of the file to be sent to the model."""

    filename: str
    """The name of the file to be sent to the model."""
