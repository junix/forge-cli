"""Type guards and utilities for Response types to enable proper type narrowing."""

from typing import Any, TypeGuard

from ._types.annotations import AnnotationFileCitation, AnnotationFilePath, AnnotationURLCitation
from ._types.response_code_interpreter_tool_call import ResponseCodeInterpreterToolCall
from ._types.response_computer_tool_call import ResponseComputerToolCall
from ._types.response_document_finder_tool_call import ResponseDocumentFinderToolCall
from ._types.response_file_search_tool_call import ResponseFileSearchToolCall
from ._types.response_function_file_reader import ResponseFunctionFileReader
from ._types.response_function_tool_call import ResponseFunctionToolCall
from ._types.response_function_web_search import ResponseFunctionWebSearch
from ._types.response_output_item import ResponseOutputItem
from ._types.response_output_message import ResponseOutputMessage
from ._types.response_reasoning_item import ResponseReasoningItem


def is_message_item(item: ResponseOutputItem) -> TypeGuard[ResponseOutputMessage]:
    """Check if output item is a message."""
    return item.type == "message"


def is_reasoning_item(item: ResponseOutputItem) -> TypeGuard[ResponseReasoningItem]:
    """Check if output item is reasoning."""
    return item.type == "reasoning"


def is_file_search_call(item: ResponseOutputItem) -> TypeGuard[ResponseFileSearchToolCall]:
    """Check if output item is a file search tool call."""
    return item.type == "file_search_call"


def is_web_search_call(item: ResponseOutputItem) -> TypeGuard[ResponseFunctionWebSearch]:
    """Check if output item is a web search tool call."""
    return item.type == "web_search_call"


def is_document_finder_call(item: ResponseOutputItem) -> TypeGuard[ResponseDocumentFinderToolCall]:
    """Check if output item is a document finder tool call."""
    return item.type == "document_finder_call"


def is_file_reader_call(item: ResponseOutputItem) -> TypeGuard[ResponseFunctionFileReader]:
    """Check if output item is a file reader tool call."""
    return item.type == "file_reader_call"


def is_computer_tool_call(item: ResponseOutputItem) -> TypeGuard[ResponseComputerToolCall]:
    """Check if output item is a computer tool call."""
    return item.type == "computer_call"


def is_function_call(item: ResponseOutputItem) -> TypeGuard[ResponseFunctionToolCall]:
    """Check if output item is a function call."""
    return item.type == "function_call"


def is_code_interpreter_call(item: ResponseOutputItem) -> TypeGuard[ResponseCodeInterpreterToolCall]:
    """Check if output item is a code interpreter tool call."""
    return item.type == "code_interpreter_call"


def is_file_citation(annotation: Any) -> TypeGuard[AnnotationFileCitation]:
    """Check if annotation is a file citation."""
    return hasattr(annotation, 'type') and annotation.type == "file_citation"


def is_url_citation(annotation: Any) -> TypeGuard[AnnotationURLCitation]:
    """Check if annotation is a URL citation."""
    return hasattr(annotation, 'type') and annotation.type == "url_citation"


def is_file_path(annotation: Any) -> TypeGuard[AnnotationFilePath]:
    """Check if annotation is a file path."""
    return hasattr(annotation, 'type') and annotation.type == "file_path"


def get_tool_queries(tool_item: ResponseOutputItem) -> list[str]:
    """Get queries from a tool item, handling both single query and multiple queries."""
    if is_file_search_call(tool_item):
        return tool_item.queries
    elif is_web_search_call(tool_item):
        return tool_item.queries if tool_item.queries else []
    elif is_document_finder_call(tool_item):
        return tool_item.queries if tool_item.queries else []
    elif is_file_reader_call(tool_item):
        # File reader doesn't have queries, return empty list
        return []
    elif is_computer_tool_call(tool_item):
        # Computer tool doesn't have queries, return empty list
        return []
    elif is_function_call(tool_item):
        # Function call doesn't have queries, return empty list
        return []
    elif is_code_interpreter_call(tool_item):
        # Code interpreter doesn't have queries, return empty list
        return []
    else:
        return []


