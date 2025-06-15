# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Literal, Required

from typing_extensions import TypedDict

__all__ = ["ToolChoiceFunctionParam"]


class ToolChoiceFunctionParam(TypedDict, total=False):
    name: Required[str]
    """The name of the function to call."""

    type: Required[Literal["function"]]
    """For function calling, the type is always `function`."""
