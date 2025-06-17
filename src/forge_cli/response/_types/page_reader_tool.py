# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Literal

from ._models import BaseModel

__all__ = ["PageReaderTool"]


class PageReaderTool(BaseModel):
    """Page reader tool definition.

    This class represents a page reader tool configuration that can be
    used in requests to enable page reading capabilities from documents.

    Attributes:
        type (str): The type of the tool, always "page_reader"
    """

    type: Literal["page_reader", "page_reader_preview"] = "page_reader"
