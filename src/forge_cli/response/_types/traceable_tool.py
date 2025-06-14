"""Base class for tool calls with execution tracing and progress tracking.

This module provides a base class for tool call results that need to track
execution progress and maintain an execution trace log. This is particularly
useful for long-running operations that benefit from streaming updates.
"""

from datetime import datetime

from pydantic import Field

from ._models import BaseModel

__all__ = ["TraceableToolCall"]


class TraceableToolCall(BaseModel):
    """Base class for tool calls that support execution tracing and progress tracking.

    This class provides common functionality for tool calls that need to:
    - Track execution progress (0.0 to 1.0)
    - Maintain an execution trace log
    - Capture streaming execution states

    Tool call classes that represent long-running operations should inherit from
    this class to gain progress tracking and execution logging capabilities.

    Attributes:
        progress: Current execution progress as a float between 0.0 and 1.0.
                 None indicates progress is not being tracked.
        execution_trace: Newline-separated log of execution events with timestamps.
                        Each line follows the format: [HH:MM:SS] message
    """

    progress: float | None = Field(default=None, ge=0.0, le=1.0, description="Current execution progress (0.0-1.0)")

    execution_trace: str | None = Field(default=None, description="Execution history as newline-separated log entries")

    def append_trace(self, message: str, step_name: str | None = None) -> None:
        """Append a message to the execution trace with current timestamp.

        This is a convenience method for adding trace entries without
        creating a full ToolExecutionState object.

        Args:
            message: The message to add to the trace
            step_name: Optional step name to include in the trace entry
        """
        timestamp = datetime.utcnow().strftime("%H:%M:%S")

        if step_name:
            trace_line = f"[{timestamp}] [{step_name}] {message}"
        else:
            trace_line = f"[{timestamp}] {message}"

        if self.execution_trace is None:
            self.execution_trace = trace_line
        else:
            self.execution_trace += f"\n{trace_line}"

    def set_progress(self, progress: float) -> None:
        """Set the execution progress.

        Args:
            progress: Progress value between 0.0 and 1.0

        Raises:
            ValueError: If progress is not between 0.0 and 1.0
        """
        if not 0.0 <= progress <= 1.0:
            raise ValueError(f"Progress must be between 0.0 and 1.0, got {progress}")
        self.progress = progress

    def get_trace_lines(self) -> list[str]:
        """Get the execution trace as a list of lines.

        Returns:
            List of trace lines, or empty list if no trace exists
        """
        if not self.execution_trace:
            return []
        return self.execution_trace.strip().split("\n")

    def clear_trace(self) -> None:
        """Clear the execution trace."""
        self.execution_trace = None
