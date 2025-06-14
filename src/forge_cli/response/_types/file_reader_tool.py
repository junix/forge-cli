from typing import Literal

from pydantic import BaseModel


class FileReaderTool(BaseModel):
    """Response function for file reader tool calls.

    This class represents a file reader tool call in the LLM response.
    It contains the query to be answered based on document content and
    document IDs to read.

    Attributes:
        type (str): The type of the function, always "file_reader_call"
        status (Literal): The current status of the file reader call ("in_progress", "searching", "completed", "incomplete")
        doc_ids (List[str]): List of document IDs to be read
        query (str): The query to answer based on the document content
        progress (float): Reading progress from 0.0 to 1.0
        navigation (str): Browsing history/path as a string
        _results (Optional[List[Chunk]]): The results of the file reading operation
        _native_tool_call (Optional[ResponseFunctionToolCall]): The native tool call
        _navigator (Any): Private temporary navigator object (not serialized)
    """

    type: Literal["file_reader"] = "file_reader"