def get_tool_results(tool_item: ResponseOutputItem) -> list[Any]:
    """Get results from a tool item."""
    if is_file_search_call(tool_item):
        return tool_item.results if tool_item.results else []
    elif is_web_search_call(tool_item):
        return tool_item.results if tool_item.results else []
    elif is_document_finder_call(tool_item):
        return tool_item.results if tool_item.results else []
    elif is_file_reader_call(tool_item):
        return tool_item.results if tool_item.results else []
    elif is_computer_tool_call(tool_item):
        return []  # Computer tool doesn't have results in the same format
    elif is_function_call(tool_item):
        return []  # Function call doesn't have results in the same format
    elif is_code_interpreter_call(tool_item):
        return tool_item.results if tool_item.results else []
    else:
        return []


def get_tool_content(tool_item: ResponseOutputItem) -> str | None:
    """Get content from a tool item."""
    if is_file_reader_call(tool_item):
        return tool_item.content
    elif is_computer_tool_call(tool_item):
        # Computer tool calls don't have a code field, they have action
        return None
    elif is_code_interpreter_call(tool_item):
        return tool_item.code if tool_item.code else None
    elif is_function_call(tool_item):
        return None  # Function calls don't have content
    else:
        return None


def get_tool_output(tool_item: ResponseOutputItem) -> str | None:
    """Get output from a tool item."""
    if is_computer_tool_call(tool_item):
        # Computer tool calls don't have output field in the same way
        return None
    elif is_function_call(tool_item):
        return getattr(tool_item, 'output', None)
    else:
        return None


def get_tool_function_name(tool_item: ResponseOutputItem) -> str | None:
    """Get function name from a function call tool item."""
    if is_function_call(tool_item):
        return tool_item.name
    else:
        return None


def get_tool_arguments(tool_item: ResponseOutputItem) -> str | None:
    """Get arguments from a function call tool item."""
    if is_function_call(tool_item):
        return tool_item.arguments
    else:
        return None


def safe_get_attr(obj: Any, attr: str, default: Any = None) -> Any:
    """Safely get attribute from object, returning default if not present."""
    return getattr(obj, attr, default)


# Content Type Guards (for ResponseOutputMessage.content)


def is_output_text(content: Any) -> bool:
    """Check if content is output text."""
    return hasattr(content, 'type') and content.type == "output_text"


def is_output_refusal(content: Any) -> bool:
    """Check if content is output refusal."""
    return hasattr(content, 'type') and content.type == "refusal"


# Input Content Type Guards (for ResponseInputContent)

from ._types.response_input_text import ResponseInputText
from ._types.response_input_image import ResponseInputImage
from ._types.response_input_file import ResponseInputFile
from ._types.tool import Tool
from ._types.file_search_tool import FileSearchTool
from ._types.web_search_tool import WebSearchTool
from ._types.function_tool import FunctionTool
from ._types.computer_tool import ComputerTool
from ._types.document_finder_tool import DocumentFinderTool
from ._types.file_reader_tool import FileReaderTool

def is_input_text(content: Any) -> TypeGuard[ResponseInputText]:
    """Check if input content is text."""
    return hasattr(content, 'type') and content.type == "input_text"


def is_input_image(content: Any) -> TypeGuard[ResponseInputImage]:
    """Check if input content is image."""
    return hasattr(content, 'type') and content.type == "input_image"


def is_input_file(content: Any) -> TypeGuard[ResponseInputFile]:
    """Check if input content is file."""
    return hasattr(content, 'type') and content.type == "input_file"


# Code Interpreter Type Guards


def is_code_interpreter_logs(result: Any) -> bool:
    """Check if code interpreter result is logs."""
    return hasattr(result, 'type') and result.type == "logs"


def is_code_interpreter_files(result: Any) -> bool:
    """Check if code interpreter result is files."""
    return hasattr(result, 'type') and result.type == "files"


# Computer Tool Output Type Guards


def is_computer_tool_output(item: Any) -> bool:
    """Check if item is computer tool call output."""
    return hasattr(item, 'type') and item.type == "computer_call_output"


# Stream Event Type Guards


def is_response_created_event(event: Any) -> bool:
    """Check if event is response created."""
    return hasattr(event, 'type') and event.type == "response.created"


def is_response_completed_event(event: Any) -> bool:
    """Check if event is response completed."""
    return hasattr(event, 'type') and event.type == "response.completed"


