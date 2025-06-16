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
    """Check if the given ResponseOutputItem is a ResponseOutputMessage.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a ResponseOutputMessage, False otherwise.
    """
    return item.type == "message"


def is_reasoning_item(item: ResponseOutputItem) -> TypeGuard[ResponseReasoningItem]:
    """Check if the given ResponseOutputItem is a ResponseReasoningItem.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a ResponseReasoningItem, False otherwise.
    """
    return item.type == "reasoning"


def is_file_search_call(item: ResponseOutputItem) -> TypeGuard[ResponseFileSearchToolCall]:
    """Check if the given ResponseOutputItem is a ResponseFileSearchToolCall.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a ResponseFileSearchToolCall, False otherwise.
    """
    return item.type == "file_search_call"


def is_web_search_call(item: ResponseOutputItem) -> TypeGuard[ResponseFunctionWebSearch]:
    """Check if the given ResponseOutputItem is a ResponseFunctionWebSearch.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a ResponseFunctionWebSearch, False otherwise.
    """
    return item.type == "web_search_call"


def is_document_finder_call(item: ResponseOutputItem) -> TypeGuard[ResponseDocumentFinderToolCall]:
    """Check if the given ResponseOutputItem is a ResponseDocumentFinderToolCall.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a ResponseDocumentFinderToolCall, False otherwise.
    """
    return item.type == "document_finder_call"


def is_file_reader_call(item: ResponseOutputItem) -> TypeGuard[ResponseFunctionFileReader]:
    """Check if the given ResponseOutputItem is a ResponseFunctionFileReader.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a ResponseFunctionFileReader, False otherwise.
    """
    return item.type == "file_reader_call"


def is_computer_tool_call(item: ResponseOutputItem) -> TypeGuard[ResponseComputerToolCall]:
    """Check if the given ResponseOutputItem is a ResponseComputerToolCall.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a ResponseComputerToolCall, False otherwise.
    """
    return item.type == "computer_call"


def is_function_call(item: ResponseOutputItem) -> TypeGuard[ResponseFunctionToolCall]:
    """Check if the given ResponseOutputItem is a ResponseFunctionToolCall.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a ResponseFunctionToolCall, False otherwise.
    """
    return item.type == "function_call"


def is_code_interpreter_call(item: ResponseOutputItem) -> TypeGuard[ResponseCodeInterpreterToolCall]:
    """Check if the given ResponseOutputItem is a ResponseCodeInterpreterToolCall.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a ResponseCodeInterpreterToolCall, False otherwise.
    """
    return item.type == "code_interpreter_call"


def is_file_citation(annotation: Any) -> TypeGuard[AnnotationFileCitation]:
    """Check if the given annotation is an AnnotationFileCitation.

    Args:
        annotation: The annotation object to check.

    Returns:
        True if the annotation is an AnnotationFileCitation, False otherwise.
    """
    return hasattr(annotation, "type") and annotation.type == "file_citation"


def is_url_citation(annotation: Any) -> TypeGuard[AnnotationURLCitation]:
    """Check if the given annotation is an AnnotationURLCitation.

    Args:
        annotation: The annotation object to check.

    Returns:
        True if the annotation is an AnnotationURLCitation, False otherwise.
    """
    return hasattr(annotation, "type") and annotation.type == "url_citation"


def is_file_path(annotation: Any) -> TypeGuard[AnnotationFilePath]:
    """Check if the given annotation is an AnnotationFilePath.

    Args:
        annotation: The annotation object to check.

    Returns:
        True if the annotation is an AnnotationFilePath, False otherwise.
    """
    return hasattr(annotation, "type") and annotation.type == "file_path"


