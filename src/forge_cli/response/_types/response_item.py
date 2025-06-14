# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from typing import Annotated, TypeAlias

from openai._utils import PropertyInfo

from .response_computer_tool_call import ResponseComputerToolCall
from .response_computer_tool_call_output_item import ResponseComputerToolCallOutputItem
from .response_file_search_tool_call import ResponseFileSearchToolCall
from .response_function_tool_call_item import ResponseFunctionToolCallItem
from .response_function_tool_call_output_item import ResponseFunctionToolCallOutputItem
from .response_function_web_search import ResponseFunctionWebSearch
from .response_input_message_item import ResponseInputMessageItem
from .response_output_message import ResponseOutputMessage

__all__ = ["ResponseItem"]

ResponseItem: TypeAlias = Annotated[
    ResponseInputMessageItem | ResponseOutputMessage | ResponseFileSearchToolCall | ResponseComputerToolCall | ResponseComputerToolCallOutputItem | ResponseFunctionWebSearch | ResponseFunctionToolCallItem | ResponseFunctionToolCallOutputItem,
    PropertyInfo(discriminator="type"),
]
