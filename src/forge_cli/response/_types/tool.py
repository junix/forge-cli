# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from openai._utils import PropertyInfo

from .file_reader_tool import FileReaderTool
from .computer_tool import ComputerTool
from .document_finder_tool import DocumentFinderTool
from .function_tool import FunctionTool
from .web_search_tool import WebSearchTool
from .file_search_tool import FileSearchTool

__all__ = ["Tool"]

Tool: TypeAlias = Annotated[
    Union[FileSearchTool, FunctionTool, WebSearchTool, ComputerTool, DocumentFinderTool, FileReaderTool],
    PropertyInfo(discriminator="type"),
]
