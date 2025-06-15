# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Literal, Required

from typing_extensions import TypedDict

__all__ = ["ResponseOutputRefusalParam"]


class ResponseOutputRefusalParam(TypedDict, total=False):
    refusal: Required[str]
    """The refusal explanationfrom the model."""

    type: Required[Literal["refusal"]]
    """The type of the refusal. Always `refusal`."""
