# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .annotations import AnnotationFileCitation
from pydantic import PrivateAttr, Field
from typing_extensions import Literal

from ._models import BaseModel
from .response_function_tool_call import ResponseFunctionToolCall
from .chunk import Chunk

__all__ = ["ResponseFileSearchToolCall", "ResponseFileSearchToolCallResult"]


class ResponseFileSearchToolCallResult(BaseModel):
    attributes: Optional[Dict[str, Union[str, float, bool, int]]] = None
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format, and querying for objects via API or the dashboard. Keys are
    strings with a maximum length of 64 characters. Values are strings with a
    maximum length of 512 characters, booleans, or numbers.
    """

    file_id: Optional[str] = None
    """The unique ID of the file."""

    filename: Optional[str] = None
    """The name of the file."""

    score: Optional[float] = None
    """The relevance score of the file - a value between 0 and 1."""

    text: Optional[str] = None
    """The text that was retrieved from the file."""

    @property
    def citation_id(self) -> Optional[Union[int, str]]:
        """The citation sequence number for this result."""
        if self.attributes is None:
            return None
        return self.attributes.get("citation_id")

    @citation_id.setter
    def citation_id(self, value: Union[int, str]) -> None:
        """Set the citation sequence number for this result."""
        if self.attributes is None:
            self.attributes = {}
        self.attributes["citation_id"] = value

    def set_citation_id(self, citation_id: Union[int, str]) -> None:
        """Set the citation sequence number for this result (method interface)."""
        self.citation_id = citation_id

    def is_citable(self) -> bool:
        """Check if the file search result is citable.

        A file search result is citable if it has a valid segment_index in its attributes,
        indicating it represents a specific, locatable segment within a document.

        Returns:
            bool: True if the result has a valid segment_index (integer >= 0), False otherwise.
        """
        from forge_cli.constants.metadata_keys import SEGMENT_INDEX_KEY
        
        # Must have attributes
        if not self.attributes:
            return False
            
        # Must have segment_index key
        if SEGMENT_INDEX_KEY not in self.attributes:
            return False
            
        segment_index = self.attributes[SEGMENT_INDEX_KEY]
        
        # Check if segment_index is a valid integer >= 0
        if isinstance(segment_index, int):
            return segment_index >= 0
        elif isinstance(segment_index, str) and segment_index.isdigit():
            return int(segment_index) >= 0
        elif isinstance(segment_index, float) and segment_index.is_integer():
            return int(segment_index) >= 0
        
        # Invalid segment_index type or value
        return False


    def as_annotation(self) -> Optional["AnnotationFileCitation"]:
        """Convert this file search result to an annotation using document segment index.
        
        Uses the segment_index from attributes (document position), not citation_id.
        This is for document-based annotations that reference the actual position
        within the source document.

        Returns:
            AnnotationFileCitation if this result has sufficient data and is citable,
            None if missing required fields (file_id, text) or not citable
        """
        # Import here to avoid circular imports
        from .annotations import AnnotationFileCitation
        from forge_cli.constants.metadata_keys import SEGMENT_INDEX_KEY

        # Validate required fields
        if not self.file_id or not self.text:
            return None

        # Use is_citable() to check if this result can be used for annotations
        if not self.is_citable():
            return None

        # Extract the validated segment_index (we know it's valid because is_citable() passed)
        segment_index = self.attributes[SEGMENT_INDEX_KEY]
        
        # Convert to int (is_citable() already validated this)
        if isinstance(segment_index, int):
            doc_index = segment_index
        elif isinstance(segment_index, str) and segment_index.isdigit():
            doc_index = int(segment_index)
        elif isinstance(segment_index, float) and segment_index.is_integer():
            doc_index = int(segment_index)
        else:
            # This shouldn't happen since is_citable() passed, but be safe
            return None

        # Create snippet from text (limit length for display)
        snippet = self.text
        if snippet and len(snippet) > 200:
            snippet = snippet[:200] + "..."

        return AnnotationFileCitation(
            type="file_citation",
            file_id=self.file_id,
            index=doc_index,  # Use document segment index, not citation_id
            snippet=snippet or "",
            filename=self.filename,
        )

    def as_chunk(self) -> "Chunk":
        """Convert this file search result to a Chunk instance.

        The chunk index is determined from the segment_index in attributes,
        which represents the actual position within the source document.

        Returns:
            Chunk: A Chunk object containing the search result content and metadata.
        """
        from forge_cli.constants.metadata_keys import (
            DOC_ID_KEY,
            DOC_TITLE_KEY,
            DOCUMENT_TITLE_KEY,
            FILE_ID_KEY,
            SCORE_KEY,
            SEGMENT_INDEX_KEY,
        )

        # Create a unique ID for the chunk
        chunk_id = self.file_id or "file_search_unknown"
        if self.attributes and "segment_id" in self.attributes:
            chunk_id = self.attributes["segment_id"]
        elif self.file_id:
            # Use segment_index if available for unique ID
            if self.attributes and SEGMENT_INDEX_KEY in self.attributes:
                segment_idx = self.attributes[SEGMENT_INDEX_KEY]
                chunk_id = f"{self.file_id}_segment_{segment_idx}"
            else:
                chunk_id = f"{self.file_id}_chunk"

        # Check if this result is citable
        is_citable = self.is_citable()

        # Extract segment_index from attributes if available and citable
        chunk_index = None  # Default to None for non-citable
        if is_citable and self.attributes and SEGMENT_INDEX_KEY in self.attributes:
            # Only assign positive index to citable content with valid segment_index
            segment_index = self.attributes[SEGMENT_INDEX_KEY]
            if isinstance(segment_index, str) and segment_index.isdigit():
                chunk_index = int(segment_index)
            elif isinstance(segment_index, (int, float)):
                chunk_index = int(segment_index)

        # Determine document title
        doc_title = self.filename or "Unknown"
        if self.attributes and DOCUMENT_TITLE_KEY in self.attributes:
            doc_title = self.attributes[DOCUMENT_TITLE_KEY]

        # Create metadata with relevant information
        metadata = {} if self.attributes is None else dict(self.attributes)
        metadata.update({
            "annotation_type": "file_citation",
            FILE_ID_KEY: self.file_id,
            DOC_ID_KEY: self.file_id,
            "filename": self.filename,
            DOC_TITLE_KEY: doc_title,
            SCORE_KEY: self.score or 0.0,
            "source_type": "file_search_call",
        })

        # Add segment_type for non-citable results
        if not is_citable:
            metadata["segment_type"] = "navigate"

        # Create and return the chunk
        chunk = Chunk(
            id=chunk_id,
            content=self.text or "",
            index=chunk_index,  # None for non-citable, positive int for citable
            metadata=metadata
        )
        return chunk


class ResponseFileSearchToolCall(BaseModel):
    id: str
    """The unique ID of the file search tool call."""

    queries: List[str]
    """The queries used to search for files."""

    status: Literal["in_progress", "searching", "completed", "incomplete", "failed"]
    """The status of the file search tool call.

    One of `in_progress`, `searching`, `incomplete` or `failed`,
    """

    type: Literal["file_search_call"]
    """The type of the file search tool call. Always `file_search_call`."""

    file_id: Optional[str] = None
    """The ID of the specific file being searched, if filtered to a single document."""

    public_results: Optional[List[ResponseFileSearchToolCallResult]] = Field(default=None, alias="results")
    """Public results field that gets serialized to JSON."""

    _results: Optional[List[ResponseFileSearchToolCallResult]] = None
    """Private results field that won't be serialized to JSON."""

    @property
    def results(self) -> Optional[List[ResponseFileSearchToolCallResult]]:
        """Get results from either _results or _public_results field.
        
        Returns _results if available, otherwise falls back to _public_results.
        This allows internal processing to use _results while maintaining
        backward compatibility with existing code.
        
        Returns:
            Optional[List[ResponseFileSearchToolCallResult]]: The appropriate results list
        """
        return self._results if self._results is not None else self._public_results

    @results.setter
    def results(self, value: Optional[List[ResponseFileSearchToolCallResult]]) -> None:
        """Set results to the public results field.
        
        This maintains backward compatibility while allowing the choice of
        which field to populate based on use case.
        
        Args:
            value: The results to set
        """
        self._public_results = value

    _native_tool_call: Optional[ResponseFunctionToolCall] = PrivateAttr(default=None)
    """Private attribute that won't be included in serialization."""

    @classmethod
    def from_chat_tool_call(
        cls,
        chat_tool_call: "ToolCall",
        status: Literal["in_progress", "searching", "completed", "incomplete", "failed"] = "in_progress",
    ) -> "ResponseFileSearchToolCall":
        """Convert a ToolCall to a ResponseFileSearchToolCall.

        Args:
            chat_tool_call (ToolCall): A tool call object from our internal message types.
            status (Literal): The status to set for the file search tool call. Defaults to "in_progress".

        Returns:
            ResponseFileSearchToolCall: A file search tool call object compatible with the response style API.
        """
        import json

        # Extract queries and doc_id from the arguments
        queries = []
        file_id = None
        try:
            arguments = json.loads(chat_tool_call.function.arguments)
            if arguments:
                queries = arguments.get("queries", [])
                # Convert doc_id to file_id
                file_id = arguments.get("doc_id")
        except (json.JSONDecodeError, AttributeError):
            # Continue with empty queries if parsing fails
            pass

        # Create the ResponseFileSearchToolCall instance
        instance = cls(
            id=chat_tool_call.id,
            queries=queries,
            status=status,
            type="file_search_call",
            file_id=file_id,
        )

        # Store the original function tool call
        function_tool_call = ResponseFunctionToolCall.from_chat_tool_call(
            chat_tool_call=chat_tool_call,
            status="in_progress" if status in ["in_progress", "searching"] else status,
        )
        instance._native_tool_call = function_tool_call

        return instance

    @classmethod
    def from_general_function_tool_call(
        cls,
        function_tool_call: ResponseFunctionToolCall,
        status: Literal["in_progress", "searching", "completed", "incomplete", "failed"] = "in_progress",
    ) -> "ResponseFileSearchToolCall":
        """Convert a ResponseFunctionToolCall to a ResponseFileSearchToolCall.

        Args:
            function_tool_call (ResponseFunctionToolCall): A function tool call object.
            status (Literal): The status to set for the file search tool call. Defaults to "in_progress".

        Returns:
            ResponseFileSearchToolCall: A file search tool call object compatible with the response style API.
        """
        import json

        # Extract queries and doc_id from the arguments
        queries = []
        results = None
        file_id = None
        try:
            arguments = json.loads(function_tool_call.arguments)
            if arguments:
                queries = arguments.get("queries", [])
                # Convert doc_id to file_id
                file_id = arguments.get("doc_id")
        except (json.JSONDecodeError, AttributeError):
            # Continue with empty queries if parsing fails
            pass

        # Create the ResponseFileSearchToolCall instance
        instance = cls(
            id=function_tool_call.id or function_tool_call.call_id,
            queries=queries,
            status=status,
            type="file_search_call",
            file_id=file_id,
            results=results,
        )

        # Store the original function tool call
        instance._native_tool_call = function_tool_call

        return instance

    def to_general_function_tool_call(self) -> ResponseFunctionToolCall:
        if self._native_tool_call is not None:
            return self._native_tool_call

        # Create a JSON string of the queries and results if available
        import json

        arguments_dict = {"queries": self.queries}
        if self.file_id is not None:
            # Convert file_id back to doc_id
            arguments_dict["doc_id"] = self.file_id
        if self.results is not None:
            arguments_dict["results"] = [result.model_dump() for result in self.results]

        arguments = json.dumps(arguments_dict)

        # Create and return a ResponseFunctionToolCall
        return ResponseFunctionToolCall(
            arguments=arguments,
            call_id=self.id,
            name="file_search",
            type="function_call",
            id=self.id,
            status="completed" if self.status == "completed" else "in_progress",
        )

    def to_chat_tool_call(self) -> "ToolCall":
        """Convert to internal ToolCall type.
        
        Returns:
            ToolCall: Internal ToolCall object for use throughout Knowledge Forge.
        """
        # Import ToolCall here to avoid circular imports
        from message._types.tool_call import ToolCall, FunctionCall
        
        if self._native_tool_call is not None:
            # If we have a native tool call, extract its properties
            native = self._native_tool_call.to_chat_tool_call()
            return ToolCall(
                id=native.id,
                type="function",
                function=FunctionCall(
                    name=native.function.name,
                    arguments=native.function.arguments
                )
            )

        # Create a JSON string of the queries and doc_id
        import json

        arguments_dict = {"queries": self.queries}
        if self.file_id is not None:
            # Convert file_id back to doc_id
            arguments_dict["doc_id"] = self.file_id
        
        arguments = json.dumps(arguments_dict)

        # Create and return internal ToolCall
        return ToolCall(
            id=self.id,
            type="function",
            function=FunctionCall(
                name="file_search", 
                arguments=arguments
            ),
        )
    

    def as_chat_toolcall_result(self, **kwargs) -> Union[str, List["Chunk"]]:
        """Convert the file search tool call results to either a string or list of Chunks.

        This method is kept for backward compatibility. It delegates to chunkify().

        Args:
            **kwargs: Additional formatting options (currently unused)

        Returns:
            Union[str, List[Chunk]]: List of Chunk objects for completed calls with results,
                              or string message for failed/incomplete calls
        """
        return self.chunkify()

    def chunkify(self) -> Union[str, List["Chunk"]]:
        """Convert this file search tool call to chunks or return error message.
        
        This method encapsulates the conversion logic for file search results.
        Returns a descriptive string if conversion isn't possible, otherwise
        returns a list of Chunk objects for further processing.
        
        Returns:
            Union[str, List[Chunk]]: Error message string if conversion fails,
                                   or list of Chunk objects if successful
        """
        from forge_cli.common.logger import logger
        
        # Check status
        if self.status == "failed":
            return "File search failed - no results available."
        
        if self.status == "incomplete":
            return "File search incomplete - partial or no results available."
        
        if self.status != "completed":
            logger.debug(f"ResponseFileSearchToolCall.chunkify: Unexpected status '{self.status}'")
            return f"File search not completed - status: {self.status}"
        
        # Check for results
        if not self.results:
            return "File search completed but no results found."
        
        # Convert results to chunks, filtering out empty content
        chunks = []
        valid_results = 0
        
        for i, result in enumerate(self.results):
            try:
                # Count results with actual content
                if result.text and result.text.strip():
                    valid_results += 1
                    # Use the existing as_chunk() method which handles all metadata
                    chunk = result.as_chunk()
                    chunks.append(chunk)
                
            except Exception as e:
                logger.warning(f"Failed to convert file search result {i}: {e}")
                continue
        
        # Return appropriate message or chunks
        if not chunks:
            if valid_results == 0:
                return "File search completed but no results with content found."
            else:
                return "File search completed but failed to convert results to chunks."
        
        return chunks

    @property
    def result_signatures(self) -> frozenset[tuple[str, int]]:
        """Get unique signatures (file_id, segment_index) for all results.
        
        Returns:
            frozenset of (file_id, segment_index) tuples that uniquely identify
            each result in the vector store.
        """
        if not self.results:
            return frozenset()
            
        signatures = set()
        for result in self.results:
            if result.is_citable() and result.file_id and result.attributes:
                seg_idx = result.attributes.get('segment_index', -1)
                if seg_idx >= 0:  # Valid segment index
                    signatures.add((result.file_id, seg_idx))
                    
        return frozenset(signatures)

