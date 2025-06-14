import uuid
from typing import Any, Literal

from constants.metadata_keys import (
    DOC_ID_KEY,
    FILE_ID_KEY,
)
from pydantic import Field, PrivateAttr

from forge_cli.common.logger import logger

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

    def to_chat_tool_call(self) -> "ToolCall":
        """Convert to internal ToolCall type.

        Returns:
            ToolCall: Internal ToolCall object for use throughout Knowledge Forge.
        """
        import json

        # Import ToolCall here to avoid circular imports
        from message._types.tool_call import FunctionCall, ToolCall

        if self._native_tool_call is not None:
            # If we have a native tool call, extract its properties
            native = self._native_tool_call.to_chat_tool_call()
            return ToolCall(
                id=native.id,
                type="function",
                function=FunctionCall(name=native.function.name, arguments=native.function.arguments),
            )

        # Create a JSON string of the arguments
        arguments = json.dumps(
            {
                "doc_ids": self.doc_ids,
                "query": self.query,
            }
        )

        # Generate a fallback ID if no native tool call
        tool_id = f"file_reader_{hash(str(self.doc_ids))}"

        # Create and return internal ToolCall
        return ToolCall(
            id=tool_id,
            type="function",
            function=FunctionCall(name="file_reader", arguments=arguments),
        )

    def as_chat_toolcall_result(self, **kwargs) -> str | list["Chunk"]:
        """Convert the file reader tool call results to either a string or list of Chunks.

        This method is kept for backward compatibility. It delegates to chunkify().

        Args:
            **kwargs: Additional formatting options (currently unused)

        Returns:
            str | List[Chunk]: List of Chunk objects for completed calls with results,
                              or string message for failed/incomplete calls
        """
        return self.chunkify()

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

    def chunkify(self) -> str | list["Chunk"]:
        """Convert this file reader tool call to chunks or return error message.

        This method encapsulates the conversion logic for file reader results.
        Returns a descriptive string if conversion isn't possible, otherwise
        returns a list of Chunk objects for further processing.

        Returns:
            str | List[Chunk]: Error message string if conversion fails,
                             or list of Chunk objects if successful
        """

        # Check status
        if self.status == "incomplete":
            return "File reading incomplete - partial or no results available."

        if self.status != "completed":
            logger.debug(f"ResponseFunctionFileReader.chunkify: Unexpected status '{self.status}'")
            return f"File reading not completed - status: {self.status}"

        # Must have results (chunks) or navigation info that can be converted
        content_chunks = self.results or []

        # Check if we have content chunks with actual content

        chunks = []

        # Process content chunks
        for chunk in content_chunks:
            # Skip chunks without content
            if not hasattr(chunk, "content") or not chunk.content or not chunk.content.strip():
                continue

            # Clone the chunk to avoid modifying the original
            chunk_copy = chunk.model_copy()

            # Ensure metadata exists and add annotation type
            if not chunk_copy.metadata:
                chunk_copy.metadata = {}

            chunk_copy.metadata["annotation_type"] = "file_citation"
            chunk_copy.metadata["source_type"] = "file_reader_call"

            # Ensure doc_id exists for citation creation
            if DOC_ID_KEY not in chunk_copy.metadata:
                chunk_copy.metadata[DOC_ID_KEY] = chunk_copy.metadata.get(FILE_ID_KEY, chunk_copy.id)

            chunks.append(chunk_copy)

        return chunks
