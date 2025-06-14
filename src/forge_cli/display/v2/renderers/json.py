"""JSON renderer - machine-readable output format."""

import json
import sys
import time
from typing import TextIO

from ..base import BaseRenderer
from ..events import Event, EventType


class JsonRenderer(BaseRenderer):
    """JSON output renderer for machine consumption."""

    def __init__(self, file: TextIO | None = None, include_events: bool = False, pretty: bool = True):
        """Initialize JSON renderer.

        Args:
            file: Output file handle (defaults to stdout)
            include_events: Whether to include all events in output
            pretty: Whether to pretty-print JSON
        """
        super().__init__()
        self._file = file or sys.stdout
        self._include_events = include_events
        self._pretty = pretty
        self._start_time = time.time()

        # Track all events if requested
        self._events: list[dict[str, str | int | float | bool | list | dict]] = []

        # Build response state
        self._state = {
            "status": "initialized",
            "query": "",
            "response_text": "",
            "reasoning_text": "",
            "tools": {},
            "citations": [],
            "errors": [],
            "metadata": {"start_time": self._start_time, "model": "", "effort": "", "temperature": 0.0},
        }

    def render_stream_event(self, event_type: str, data: dict[str, str | int | float | bool | list | dict]) -> None:
        """Process and accumulate event data."""
        self._ensure_not_finalized()

        # Record event if requested
        if self._include_events:
            event = Event(type=EventType(event_type), data=data.copy())
            self._events.append(event.to_dict())

        # Update state based on event type
        event_enum = EventType.from_string(event_type)

        if event_enum:
            match event_enum:
                case EventType.STREAM_START:
                    self._handle_stream_start(data)
                case EventType.STREAM_END:
                    self._handle_stream_end(data)
                case EventType.STREAM_ERROR:
                    self._handle_stream_error(data)
                case EventType.TEXT_DELTA:
                    self._handle_text_delta(data)
                case EventType.TEXT_COMPLETE:
                    self._handle_text_complete(data)
                case EventType.REASONING_START:
                    self._handle_reasoning_start(data)
                case EventType.REASONING_DELTA:
                    self._handle_reasoning_delta(data)
                case EventType.REASONING_COMPLETE:
                    self._handle_reasoning_complete(data)
                case EventType.TOOL_START:
                    self._handle_tool_start(data)
                case EventType.TOOL_PROGRESS:
                    self._handle_tool_progress(data)
                case EventType.TOOL_COMPLETE:
                    self._handle_tool_complete(data)
                case EventType.TOOL_ERROR:
                    self._handle_tool_error(data)
                case EventType.CITATION_FOUND:
                    self._handle_citation_found(data)
                case EventType.MESSAGE_START:
                    self._handle_message_start(data)
                case EventType.MESSAGE_COMPLETE:
                    self._handle_message_complete(data)
                case _:
                    # Unknown events are recorded but not processed
                    pass

    def _handle_stream_start(self, data: dict[str, str | int | float | bool | list | dict]) -> None:
        """Handle stream start event."""
        self._state["status"] = "streaming"
        self._state["query"] = data.get("query", "")

        # Update metadata
        metadata = self._state["metadata"]
        metadata["model"] = data.get("model", "")
        metadata["effort"] = data.get("effort", "")
        metadata["temperature"] = data.get("temperature", 0.0)

    def _handle_stream_end(self, data: dict[str, str | int | float | bool | list | dict]) -> None:
        """Handle stream end event."""
        self._state["status"] = "completed"
        self._state["metadata"]["end_time"] = time.time()
        self._state["metadata"]["duration"] = data.get("duration", time.time() - self._start_time)
        self._state["metadata"]["usage"] = data.get("usage", {})
        self._state["metadata"]["response_id"] = data.get("response_id", "")

    def _handle_stream_error(self, data: dict[str, str | int | float | bool | list | dict]) -> None:
        """Handle stream error event."""
        self._state["status"] = "error"
        self._state["errors"].append(
            {"timestamp": data.get("timestamp", time.time()), "error": data.get("error", "Unknown error")}
        )

    def _handle_text_delta(self, data: dict[str, str | int | float | bool | list | dict]) -> None:
        """Handle text delta event - actually a snapshot."""
        text = data.get("text", "")
        # Since this is a snapshot, replace the entire text
        self._state["response_text"] = text

    def _handle_text_complete(self, data: dict[str, str | int | float | bool | list | dict]) -> None:
        """Handle text complete event."""
        # Could store final text if different
        pass

    def _handle_reasoning_start(self, data: dict[str, str | int | float | bool | list | dict]) -> None:
        """Handle reasoning start event."""
        if "reasoning" not in self._state:
            self._state["reasoning"] = {"status": "active", "text": "", "started_at": time.time()}

    def _handle_reasoning_delta(self, data: dict[str, str | int | float | bool | list | dict]) -> None:
        """Handle reasoning delta event - actually a snapshot."""
        text = data.get("text", "")
        if isinstance(self._state.get("reasoning"), dict):
            # Since this is a snapshot, replace the entire text
            self._state["reasoning"]["text"] = text
        else:
            # Legacy compatibility
            self._state["reasoning_text"] = text

    def _handle_reasoning_complete(self, data: dict[str, str | int | float | bool | list | dict]) -> None:
        """Handle reasoning complete event."""
        if isinstance(self._state.get("reasoning"), dict):
            self._state["reasoning"]["status"] = "completed"
            self._state["reasoning"]["completed_at"] = time.time()

    def _handle_tool_start(self, data: dict[str, str | int | float | bool | list | dict]) -> None:
        """Handle tool start event."""
        tool_id = data.get("tool_id", f"tool_{time.time()}")
        self._state["tools"][tool_id] = {
            "type": data.get("tool_type", "unknown"),
            "status": "running",
            "started_at": time.time(),
            "parameters": data.get("parameters", {}),
        }

    def _handle_tool_progress(self, data: dict[str, str | int | float | bool | list | dict]) -> None:
        """Handle tool progress event."""
        tool_id = data.get("tool_id")
        if tool_id and tool_id in self._state["tools"]:
            tool = self._state["tools"][tool_id]
            tool["progress"] = data.get("progress", 0)
            tool["message"] = data.get("message", "")

    def _handle_tool_complete(self, data: dict[str, str | int | float | bool | list | dict]) -> None:
        """Handle tool complete event."""
        tool_id = data.get("tool_id")
        if tool_id and tool_id in self._state["tools"]:
            tool = self._state["tools"][tool_id]
            tool["status"] = "completed"
            tool["completed_at"] = time.time()
            tool["results_count"] = data.get("results_count", 0)
            tool["results"] = data.get("results", [])

    def _handle_tool_error(self, data: dict[str, str | int | float | bool | list | dict]) -> None:
        """Handle tool error event."""
        tool_id = data.get("tool_id")
        if tool_id and tool_id in self._state["tools"]:
            tool = self._state["tools"][tool_id]
            tool["status"] = "error"
            tool["error"] = data.get("error", "Unknown error")

    def _handle_citation_found(self, data: dict[str, str | int | float | bool | list | dict]) -> None:
        """Handle citation found event."""
        citation = {
            "number": data.get("citation_num", len(self._state["citations"]) + 1),
            "type": data.get("citation_type", "unknown"),
            "text": data.get("citation_text", ""),
            "source": data.get("source", ""),
            "metadata": {},
        }

        # Add type-specific metadata
        if "file_id" in data:
            citation["metadata"]["file_id"] = data["file_id"]
        if "file_name" in data:
            citation["metadata"]["file_name"] = data["file_name"]
        if "page_number" in data:
            citation["metadata"]["page_number"] = data["page_number"]
        if "url" in data:
            citation["metadata"]["url"] = data["url"]

        self._state["citations"].append(citation)

    def _handle_message_start(self, data: dict[str, str | int | float | bool | list | dict]) -> None:
        """Handle message start event."""
        self._state["message"] = {
            "status": "active",
            "type": data.get("message_type", "assistant"),
            "started_at": time.time(),
        }

    def _handle_message_complete(self, data: dict[str, str | int | float | bool | list | dict]) -> None:
        """Handle message complete event."""
        if "message" in self._state:
            self._state["message"]["status"] = "completed"
            self._state["message"]["completed_at"] = time.time()

    def finalize(self) -> None:
        """Output final JSON."""
        if not self._finalized:
            # Ensure status is set
            if self._state["status"] == "streaming":
                self._state["status"] = "completed"

            # Calculate final duration if not set
            if "end_time" not in self._state["metadata"]:
                self._state["metadata"]["end_time"] = time.time()
                self._state["metadata"]["duration"] = time.time() - self._start_time

            # Build v1-compatible output structure
            output = {}

            # Add request info
            if self._state["query"]:
                output["request"] = {
                    "question": self._state["query"],
                    "model": self._state["metadata"].get("model", ""),
                    "effort": self._state["metadata"].get("effort", ""),
                }

            # Add response
            output["response"] = {
                "id": self._state["metadata"].get("response_id", ""),
                "model": self._state["metadata"].get("model", ""),
                "content": self._state["response_text"],
                "usage": self._state["metadata"].get("usage", {}),
            }

            # Add error if any
            if self._state["errors"]:
                output["error"] = self._state["errors"][-1]["error"] if self._state["errors"] else None

            # Add citations summary if any
            if self._state["citations"]:
                output["citations_summary"] = {
                    "total_citations": len(self._state["citations"]),
                    "citations": self._state["citations"],
                }

            # Output JSON in v1 format
            json.dump(output, self._file, indent=2, ensure_ascii=False)
            self._file.flush()
            self._finalized = True
