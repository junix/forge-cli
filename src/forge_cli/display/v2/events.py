"""Event type definitions for v2 display system."""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict


class EventType(Enum):
    """Standardized event types for display system."""

    # Stream lifecycle
    STREAM_START = "stream_start"
    STREAM_END = "stream_end"
    STREAM_ERROR = "stream_error"

    # Content events
    TEXT_DELTA = "text_delta"
    TEXT_COMPLETE = "text_complete"

    # Tool events
    TOOL_START = "tool_start"
    TOOL_PROGRESS = "tool_progress"
    TOOL_COMPLETE = "tool_complete"
    TOOL_ERROR = "tool_error"

    # Reasoning events
    REASONING_START = "reasoning_start"
    REASONING_DELTA = "reasoning_delta"
    REASONING_COMPLETE = "reasoning_complete"

    # Citation events
    CITATION_FOUND = "citation_found"
    CITATION_TABLE = "citation_table"

    # Message events
    MESSAGE_START = "message_start"
    MESSAGE_COMPLETE = "message_complete"

    @classmethod
    def from_string(cls, value: str) -> "EventType":
        """Convert string to EventType, return None if not found."""
        try:
            return cls(value)
        except ValueError:
            return None


@dataclass
class Event:
    """Standardized event structure."""

    type: EventType
    data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {"type": self.type.value, "data": self.data, "timestamp": self.timestamp}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Create event from dictionary."""
        return cls(
            type=EventType(data["type"]), data=data.get("data", {}), timestamp=data.get("timestamp", time.time())
        )
