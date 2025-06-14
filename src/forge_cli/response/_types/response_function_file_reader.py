import uuid
from typing import Literal

from pydantic import Field

# Removed unused TYPE_CHECKING import
from .traceable_tool import TraceableToolCall


class ResponseFunctionFileReader(TraceableToolCall):
    """Response function for file reader tool calls.

    This class represents a file reader tool call in the LLM response.
    It contains the query to be answered based on document content and
    document IDs to read. Inherits from TraceableToolCall to provide
    execution progress tracking and trace logging.

    Attributes:
        type (str): The type of the function, always "file_reader_call"
        status (Literal): The current status of the file reader call ("in_progress", "searching", "completed", "incomplete")
        doc_ids (List[str]): List of document IDs to be read
        query (str): The query to answer based on the document content
        navigation (str): Browsing history/path as a string
        _results (Optional[List[Chunk]]): The results of the file reading operation
        _native_tool_call (Optional[ResponseFunctionToolCall]): The native tool call
        _navigator (Any): Private temporary navigator object (not serialized)

    Inherited from TraceableToolCall:
        progress (Optional[float]): Reading progress from 0.0 to 1.0
        execution_trace (Optional[str]): Execution history as newline-separated log entries
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str = "file_reader_call"
    status: Literal["in_progress", "searching", "completed", "incomplete"] = "in_progress"
    doc_ids: list[str] = Field(default_factory=list)
    query: str = ""
    navigation: str = Field(default="")