def get_tool_queries(tool_item: ResponseOutputItem) -> list[str]:
    """Extracts search queries from a ResponseOutputItem if it's a tool call that supports queries.

    Handles tool calls like file search, web search, and document finder.
    Returns an empty list if the tool item doesn't have queries (e.g., file reader, computer tool).

    Args:
        tool_item: The ResponseOutputItem to extract queries from.

    Returns:
        A list of query strings, or an empty list if no queries are applicable.
    """
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
    """Extracts results from a ResponseOutputItem if it's a tool call that produces results.

    Handles tool calls like file search, web search, document finder, file reader, and code interpreter.
    Returns an empty list for tool calls that don't have results in this format (e.g., computer tool, function call).

    Args:
        tool_item: The ResponseOutputItem to extract results from.

    Returns:
        A list of results, or an empty list if no results are applicable or available.
    """
    if is_file_search_call(tool_item):
        return []  # File search results are not directly accessible from tool call
    elif is_web_search_call(tool_item):
        return []  # Web search results are not directly accessible from tool call
    elif is_document_finder_call(tool_item):
        return []  # Document finder results are not directly accessible from tool call
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
    """Extracts content (e.g., file content, code) from a ResponseOutputItem.

    Applicable to tool calls like file reader (content) and code interpreter (code).
    Returns None for tool calls that don't have a direct 'content' or 'code' field (e.g., computer tool, function call).

    Args:
        tool_item: The ResponseOutputItem to extract content from.

    Returns:
        The content string if available, otherwise None.
    """
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
    """Extracts the output from a ResponseOutputItem, typically from a function call.

    Primarily used for `ResponseFunctionToolCall` to get its `output` attribute.
    Returns None for other tool types or if the output attribute is not present.

    Args:
        tool_item: The ResponseOutputItem to extract output from.

    Returns:
        The output string if available (for function calls), otherwise None.
    """
    if is_computer_tool_call(tool_item):
        # Computer tool calls don't have output field in the same way
        return None
    elif is_function_call(tool_item):
        return getattr(tool_item, "output", None)
    else:
        return None


def get_tool_function_name(tool_item: ResponseOutputItem) -> str | None:
    """Extracts the function name from a ResponseOutputItem if it's a ResponseFunctionToolCall.

    Args:
        tool_item: The ResponseOutputItem to check.

    Returns:
        The function name string if the item is a function call, otherwise None.
    """
    if is_function_call(tool_item):
        return tool_item.name
    else:
        return None


def get_tool_arguments(tool_item: ResponseOutputItem) -> str | None:
    """Extracts the arguments string from a ResponseOutputItem if it's a ResponseFunctionToolCall.

    Args:
        tool_item: The ResponseOutputItem to check.

    Returns:
        The arguments string if the item is a function call, otherwise None.
    """
    if is_function_call(tool_item):
        return tool_item.arguments
    else:
        return None


def safe_get_attr(obj: Any, attr: str, default: Any = None) -> Any:
    """Safely retrieve an attribute from an object.

    If the attribute does not exist, returns the provided default value.

    Args:
        obj: The object from which to get the attribute.
        attr: The name of the attribute to retrieve.
        default: The value to return if the attribute is not found. Defaults to None.

    Returns:
        The attribute's value or the default value.
    """
    return getattr(obj, attr, default)


# Content Type Guards (for ResponseOutputMessage.content)

from ._types.response_output_refusal import ResponseOutputRefusal
from ._types.response_output_text import ResponseOutputText


def is_output_text(content: Any) -> TypeGuard[ResponseOutputText]:
    """Check if the given content object is a ResponseOutputText.

    This is used to narrow down the type of `ResponseOutputMessage.content`.

    Args:
        content: The content object to check.

    Returns:
        True if the content is ResponseOutputText, False otherwise.
    """
    return hasattr(content, "type") and content.type == "output_text"


def is_output_refusal(content: Any) -> TypeGuard[ResponseOutputRefusal]:
    """Check if the given content object is a ResponseOutputRefusal.

    This is used to narrow down the type of `ResponseOutputMessage.content`.

    Args:
        content: The content object to check.

    Returns:
        True if the content is ResponseOutputRefusal, False otherwise.
    """
    return hasattr(content, "type") and content.type == "refusal"


# Input Content Type Guards (for ResponseInputContent)

from ._types.computer_tool import ComputerTool
from ._types.document_finder_tool import DocumentFinderTool
from ._types.file_reader_tool import FileReaderTool
from ._types.file_search_tool import FileSearchTool
from ._types.function_tool import FunctionTool
from ._types.response_input_file import ResponseInputFile
from ._types.response_input_image import ResponseInputImage
from ._types.response_input_text import ResponseInputText
from ._types.tool import Tool
from ._types.web_search_tool import WebSearchTool