def is_response_failed_event(event: Any) -> bool:
    """Check if event is response failed."""
    return hasattr(event, 'type') and event.type == "response.failed"


def is_text_delta_event(event: Any) -> bool:
    """Check if event is text delta."""
    return hasattr(event, 'type') and event.type == "response.text.delta"


def is_text_done_event(event: Any) -> bool:
    """Check if event is text done."""
    return hasattr(event, 'type') and event.type == "response.text.done"


def is_error_event(event: Any) -> bool:
    """Check if event is error event."""
    return hasattr(event, 'type') and event.type == "error"


# Additional Stream Event Type Guards for Code Interpreter


def is_code_interpreter_call_in_progress_event(event: Any) -> bool:
    """Check if event is code interpreter call in progress."""
    return hasattr(event, 'type') and event.type == "response.code_interpreter_call.in_progress"


def is_code_interpreter_call_interpreting_event(event: Any) -> bool:
    """Check if event is code interpreter call interpreting."""
    return hasattr(event, 'type') and event.type == "response.code_interpreter_call.interpreting"


def is_code_interpreter_call_completed_event(event: Any) -> bool:
    """Check if event is code interpreter call completed."""
    return hasattr(event, 'type') and event.type == "response.code_interpreter_call.completed"


def is_code_interpreter_call_code_delta_event(event: Any) -> bool:
    """Check if event is code interpreter call code delta."""
    return hasattr(event, 'type') and event.type == "response.code_interpreter_call.code.delta"


def is_code_interpreter_call_code_done_event(event: Any) -> bool:
    """Check if event is code interpreter call code done."""
    return hasattr(event, 'type') and event.type == "response.code_interpreter_call.code.done"


# Additional Stream Event Type Guards for File Search


def is_file_search_call_in_progress_event(event: Any) -> bool:
    """Check if event is file search call in progress."""
    return hasattr(event, 'type') and event.type == "response.file_search_call.in_progress"


def is_file_search_call_searching_event(event: Any) -> bool:
    """Check if event is file search call searching."""
    return hasattr(event, 'type') and event.type == "response.file_search_call.searching"


def is_file_search_call_completed_event(event: Any) -> bool:
    """Check if event is file search call completed."""
    return hasattr(event, 'type') and event.type == "response.file_search_call.completed"


# Additional Stream Event Type Guards for Web Search


def is_web_search_call_in_progress_event(event: Any) -> bool:
    """Check if event is web search call in progress."""
    return hasattr(event, 'type') and event.type == "response.web_search_call.in_progress"


def is_web_search_call_searching_event(event: Any) -> bool:
    """Check if event is web search call searching."""
    return hasattr(event, 'type') and event.type == "response.web_search_call.searching"


def is_web_search_call_completed_event(event: Any) -> bool:
    """Check if event is web search call completed."""
    return hasattr(event, 'type') and event.type == "response.web_search_call.completed"


# Additional Stream Event Type Guards for Function Calls


def is_function_call_arguments_delta_event(event: Any) -> bool:
    """Check if event is function call arguments delta."""
    return hasattr(event, 'type') and event.type == "response.function_call.arguments.delta"


def is_function_call_arguments_done_event(event: Any) -> bool:
    """Check if event is function call arguments done."""
    return hasattr(event, 'type') and event.type == "response.function_call.arguments.done"


# Content Part Event Type Guards


def is_content_part_added_event(event: Any) -> bool:
    """Check if event is content part added."""
    return hasattr(event, 'type') and event.type == "response.content_part.added"


def is_content_part_done_event(event: Any) -> bool:
    """Check if event is content part done."""
    return hasattr(event, 'type') and event.type == "response.content_part.done"


# Output Item Event Type Guards


def is_output_item_added_event(event: Any) -> bool:
    """Check if event is output item added."""
    return hasattr(event, 'type') and event.type == "response.output_item.added"


def is_output_item_done_event(event: Any) -> bool:
    """Check if event is output item done."""
    return hasattr(event, 'type') and event.type == "response.output_item.done"


# Reasoning Event Type Guards


def is_reasoning_summary_part_added_event(event: Any) -> bool:
    """Check if event is reasoning summary part added."""
    return hasattr(event, 'type') and event.type == "response.reasoning_summary.part.added"


