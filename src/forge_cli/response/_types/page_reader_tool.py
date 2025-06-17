# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Literal

from ._models import BaseModel

__all__ = ["PageReaderTool"]


class PageReaderTool(BaseModel):
    type: Literal["page_reader"]
    """The type of the page reader tool.

    One of `page_reader` or `page_reader_preview`.
    """