def is_input_text(content: Any) -> TypeGuard[ResponseInputText]:
    """Check if the given input content object is a ResponseInputText.

    This is used to narrow down the type of items in `Response.input.content`.

    Args:
        content: The input content object to check.

    Returns:
        True if the input content is ResponseInputText, False otherwise.
    """
    return hasattr(content, "type") and content.type == "input_text"


def is_input_image(content: Any) -> TypeGuard[ResponseInputImage]:
    """Check if the given input content object is a ResponseInputImage.

    This is used to narrow down the type of items in `Response.input.content`.

    Args:
        content: The input content object to check.

    Returns:
        True if the input content is ResponseInputImage, False otherwise.
    """
    return hasattr(content, "type") and content.type == "input_image"


def is_input_file(content: Any) -> TypeGuard[ResponseInputFile]:
    """Check if the given input content object is a ResponseInputFile.

    This is used to narrow down the type of items in `Response.input.content`.

    Args:
        content: The input content object to check.

    Returns:
        True if the input content is ResponseInputFile, False otherwise.
    """
    return hasattr(content, "type") and content.type == "input_file"


# Code Interpreter Type Guards


def is_code_interpreter_logs(result: Any) -> bool:
    """Check if a result from a Code Interpreter tool call is of type 'logs'.

    Args:
        result: The result item from `ResponseCodeInterpreterToolCall.results`.

    Returns:
        True if the result type is 'logs', False otherwise.
    """
    return hasattr(result, "type") and result.type == "logs"


def is_code_interpreter_files(result: Any) -> bool:
    """Check if a result from a Code Interpreter tool call is of type 'files'.

    Args:
        result: The result item from `ResponseCodeInterpreterToolCall.results`.

    Returns:
        True if the result type is 'files', False otherwise.
    """
    return hasattr(result, "type") and result.type == "files"


# Computer Tool Output Type Guards


def is_computer_tool_output(item: Any) -> bool:
    """Check if an item is a computer tool call output.

    This typically refers to the structured output from a computer interaction.

    Args:
        item: The item to check.

    Returns:
        True if the item's type is 'computer_call_output', False otherwise.
    """
    return hasattr(item, "type") and item.type == "computer_call_output"


# Stream Event Type Guards


def is_response_created_event(event: Any) -> bool:
    """Check if a stream event indicates that a response has been created.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.created', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.created"


def is_response_completed_event(event: Any) -> bool:
    """Check if a stream event indicates that a response has been completed.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.completed', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.completed"


def is_response_failed_event(event: Any) -> bool:
    """Check if a stream event indicates that a response has failed.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.failed', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.failed"


def is_text_delta_event(event: Any) -> bool:
    """Check if a stream event is a text delta, indicating a chunk of text content.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.text.delta', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.text.delta"


def is_text_done_event(event: Any) -> bool:
    """Check if a stream event indicates that text streaming is done.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.text.done', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.text.done"


def is_error_event(event: Any) -> bool:
    """Check if a stream event is an error event.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'error', False otherwise.
    """
    return hasattr(event, "type") and event.type == "error"


# Additional Stream Event Type Guards for Code Interpreter


def is_code_interpreter_call_in_progress_event(event: Any) -> bool:
    """Check if a stream event indicates a code interpreter call is in progress.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.code_interpreter_call.in_progress', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.code_interpreter_call.in_progress"


def is_code_interpreter_call_interpreting_event(event: Any) -> bool:
    """Check if a stream event indicates a code interpreter call is currently interpreting code.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.code_interpreter_call.interpreting', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.code_interpreter_call.interpreting"


def is_code_interpreter_call_completed_event(event: Any) -> bool:
    """Check if a stream event indicates a code interpreter call has completed.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.code_interpreter_call.completed', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.code_interpreter_call.completed"


def is_code_interpreter_call_code_delta_event(event: Any) -> bool:
    """Check if a stream event is a code delta for a code interpreter call.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.code_interpreter_call.code.delta', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.code_interpreter_call.code.delta"


def is_code_interpreter_call_code_done_event(event: Any) -> bool:
    """Check if a stream event indicates that code streaming for a code interpreter call is done.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.code_interpreter_call.code.done', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.code_interpreter_call.code.done"


# Additional Stream Event Type Guards for File Search


def is_file_search_call_in_progress_event(event: Any) -> bool:
    """Check if a stream event indicates a file search call is in progress.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.file_search_call.in_progress', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.file_search_call.in_progress"


def is_file_search_call_searching_event(event: Any) -> bool:
    """Check if a stream event indicates a file search call is currently searching.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.file_search_call.searching', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.file_search_call.searching"


