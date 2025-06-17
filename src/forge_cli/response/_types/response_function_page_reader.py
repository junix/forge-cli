import uuid
from typing import Literal

from pydantic import Field

from .traceable_tool import TraceableToolCall


class ResponseFunctionPageReader(TraceableToolCall):
    """Response function for page reader tool calls.

    This class represents a page reader tool call in the LLM response.
    It contains the document ID and page range to read from a specific document.
    Inherits from TraceableToolCall to provide execution progress tracking and trace logging.

    Attributes:
        type (str): The type of the function, always "page_reader_call"
        status (Literal): The current status of the page reader call ("in_progress", "searching", "completed", "incomplete")
        document_id (str): Document ID to read pages from
        start_page (int): Starting page number (0-indexed)
        end_page (Optional[int]): Ending page number (0-indexed, defaults to start_page)

    Inherited from TraceableToolCall:
        progress (Optional[float]): Reading progress from 0.0 to 1.0
        execution_trace (Optional[str]): Execution history as newline-separated log entries

    Note: Results are accessed through separate mechanisms, not directly from this object.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str = "page_reader_call"
    status: Literal["in_progress", "searching", "completed", "incomplete"] = "in_progress"
    document_id: str = ""
    start_page: int = 0
    end_page: int | None = None
