"""Event type definitions for streaming responses."""

from enum import Enum
from typing import TypedDict, Dict, List, Union, Optional


class EventType(Enum):
    """Enumeration of all possible event types."""

    # Response lifecycle
    RESPONSE_CREATED = "response.created"
    RESPONSE_IN_PROGRESS = "response.in_progress"
    RESPONSE_COMPLETED = "response.completed"

    # Output events
    RESPONSE_OUTPUT_ITEM_ADDED = "response.output_item.added"
    RESPONSE_OUTPUT_ITEM_DONE = "response.output_item.done"
    RESPONSE_OUTPUT_TEXT_DELTA = "response.output_text.delta"
    RESPONSE_OUTPUT_TEXT_DONE = "response.output_text.done"

    # Tool-specific events
    FILE_SEARCH_SEARCHING = "response.file_search_call.searching"
    FILE_SEARCH_IN_PROGRESS = "response.file_search_call.in_progress"
    FILE_SEARCH_COMPLETED = "response.file_search_call.completed"

    DOCUMENT_FINDER_SEARCHING = "response.document_finder_call.searching"
    DOCUMENT_FINDER_IN_PROGRESS = "response.document_finder_call.in_progress"
    DOCUMENT_FINDER_COMPLETED = "response.document_finder_call.completed"

    WEB_SEARCH_SEARCHING = "response.web_search_call.searching"
    WEB_SEARCH_IN_PROGRESS = "response.web_search_call.in_progress"
    WEB_SEARCH_COMPLETED = "response.web_search_call.completed"

    FILE_READER_IN_PROGRESS = "response.file_reader_call.in_progress"
    FILE_READER_COMPLETED = "response.file_reader_call.completed"

    # Control events
    ERROR = "error"
    DONE = "done"
    FINAL_RESPONSE = "final_response"

    @classmethod
    def from_string(cls, event_str: str) -> Optional["EventType"]:
        """Convert string to EventType, returns None if not found."""
        for event_type in cls:
            if event_type.value == event_str:
                return event_type
        return None


class StreamEvent(TypedDict):
    """Structure of a streaming event."""

    type: str
    data: Union[Dict[str, Union[str, int, float, bool, List, Dict]], str, int, float, bool]
    usage: Optional[Dict[str, Union[str, int]]]