def is_file_search_call_completed_event(event: Any) -> bool:
    """Check if a stream event indicates a file search call has completed.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.file_search_call.completed', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.file_search_call.completed"


# Additional Stream Event Type Guards for Web Search


def is_web_search_call_in_progress_event(event: Any) -> bool:
    """Check if a stream event indicates a web search call is in progress.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.web_search_call.in_progress', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.web_search_call.in_progress"


def is_web_search_call_searching_event(event: Any) -> bool:
    """Check if a stream event indicates a web search call is currently searching.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.web_search_call.searching', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.web_search_call.searching"


def is_web_search_call_completed_event(event: Any) -> bool:
    """Check if a stream event indicates a web search call has completed.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.web_search_call.completed', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.web_search_call.completed"


# Additional Stream Event Type Guards for Function Calls


def is_function_call_arguments_delta_event(event: Any) -> bool:
    """Check if a stream event is an arguments delta for a function call.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.function_call.arguments.delta', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.function_call.arguments.delta"


def is_function_call_arguments_done_event(event: Any) -> bool:
    """Check if a stream event indicates that arguments streaming for a function call is done.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.function_call.arguments.done', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.function_call.arguments.done"


# Content Part Event Type Guards


def is_content_part_added_event(event: Any) -> bool:
    """Check if a stream event indicates a content part has been added.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.content_part.added', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.content_part.added"


def is_content_part_done_event(event: Any) -> bool:
    """Check if a stream event indicates that processing for a content part is done.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.content_part.done', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.content_part.done"


# Output Item Event Type Guards


def is_output_item_added_event(event: Any) -> bool:
    """Check if a stream event indicates an output item has been added.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.output_item.added', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.output_item.added"


def is_output_item_done_event(event: Any) -> bool:
    """Check if a stream event indicates that processing for an output item is done.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.output_item.done', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.output_item.done"


# Reasoning Event Type Guards


def is_reasoning_summary_part_added_event(event: Any) -> bool:
    """Check if a stream event indicates a reasoning summary part has been added.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.reasoning_summary.part.added', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.reasoning_summary.part.added"


def is_reasoning_summary_part_done_event(event: Any) -> bool:
    """Check if a stream event indicates that processing for a reasoning summary part is done.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.reasoning_summary.part.done', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.reasoning_summary.part.done"


def is_reasoning_summary_text_delta_event(event: Any) -> bool:
    """Check if a stream event is a text delta for a reasoning summary.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.reasoning_summary.text.delta', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.reasoning_summary.text.delta"


def is_reasoning_summary_text_done_event(event: Any) -> bool:
    """Check if a stream event indicates that text streaming for a reasoning summary is done.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.reasoning_summary.text.done', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.reasoning_summary.text.done"


# Refusal Event Type Guards


def is_refusal_delta_event(event: Any) -> bool:
    """Check if a stream event is a refusal delta, indicating a chunk of refusal message content.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.refusal.delta', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.refusal.delta"


def is_refusal_done_event(event: Any) -> bool:
    """Check if a stream event indicates that refusal message streaming is done.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.refusal.done', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.refusal.done"


# Text Annotation Event Type Guards


def is_text_annotation_delta_event(event: Any) -> bool:
    """Check if a stream event is a text annotation delta.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.text.annotation.delta', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.text.annotation.delta"


# Audio Event Type Guards


def is_audio_delta_event(event: Any) -> bool:
    """Check if a stream event is an audio delta, indicating a chunk of audio data.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.audio.delta', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.audio.delta"


def is_audio_done_event(event: Any) -> bool:
    """Check if a stream event indicates that audio streaming is done.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.audio.done', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.audio.done"


def is_audio_transcript_delta_event(event: Any) -> bool:
    """Check if a stream event is an audio transcript delta.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.audio.transcript.delta', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.audio_transcript.delta"


def is_audio_transcript_done_event(event: Any) -> bool:
    """Check if a stream event indicates that audio transcript streaming is done.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.audio.transcript.done', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.audio_transcript.done"


# In Progress Event Type Guards


def is_in_progress_event(event: Any) -> bool:
    """Check if a stream event indicates that the overall response generation is in progress.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.in_progress', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.in_progress"


