# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Literal, Required

from typing_extensions import TypedDict

__all__ = ["PageReaderToolParam"]


class PageReaderToolParam(TypedDict, total=False):
    type: Required[Literal["page_reader", "page_reader_preview"]]
    """The type of the page reader tool.

    One of `page_reader` or `page_reader_preview`.
    """
