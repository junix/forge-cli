# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Literal, Required

from typing_extensions import TypedDict

__all__ = ["ResponseInputTextParam"]


class ResponseInputTextParam(TypedDict, total=False):
    text: Required[str]
    """The text input to the model."""

    type: Required[Literal["input_text"]]
    """The type of the input item. Always `input_text`."""