def is_incomplete_event(event: Any) -> bool:
    """Check if a stream event indicates that the response is incomplete.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.incomplete', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.incomplete"


# Status and Error Type Guards


def is_response_completed_status(status: str) -> bool:
    """Check if a response status string indicates 'completed'.

    Args:
        status: The response status string.

    Returns:
        True if the status is 'completed', False otherwise.
    """
    return status == "completed"


def is_response_failed_status(status: str) -> bool:
    """Check if a response status string indicates 'failed'.

    Args:
        status: The response status string.

    Returns:
        True if the status is 'failed', False otherwise.
    """
    return status == "failed"


def is_response_in_progress_status(status: str) -> bool:
    """Check if a response status string indicates 'in_progress'.

    Args:
        status: The response status string.

    Returns:
        True if the status is 'in_progress', False otherwise.
    """
    return status == "in_progress"


def is_response_incomplete_status(status: str) -> bool:
    """Check if a response status string indicates 'incomplete'.

    Args:
        status: The response status string.

    Returns:
        True if the status is 'incomplete', False otherwise.
    """
    return status == "incomplete"


def is_response_error(obj: Any) -> bool:
    """Check if an object represents a response error structure.

    This typically checks for the presence of 'type' and 'error' attributes.

    Args:
        obj: The object to check.

    Returns:
        True if the object appears to be a response error, False otherwise.
    """
    return hasattr(obj, "code") and hasattr(obj, "message")


# Additional Utility Functions


def get_content_text(content: Any) -> str | None:
    """Extracts the text value from a content item if it's a ResponseOutputText.

    Args:
        content: The content item, expected to be of a type with a 'text' attribute
                 if it's an output text item (e.g., ResponseOutputText).

    Returns:
        The text string if the content is ResponseOutputText and has a text value,
        otherwise None.
    """
    if is_output_text(content):
        return content.text
    elif is_input_text(content):
        return content.text
    else:
        return None


def is_dict_with_type(obj: Any, type_value: str) -> bool:
    """Check if an object is a dictionary and has a 'type' key with a specific value.

    Args:
        obj: The object to check.
        type_value: The expected value for the 'type' key.

    Returns:
        True if obj is a dict and obj.get('type') == type_value, False otherwise.
    """
    return isinstance(obj, dict) and obj.get("type") == type_value


def is_assistant_message_dict(obj: Any) -> bool:
    """Check if an object is a dictionary representing an assistant message.

    This specifically checks if it's a dict with 'role': 'assistant'.

    Args:
        obj: The object to check.

    Returns:
        True if obj is a dict with obj.get('role') == 'assistant', False otherwise.
    """
    return isinstance(obj, dict) and obj.get("type") == "message" and obj.get("role") == "assistant"


def get_content_refusal(content: Any) -> str | None:
    """Extracts the refusal message from a content item if it's a ResponseOutputRefusal.

    Args:
        content: The content item, expected to be ResponseOutputRefusal.

    Returns:
        The refusal message string if the content is ResponseOutputRefusal,
        otherwise None.
    """
    if is_output_refusal(content):
        return content.refusal
    else:
        return None


def get_error_message(error: Any) -> str | None:
    """Safely extracts the error message string from an error object.

    Assumes the error object might have a 'message' attribute.

    Args:
        error: The error object.

    Returns:
        The error message string if present, otherwise None.
    """
    if is_response_error(error):
        return error.message
    else:
        return None


def get_error_code(error: Any) -> str | None:
    """Safely extracts the error code from an error object.

    Assumes the error object might have a 'code' attribute.

    Args:
        error: The error object.

    Returns:
        The error code string if present, otherwise None.
    """
    if is_response_error(error):
        return error.code
    else:
        return None


def is_tool_call_completed(tool_item: ResponseOutputItem) -> bool:
    """Check if the status of a tool call item indicates it has completed.

    Args:
        tool_item: The ResponseOutputItem representing a tool call.

    Returns:
        True if the tool call's status is 'completed', False otherwise.
    """
    return hasattr(tool_item, "status") and tool_item.status == "completed"


def is_tool_call_in_progress(tool_item: ResponseOutputItem) -> bool:
    """Check if the status of a tool call item indicates it is in progress.

    Args:
        tool_item: The ResponseOutputItem representing a tool call.

    Returns:
        True if the tool call's status is 'in_progress', False otherwise.
    """
    return hasattr(tool_item, "status") and tool_item.status == "in_progress"


def is_tool_call_failed(tool_item: ResponseOutputItem) -> bool:
    """Check if the status of a tool call item indicates it has failed.

    Args:
        tool_item: The ResponseOutputItem representing a tool call.

    Returns:
        True if the tool call's status is 'failed', False otherwise.
    """
    return hasattr(tool_item, "status") and tool_item.status in ["failed", "incomplete"]


def is_tool_call_searching(tool_item: ResponseOutputItem) -> bool:
    """Check if the status of a tool call item indicates it is currently searching.

    Applicable to search-related tools like file search, web search, document finder.

    Args:
        tool_item: The ResponseOutputItem representing a tool call.

    Returns:
        True if the tool call's status is 'searching', False otherwise.
    """
    return hasattr(tool_item, "status") and tool_item.status == "searching"


def is_tool_call_interpreting(tool_item: ResponseOutputItem) -> bool:
    """Check if the status of a tool call item indicates it is interpreting code.

    Specifically for Code Interpreter tool calls.

    Args:
        tool_item: The ResponseOutputItem representing a tool call.

    Returns:
        True if the tool call's status is 'interpreting', False otherwise.
    """
    return hasattr(tool_item, "status") and tool_item.status == "interpreting"


# Tool Type Validation Guards


def is_any_tool_call(item: ResponseOutputItem) -> bool:
    """Check if a ResponseOutputItem is any known type of tool call.

    This includes file search, web search, document finder, file reader,
    computer tool, function call, and code interpreter calls.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is one of the recognized tool call types, False otherwise.
    """
    return (
        is_file_search_call(item)
        or is_web_search_call(item)
        or is_document_finder_call(item)
        or is_file_reader_call(item)
        or is_computer_tool_call(item)
        or is_function_call(item)
        or is_code_interpreter_call(item)
    )


# Tool Type Guards (for Tool objects)


def is_file_search_tool(tool: Tool) -> TypeGuard[FileSearchTool]:
    """Check if the given Tool object is a FileSearchTool.

    Args:
        tool: The Tool object to check.

    Returns:
        True if the tool is a FileSearchTool, False otherwise.
    """
    return tool.type == "file_search"


def is_web_search_tool(tool: Tool) -> TypeGuard[WebSearchTool]:
    """Check if the given Tool object is a WebSearchTool.

    Args:
        tool: The Tool object to check.

    Returns:
        True if the tool is a WebSearchTool, False otherwise.
    """
    return tool.type in ["web_search", "web_search_preview", "web_search_preview_2025_03_11"]


def is_function_tool(tool: Tool) -> TypeGuard[FunctionTool]:
    """Check if the given Tool object is a FunctionTool.

    Args:
        tool: The Tool object to check.

    Returns:
        True if the tool is a FunctionTool, False otherwise.
    """
    return tool.type == "function"


def is_computer_tool(tool: Tool) -> TypeGuard[ComputerTool]:
    """Check if the given Tool object is a ComputerTool.

    Args:
        tool: The Tool object to check.

    Returns:
        True if the tool is a ComputerTool, False otherwise.
    """
    return tool.type == "computer_use_preview"


def is_document_finder_tool(tool: Tool) -> TypeGuard[DocumentFinderTool]:
    """Check if the given Tool object is a DocumentFinderTool.

    Args:
        tool: The Tool object to check.

    Returns:
        True if the tool is a DocumentFinderTool, False otherwise.
    """
    return tool.type == "document_finder"


def is_file_reader_tool(tool: Tool) -> TypeGuard[FileReaderTool]:
    """Check if the given Tool object is a FileReaderTool.

    Args:
        tool: The Tool object to check.

    Returns:
        True if the tool is a FileReaderTool, False otherwise.
    """
    return tool.type == "file_reader"


def is_search_related_tool_call(item: ResponseOutputItem) -> bool:
    """Check if a ResponseOutputItem is a search-related tool call.

    This includes file search, web search, and document finder calls.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a file search, web search, or document finder call, False otherwise.
    """
    return is_file_search_call(item) or is_web_search_call(item) or is_document_finder_call(item)


def is_execution_tool_call(item: ResponseOutputItem) -> bool:
    """Check if a ResponseOutputItem is an execution-related tool call.

    This includes computer tool calls and code interpreter calls.

    Args:
        item: The ResponseOutputItem to check.

    Returns:
        True if the item is a computer tool call or code interpreter call, False otherwise.
    """
    return is_computer_tool_call(item) or is_code_interpreter_call(item)


# Comprehensive Event Type Guard


def get_event_type(event: Any) -> str | None:
    """Safely retrieves the 'type' attribute from an event object.

    Args:
        event: The event object.

    Returns:
        The event type string if present and is a string, otherwise None.
    """
    return getattr(event, "type", None)


# Comprehensive Tool Call Information


def get_tool_call_id(tool_item: ResponseOutputItem) -> str | None:
    """Safely retrieves the 'id' attribute from a tool call item.

    Args:
        tool_item: The ResponseOutputItem representing a tool call.

    Returns:
        The tool call ID string if present and is a string, otherwise None.
    """
    return getattr(tool_item, "id", None)


def get_tool_call_status(tool_item: ResponseOutputItem) -> str | None:
    """Safely retrieves the 'status' attribute from a tool call item.

    Args:
        tool_item: The ResponseOutputItem representing a tool call.

    Returns:
        The tool call status string if present and is a string, otherwise None.
    """
    return getattr(tool_item, "status", None)


def get_tool_call_type(tool_item: ResponseOutputItem) -> str | None:
    """Safely retrieves the 'type' attribute from a tool call item.

    Args:
        tool_item: The ResponseOutputItem representing a tool call.

    Returns:
        The tool call type string if present and is a string, otherwise None.
    """
    return getattr(tool_item, "type", None)


# Computer Tool Action Type Guards


def is_computer_action_click(action: Any) -> bool:
    """Check if a computer tool action is a 'click' action.

    Args:
        action: The computer tool action object.

    Returns:
        True if the action type is 'click', False otherwise.
    """
    return hasattr(action, "type") and action.type == "click"


def is_computer_action_double_click(action: Any) -> bool:
    """Check if a computer tool action is a 'double_click' action.

    Args:
        action: The computer tool action object.

    Returns:
        True if the action type is 'double_click', False otherwise.
    """
    return hasattr(action, "type") and action.type == "double_click"


def is_computer_action_drag(action: Any) -> bool:
    """Check if a computer tool action is a 'drag' action.

    Args:
        action: The computer tool action object.

    Returns:
        True if the action type is 'drag', False otherwise.
    """
    return hasattr(action, "type") and action.type == "drag"


def is_computer_action_keypress(action: Any) -> bool:
    """Check if a computer tool action is a 'keypress' action.

    Args:
        action: The computer tool action object.

    Returns:
        True if the action type is 'keypress', False otherwise.
    """
    return hasattr(action, "type") and action.type == "keypress"


def is_computer_action_move(action: Any) -> bool:
    """Check if a computer tool action is a 'move' action.

    Args:
        action: The computer tool action object.

    Returns:
        True if the action type is 'move', False otherwise.
    """
    return hasattr(action, "type") and action.type == "move"


def is_computer_action_screenshot(action: Any) -> bool:
    """Check if a computer tool action is a 'screenshot' action.

    Args:
        action: The computer tool action object.

    Returns:
        True if the action type is 'screenshot', False otherwise.
    """
    return hasattr(action, "type") and action.type == "screenshot"


def is_computer_action_scroll(action: Any) -> bool:
    """Check if a computer tool action is a 'scroll' action.

    Args:
        action: The computer tool action object.

    Returns:
        True if the action type is 'scroll', False otherwise.
    """
    return hasattr(action, "type") and action.type == "scroll"


def is_computer_action_type(action: Any) -> bool:
    """Check if a computer tool action is a 'type' (text input) action.

    Args:
        action: The computer tool action object.

    Returns:
        True if the action type is 'type', False otherwise.
    """
    return hasattr(action, "type") and action.type == "type"


def is_computer_action_wait(action: Any) -> bool:
    """Check if a computer tool action is a 'wait' action.

    Args:
        action: The computer tool action object.

    Returns:
        True if the action type is 'wait', False otherwise.
    """
    return hasattr(action, "type") and action.type == "wait"