def is_reasoning_summary_part_done_event(event: Any) -> bool:
    """Check if event is reasoning summary part done."""
    return hasattr(event, 'type') and event.type == "response.reasoning_summary.part.done"


def is_reasoning_summary_text_delta_event(event: Any) -> bool:
    """Check if event is reasoning summary text delta."""
    return hasattr(event, 'type') and event.type == "response.reasoning_summary.text.delta"


def is_reasoning_summary_text_done_event(event: Any) -> bool:
    """Check if event is reasoning summary text done."""
    return hasattr(event, 'type') and event.type == "response.reasoning_summary.text.done"


# Refusal Event Type Guards


def is_refusal_delta_event(event: Any) -> bool:
    """Check if event is refusal delta."""
    return hasattr(event, 'type') and event.type == "response.refusal.delta"


def is_refusal_done_event(event: Any) -> bool:
    """Check if event is refusal done."""
    return hasattr(event, 'type') and event.type == "response.refusal.done"


# Text Annotation Event Type Guards


def is_text_annotation_delta_event(event: Any) -> bool:
    """Check if event is text annotation delta."""
    return hasattr(event, 'type') and event.type == "response.text.annotation.delta"


# Audio Event Type Guards


def is_audio_delta_event(event: Any) -> bool:
    """Check if event is audio delta."""
    return hasattr(event, 'type') and event.type == "response.audio.delta"


def is_audio_done_event(event: Any) -> bool:
    """Check if event is audio done."""
    return hasattr(event, 'type') and event.type == "response.audio.done"


def is_audio_transcript_delta_event(event: Any) -> bool:
    """Check if event is audio transcript delta."""
    return hasattr(event, 'type') and event.type == "response.audio_transcript.delta"


def is_audio_transcript_done_event(event: Any) -> bool:
    """Check if event is audio transcript done."""
    return hasattr(event, 'type') and event.type == "response.audio_transcript.done"


# In Progress Event Type Guards


def is_in_progress_event(event: Any) -> bool:
    """Check if event is in progress."""
    return hasattr(event, 'type') and event.type == "response.in_progress"


def is_incomplete_event(event: Any) -> bool:
    """Check if event is incomplete."""
    return hasattr(event, 'type') and event.type == "response.incomplete"


# Status and Error Type Guards


def is_response_completed_status(status: str) -> bool:
    """Check if response status is completed."""
    return status == "completed"


def is_response_failed_status(status: str) -> bool:
    """Check if response status is failed."""
    return status == "failed"


def is_response_in_progress_status(status: str) -> bool:
    """Check if response status is in progress."""
    return status == "in_progress"


def is_response_incomplete_status(status: str) -> bool:
    """Check if response status is incomplete."""
    return status == "incomplete"


def is_response_error(obj: Any) -> bool:
    """Check if object is a response error."""
    return hasattr(obj, 'code') and hasattr(obj, 'message')


# Additional Utility Functions


def get_content_text(content: Any) -> str | None:
    """Get text from content item."""
    if is_output_text(content):
        return content.text
    elif is_input_text(content):
        return content.text
    else:
        return None


def get_content_refusal(content: Any) -> str | None:
    """Get refusal text from content item."""
    if is_output_refusal(content):
        return content.refusal
    else:
        return None


def get_error_message(error: Any) -> str | None:
    """Get error message from error object."""
    if is_response_error(error):
        return error.message
    else:
        return None


def get_error_code(error: Any) -> str | None:
    """Get error code from error object."""
    if is_response_error(error):
        return error.code
    else:
        return None


def is_tool_call_completed(tool_item: ResponseOutputItem) -> bool:
    """Check if tool call is completed."""
    return hasattr(tool_item, 'status') and tool_item.status == "completed"


def is_tool_call_in_progress(tool_item: ResponseOutputItem) -> bool:
    """Check if tool call is in progress."""
    return hasattr(tool_item, 'status') and tool_item.status == "in_progress"


def is_tool_call_failed(tool_item: ResponseOutputItem) -> bool:
    """Check if tool call failed."""
    return hasattr(tool_item, 'status') and tool_item.status in ["failed", "incomplete"]


def is_tool_call_searching(tool_item: ResponseOutputItem) -> bool:
    """Check if tool call is searching."""
    return hasattr(tool_item, 'status') and tool_item.status == "searching"


