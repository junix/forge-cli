# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import TypeAlias

from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam

from .computer_tool_param import ComputerToolParam
from .document_finder_tool_param import DocumentFinderToolParam
from .file_search_tool_param import FileSearchToolParam
from .function_tool_param import FunctionToolParam
from .web_search_tool_param import WebSearchToolParam

__all__ = ["ToolParam"]

ToolParam: TypeAlias = FileSearchToolParam | FunctionToolParam | WebSearchToolParam | ComputerToolParam | DocumentFinderToolParam

ParseableToolParam: TypeAlias = ToolParam | ChatCompletionToolParam
