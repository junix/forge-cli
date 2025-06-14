import uuid
from typing import Any, Literal

from pydantic import Field, PrivateAttr


from .chunk import Chunk

# Removed unused TYPE_CHECKING import
from .response_function_tool_call import (
    ResponseFunctionToolCall,
)
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
    _results: list[Chunk] | None = None
    _native_tool_call: ResponseFunctionToolCall | None = None
    _navigator: Any = PrivateAttr(default=None)

    @property
    def results(self) -> list[Chunk]:
        """Get the results of the file reading operation.

        Returns:
            List[Chunk]: List of Chunk objects containing document content
        """
        return self._results if self._results is not None else []

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Override model_dump to customize serialization behavior.

        Returns:
            Dict[str, Any]: A dictionary representation of the model.
        """
        data = super().model_dump(**kwargs)
        # Remove private fields from serialized output
        if "_results" in data:
            del data["_results"]
        if "_native_tool_call" in data:
            del data["_native_tool_call"]
        if "_navigator" in data:
            del data["_navigator"]
        return data

    def detail_description(self, with_arguments: bool = True, **kwargs) -> str:
        """Returns a detailed description of the file reader tool.

        This method provides a comprehensive description that can be used
        in prompts, documentation, or UI elements. The description explains
        the tool's purpose, capabilities, and typical use cases.

        Args:
            with_arguments: If True, includes XML format argument descriptions.
                           If False, returns only the basic description.

        Returns:
            str: A detailed description of the file reader tool's functionality.
                 The description follows the format "TOOL_NAME: Brief explanation
                 of what the tool does and how it can be used."
                 When with_arguments=True, also includes XML argument format.

        Example:
            >>> tool = ResponseFunctionFileReader()
            >>> print(tool.description(with_arguments=False))
            DOCUMENT_READING: Read specific documents in detail
            >>> print(tool.description(with_arguments=True))
            DOCUMENT_READING: Read specific documents in detail

            Arguments:
            <document_ids>
            <id>doc_id_1</id>
            <id>doc_id_2</id>
            </document_ids>
        """
        base_description = "DOCUMENT_READING: Read specific documents in detail"

        if not with_arguments:
            return base_description

        return f"""{base_description}

Arguments:
<document_ids>
<id>doc_id_1</id>
<id>doc_id_2</id>
</document_ids>"""
