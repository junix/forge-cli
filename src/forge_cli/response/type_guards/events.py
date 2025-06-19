from __future__ import annotations

"""Type guards for stream events."""

from typing import Any


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


def is_text_annotation_delta_event(event: Any) -> bool:
    """Check if a stream event is a text annotation delta.

    Args:
        event: The stream event object.

    Returns:
        True if the event type is 'response.text.annotation.delta', False otherwise.
    """
    return hasattr(event, "type") and event.type == "response.text.annotation.delta"


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


def get_event_type(event: Any) -> str | None:
    """Safely retrieves the 'type' attribute from an event object.

    Args:
        event: The event object.

    Returns:
        The event type string if present and is a string, otherwise None.
    """
    return getattr(event, "type", None)
