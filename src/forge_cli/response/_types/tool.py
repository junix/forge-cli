# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from typing import Annotated, TypeAlias

from openai._utils import PropertyInfo

from .computer_tool import ComputerTool
from .file_reader_tool import FileReaderTool
from .file_search_tool import FileSearchTool
from .function_tool import FunctionTool
from .list_documents_tool import ListDocumentsTool
from .web_search_tool import WebSearchTool

__all__ = ["Tool"]

Tool: TypeAlias = Annotated[
    FileSearchTool | FunctionTool | WebSearchTool | ComputerTool | ListDocumentsTool | FileReaderTool,
    PropertyInfo(discriminator="type"),
]
