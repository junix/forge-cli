# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union

from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam
from typing_extensions import TypeAlias

from .computer_tool_param import ComputerToolParam
from .document_finder_tool_param import DocumentFinderToolParam
from .file_search_tool_param import FileSearchToolParam
from .function_tool_param import FunctionToolParam
from .web_search_tool_param import WebSearchToolParam

__all__ = ["ToolParam"]

ToolParam: TypeAlias = Union[
    FileSearchToolParam,
    FunctionToolParam,
    WebSearchToolParam,
    ComputerToolParam,
    DocumentFinderToolParam,
]

ParseableToolParam: TypeAlias = Union[ToolParam, ChatCompletionToolParam]
