# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from typing import Annotated, TypeAlias

from openai._utils import PropertyInfo

from .response_computer_tool_call import ResponseComputerToolCall
from .response_list_documents_tool_call import ResponseListDocumentsToolCall
from .response_file_search_tool_call import ResponseFileSearchToolCall
from .response_function_file_reader import ResponseFunctionFileReader
from .response_function_tool_call import ResponseFunctionToolCall
from .response_function_web_search import ResponseFunctionWebSearch
from .response_output_message import ResponseOutputMessage
from .response_reasoning_item import ResponseReasoningItem

__all__ = ["ResponseOutputItem"]

ResponseOutputItem: TypeAlias = Annotated[
    ResponseOutputMessage | ResponseFileSearchToolCall | ResponseFunctionToolCall | ResponseFunctionWebSearch | ResponseListDocumentsToolCall | ResponseFunctionFileReader | ResponseComputerToolCall | ResponseReasoningItem,
    PropertyInfo(discriminator="type"),
]