def is_tool_call_interpreting(tool_item: ResponseOutputItem) -> bool:
    """Check if tool call is interpreting (for code interpreter)."""
    return hasattr(tool_item, 'status') and tool_item.status == "interpreting"


# Tool Type Validation Guards


def is_any_tool_call(item: ResponseOutputItem) -> bool:
    """Check if output item is any type of tool call."""
    return (
        is_file_search_call(item) or
        is_web_search_call(item) or
        is_document_finder_call(item) or
        is_file_reader_call(item) or
        is_computer_tool_call(item) or
        is_function_call(item) or
        is_code_interpreter_call(item)
    )


# Tool Type Guards (for Tool objects)


def is_file_search_tool(tool: Tool) -> TypeGuard[FileSearchTool]:
    """Check if tool is a file search tool."""
    return tool.type == "file_search"


def is_web_search_tool(tool: Tool) -> TypeGuard[WebSearchTool]:
    """Check if tool is a web search tool."""
    return tool.type in ["web_search", "web_search_preview", "web_search_preview_2025_03_11"]


def is_function_tool(tool: Tool) -> TypeGuard[FunctionTool]:
    """Check if tool is a function tool."""
    return tool.type == "function"


def is_computer_tool(tool: Tool) -> TypeGuard[ComputerTool]:
    """Check if tool is a computer use tool."""
    return tool.type == "computer_use_preview"


def is_document_finder_tool(tool: Tool) -> TypeGuard[DocumentFinderTool]:
    """Check if tool is a document finder tool."""
    return tool.type == "document_finder"


def is_file_reader_tool(tool: Tool) -> TypeGuard[FileReaderTool]:
    """Check if tool is a file reader tool."""
    return tool.type == "file_reader"


def is_search_related_tool_call(item: ResponseOutputItem) -> bool:
    """Check if output item is a search-related tool call."""
    return (
        is_file_search_call(item) or
        is_web_search_call(item) or
        is_document_finder_call(item)
    )


def is_execution_tool_call(item: ResponseOutputItem) -> bool:
    """Check if output item is an execution tool call (computer or code interpreter)."""
    return is_computer_tool_call(item) or is_code_interpreter_call(item)


# Comprehensive Event Type Guard


def get_event_type(event: Any) -> str | None:
    """Get the event type from any event object."""
    return getattr(event, 'type', None)


# Comprehensive Tool Call Information


def get_tool_call_id(tool_item: ResponseOutputItem) -> str | None:
    """Get the ID from any tool call."""
    return getattr(tool_item, 'id', None)


def get_tool_call_status(tool_item: ResponseOutputItem) -> str | None:
    """Get the status from any tool call."""
    return getattr(tool_item, 'status', None)


def get_tool_call_type(tool_item: ResponseOutputItem) -> str | None:
    """Get the type from any tool call."""
    return getattr(tool_item, 'type', None)


# Computer Tool Action Type Guards


def is_computer_action_click(action: Any) -> bool:
    """Check if computer action is a click."""
    return hasattr(action, 'type') and action.type == "click"


def is_computer_action_double_click(action: Any) -> bool:
    """Check if computer action is a double click."""
    return hasattr(action, 'type') and action.type == "double_click"


def is_computer_action_drag(action: Any) -> bool:
    """Check if computer action is a drag."""
    return hasattr(action, 'type') and action.type == "drag"


def is_computer_action_keypress(action: Any) -> bool:
    """Check if computer action is a keypress."""
    return hasattr(action, 'type') and action.type == "keypress"


def is_computer_action_move(action: Any) -> bool:
    """Check if computer action is a move."""
    return hasattr(action, 'type') and action.type == "move"


def is_computer_action_screenshot(action: Any) -> bool:
    """Check if computer action is a screenshot."""
    return hasattr(action, 'type') and action.type == "screenshot"


def is_computer_action_scroll(action: Any) -> bool:
    """Check if computer action is a scroll."""
    return hasattr(action, 'type') and action.type == "scroll"


def is_computer_action_type(action: Any) -> bool:
    """Check if computer action is a type action."""
    return hasattr(action, 'type') and action.type == "type"


def is_computer_action_wait(action: Any) -> bool:
    """Check if computer action is a wait."""
    return hasattr(action, 'type') and action.type == "wait"
