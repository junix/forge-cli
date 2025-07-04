# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal, Required, TypeAlias

from typing_extensions import TypedDict

from .response_output_refusal_param import ResponseOutputRefusalParam
from .response_output_text_param import ResponseOutputTextParam

__all__ = ["ResponseOutputMessageParam", "Content"]

Content: TypeAlias = ResponseOutputTextParam | ResponseOutputRefusalParam


class ResponseOutputMessageParam(TypedDict, total=False):
    id: Required[str]
    """The unique ID of the output message."""

    content: Required[Iterable[Content]]
    """The content of the output message."""

    role: Required[Literal["assistant"]]
    """The role of the output message. Always `assistant`."""

    status: Required[Literal["in_progress", "completed", "incomplete"]]
    """The status of the message input.

    One of `in_progress`, `completed`, or `incomplete`. Populated when input items
    are returned via API.
    """

    type: Required[Literal["message"]]
    """The type of the output message. Always `message`."""
