# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from message._types.tool_call import ToolCall
from pydantic import PrivateAttr
from .response_function_tool_call import (
    ResponseFunctionToolCall,
)
from typing_extensions import Literal
if TYPE_CHECKING:
    from .annotations import AnnotationURLCitation
    from _types.chunk import Chunk

from ._models import BaseModel

__all__ = ["ResponseFunctionWebSearch", "ResponseFunctionWebSearchResult"]


class ResponseFunctionWebSearchResult(BaseModel):
    """Structured result from a web search operation."""

    title: Optional[str] = None
    """The title of the web page."""

    url: Optional[str] = None
    """The URL of the web page."""

    snippet: Optional[str] = None
    """A snippet or description of the web page content."""

    site_name: Optional[str] = None
    """The name of the source website."""

    date_published: Optional[str] = None
    """The publication date of the content."""

    score: Optional[float] = None
    """The relevance score of the result - a value between 0 and 1."""

    metadata: Optional[Dict[str, Any]] = None


    @property
    def citation_id(self) -> Optional[Union[int, str]]:
        """The citation sequence number for this result."""
        if self.metadata is None:
            return None
        return self.metadata.get("citation_id")

    @citation_id.setter
    def citation_id(self, value: Union[int, str]) -> None:
        """Set the citation sequence number for this result."""
        if self.metadata is None:
            self.metadata = {}
        self.metadata["citation_id"] = value

    def set_citation_id(self, citation_id: Union[int, str]) -> None:
        """Set the citation sequence number for this result (method interface)."""
        self.citation_id = citation_id

    def is_citable(self) -> bool:
        """Check if the web search result is citable.

        Web search results are always considered citable.

        Returns:
            bool: Always True for web search results.
        """
        return True

    def as_chunk(self, index: int) -> "Chunk":
        """Convert this web search result to a Chunk instance.

        Returns:
            Chunk: A Chunk object containing the search result content and metadata.
        """
        from _types.chunk import Chunk
        from forge_cli.common.logger import logger

        # Create a unique ID for the chunk
        chunk_id = f"web-search-{index}"

        # Create metadata with relevant information
        metadata = {} if self.metadata is None else dict(self.metadata)
        metadata.update({
            "annotation_type": "url_citation",
            "doc_url": self.url,
            "doc_title": self.title,
            "site": self.site_name,
            "date": self.date_published
        })

        # Create and return the chunk
        chunk = Chunk(
            id=chunk_id,
            content=self.snippet,
            index=index,
            metadata=metadata
        )
        return chunk


    def as_annotation(self) -> Optional["AnnotationURLCitation"]:
        """Convert this web search result to an annotation using URL as document reference.
        
        For web search results, there is no document segment index since they are
        not part of a structured document. Uses URL as the document reference.

        Returns:
            AnnotationURLCitation if this result has sufficient data and is citable,
            None if missing required fields or not citable
        """
        # Import here to avoid circular imports
        from .annotations import AnnotationURLCitation

        # Use is_citable() to check if this result can be used for annotations
        if not self.is_citable():
            return None

        # Validate required fields for URL annotation
        if not self.url or not self.snippet:
            return None

        # Create snippet from content (limit length for display)
        snippet = self.snippet
        if snippet and len(snippet) > 200:
            snippet = snippet[:200] + "..."

        favicon = self.metadata.get("favicon")
        # For web search results, use -1 as index since there's no document position
        return AnnotationURLCitation(
            type="url_citation",
            url=self.url,
            title=self.title or "Web Result",
            start_index=-1,  # No document position for web results
            end_index=-1,    # No document position for web results
            snippet=snippet or "",
            favicon=favicon,
        )


class ResponseFunctionWebSearch(BaseModel):
    _results: List[ResponseFunctionWebSearchResult] = PrivateAttr(default_factory=list)
    _native_tool_call: Optional[ResponseFunctionToolCall] = PrivateAttr(default=None)
    """Private attribute that won't be included in serialization."""

    id: str
    """The unique ID of the web search tool call."""

    status: Literal["in_progress", "searching", "completed", "failed"]
    """The status of the web search tool call."""

    type: Literal["web_search_call"]
    """The type of the web search tool call. Always `web_search_call`."""

    queries: list[str]
    """The search query used for web search."""

    @property
    def results(self) -> List[ResponseFunctionWebSearchResult]:
        return self._results

    def add_result(self, result: ResponseFunctionWebSearchResult) -> None:
        """Add a web search result.

        Args:
            result: Either a ResponseFunctionWebSearchResult object or a dict with result data
        """
        assert  isinstance(result, ResponseFunctionWebSearchResult)
        self._results.append(result)

    def add_results(self, results: List[ResponseFunctionWebSearchResult]) -> None:
        """Add multiple web search results.

        Args:
            results: List of ResponseFunctionWebSearchResult objects or dicts with result data
        """
        for result in results:
            self.add_result(result)

    @classmethod
    def from_chat_tool_call(
        cls,
        chat_tool_call: "ToolCall",
        status: Literal["in_progress", "searching", "completed", "failed"] = "in_progress",
    ) -> "ResponseFunctionWebSearch":
        """Convert a ToolCall to a ResponseFunctionWebSearch.

        Args:
            chat_tool_call (ToolCall): A tool call object from our internal message types.
            status (Literal): The status to set for the web search tool call. Defaults to "in_progress".

        Returns:
            ResponseFunctionWebSearch: A web search tool call object compatible with the response style API.
        """
        import json

        # Extract query from the arguments
        queries = []
        try:
            arguments = json.loads(chat_tool_call.function.arguments)
            if arguments:
                # Web search uses "queries" array, take first query
                queries = arguments.get("queries") or arguments.get("query") or []
                if isinstance(queries, str):
                    queries = [queries]
        except (json.JSONDecodeError, AttributeError):
            # Continue with empty query if parsing fails
            pass

        # Create the ResponseFunctionWebSearch instance
        instance = cls(
            id=chat_tool_call.id,
            queries=queries,
            status=status,
            type="web_search_call",
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
        status: Literal["in_progress", "searching", "completed", "failed"] = "in_progress",
    ) -> "ResponseFunctionWebSearch":
        """Convert a ResponseFunctionToolCall to a ResponseFunctionWebSearch.

        Args:
            function_tool_call (ResponseFunctionToolCall): A function tool call object.
            status (Literal): The status to set for the web search tool call. Defaults to "in_progress".

        Returns:
            ResponseFunctionWebSearch: A web search tool call object compatible with the response style API.
        """
        import json

        # Extract query from the arguments
        queries = []
        try:
            arguments = json.loads(function_tool_call.arguments)
            if arguments:
                # Web search uses "queries" array, take first query
                queries = arguments.get("queries") or arguments.get("query") or []
                if isinstance(queries, str):
                    queries = [queries]
        except (json.JSONDecodeError, AttributeError):
            # Continue with empty query if parsing fails
            pass

        # Create the ResponseFunctionWebSearch instance
        instance = cls(
            id=function_tool_call.id or function_tool_call.call_id,
            queries=queries,
            status=status,
            type="web_search_call",
        )

        # Store the original function tool call
        instance._native_tool_call = function_tool_call

        return instance

    def to_general_function_tool_call(self) -> ResponseFunctionToolCall:
        """Convert this ResponseFunctionWebSearch to a general ResponseFunctionToolCall.

        Returns:
            ResponseFunctionToolCall: A function tool call representation of this web search call.
        """
        if self._native_tool_call is not None:
            return self._native_tool_call

        # Create a JSON string of the query and search results if available
        import json

        arguments_dict = {"queries": self.queries}
        if self._results:
            # Convert structured results to dict format for serialization
            arguments_dict["results"] = [result.model_dump() for result in self._results]

        arguments = json.dumps(arguments_dict)

        # Create and return a ResponseFunctionToolCall
        return ResponseFunctionToolCall(
            arguments=arguments,
            call_id=self.id,
            name="web_search",
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

        # Create a JSON string of the query
        import json

        arguments = json.dumps({"queries": self.queries})

        # Create and return internal ToolCall
        return ToolCall(
            id=self.id,
            type="function",
            function=FunctionCall(
                name="web_search", 
                arguments=arguments
            ),
        )
    

    def as_chat_toolcall_result(self, **kwargs) -> Union[str, List["Chunk"]]:
        """Convert the web search tool call results to either a string or list of Chunks.

        This method is kept for backward compatibility. It delegates to chunkify().

        Args:
            **kwargs: Additional formatting options (currently unused)

        Returns:
            Union[str, List[Chunk]]: List of Chunk objects for completed calls with results,
                              or string message for failed calls
        """
        return self.chunkify()

    def chunkify(self) -> Union[str, List["Chunk"]]:
        """Convert this web search tool call to chunks or return error message.
        
        This method encapsulates the conversion logic for web search results.
        Returns a descriptive string if conversion isn't possible, otherwise
        returns a list of Chunk objects for further processing.
        
        Returns:
            Union[str, List[Chunk]]: Error message string if conversion fails,
                                   or list of Chunk objects if successful
        """
        from forge_cli.common.logger import logger
        from constants.metadata_keys import (
            DOC_TITLE_KEY,
            DOC_URL_KEY,
            SCORE_KEY,
        )
        
        # Check status
        if self.status == "failed":
            return "Web search failed - no results available."
        
        if self.status == "incomplete":
            return "Web search incomplete - partial or no results available."
            
        if self.status != "completed":
            logger.debug(f"ResponseFunctionWebSearch.chunkify: Unexpected status '{self.status}'")
            return f"Web search not completed - status: {self.status}"
        
        # Check for results
        if not self._results:
            return "Web search completed but no results found."
        
        # Import Chunk here to avoid circular imports
        from _types.chunk import Chunk
        
        # Convert results to chunks
        chunks = []
        valid_results = 0
        source_type = "web_search_call"
        
        for i, result in enumerate(self._results):
            try:
                # Count results with actual content
                if result.snippet and result.snippet.strip():
                    valid_results += 1
                    
                    chunk_id = f"web_search_call_{i}"
                    
                    # Build metadata
                    metadata = {
                        "annotation_type": "url_citation",
                        "url": result.url or "",
                        DOC_URL_KEY: result.url or "",
                        "title": result.title or "",
                        DOC_TITLE_KEY: result.title or "",
                        "source_type": source_type,
                        SCORE_KEY: (
                            result.score if result.score is not None else (1.0 - (i * 0.1))
                        ),  # Use provided score or simple relevance scoring
                    }
                    
                    # Add optional fields if available
                    if result.date_published:
                        metadata["date_published"] = result.date_published
                    if result.site_name:
                        metadata["site_name"] = result.site_name
                    
                    # Merge original metadata (if any)
                    if result.metadata:
                        metadata.update(result.metadata)
                    
                    chunk = Chunk(
                        id=chunk_id,
                        content=result.snippet,
                        index=i,
                        metadata=metadata,
                    )
                    chunks.append(chunk)
                
            except Exception as e:
                logger.warning(f"Failed to convert web search result {i}: {e}")
                continue
        
        # Return appropriate message or chunks
        if not chunks:
            if valid_results == 0:
                return "Web search completed but no results with content found."
            else:
                return "Web search completed but failed to convert results to chunks."
        
        return chunks

