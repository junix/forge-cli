# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional, Union
import xml.etree.ElementTree as ET

from pydantic import PrivateAttr
from typing_extensions import Literal

from ._models import BaseModel
from .response_function_tool_call import ResponseFunctionToolCall

__all__ = ["ResponseDocumentFinderToolCall", "DocumentFinderResult"]


class DocumentFinderResult(BaseModel):
    document_id: str
    """The unique ID of the document."""

    title: str
    """The title of the document."""

    content: str
    """A snippet of the document content."""

    score: float
    """The relevance score of this document (0-1)."""

    metadata: Optional[Dict[str, Union[str, float, bool, int]]] = None
    """Additional metadata about the document."""


class ResponseDocumentFinderToolCall(BaseModel):
    id: str
    """The unique ID of the document finder tool call."""

    queries: List[str]
    """The queries used to search for documents."""

    count: int = 10
    """The number of documents to return."""

    status: Literal["in_progress", "searching", "completed", "incomplete"]
    """The status of the document finder tool call.

    One of `in_progress`, `searching`, `completed` or `incomplete`.
    """

    type: Literal["document_finder_call"]
    """The type of the document finder tool call. Always `document_finder_call`."""

    _results: Optional[List[DocumentFinderResult]] = None
    """The results of the document finder tool call."""

    _native_tool_call: Optional[ResponseFunctionToolCall] = PrivateAttr(default=None)
    """Private attribute that won't be included in serialization."""

    @property
    def results(self) -> Optional[List[DocumentFinderResult]]:
        return self._results

    def chunkify(self) -> str:
        """Convert DocumentFinderResult list to XML string format.
        
        Returns:
            str: XML representation of the document finder results.
        """
        if not self._results:
            return "No documents found"
        
        # Build XML manually with CDATA sections
        xml_parts = ["<documents>"]
        
        for result in self._results:
            xml_parts.append(f'<document>')
            
            # Add title with CDATA
            xml_parts.append(f"<title>{result.title}</title>")
            
            # Add content with CDATA
            xml_parts.append(f"<content>{result.content}</content>")
            
            # Add metadata if present
            if result.metadata:
                for key, value in result.metadata.items():
                    if key in ("score", "collection_name", "segment_type", "content"):
                        continue
                    if key == "file_id":
                        key = "doc_id"
                    xml_parts.append(f'<{key}>{str(value)}</{key}>')
            
            xml_parts.append("</document>")
        
        xml_parts.append("</documents>")
        
        return "".join(xml_parts)

    @classmethod
    def from_general_function_tool_call(
        cls,
        function_tool_call: ResponseFunctionToolCall,
        status: Literal["in_progress", "searching", "completed", "incomplete"] = "in_progress",
    ) -> "ResponseDocumentFinderToolCall":
        """Convert a ResponseFunctionToolCall to a ResponseDocumentFinderToolCall.

        Args:
            function_tool_call (ResponseFunctionToolCall): A function tool call object.
            status (Literal): The status to set for the document finder tool call. Defaults to "in_progress".

        Returns:
            ResponseDocumentFinderToolCall: A document finder tool call object compatible with the response style API.
        """
        import json

        # Extract queries and count from the arguments
        queries = []
        count = 10  # Default value
        results = None
        try:
            arguments = json.loads(function_tool_call.arguments)
            if arguments:
                queries = arguments.get("queries", [])
                count = arguments.get("count", 10)
        except (json.JSONDecodeError, AttributeError):
            # Continue with defaults if parsing fails
            pass

        # Create the ResponseDocumentFinderToolCall instance
        instance = cls(
            id=function_tool_call.id or function_tool_call.call_id,
            queries=queries,
            count=count,
            status=status,
            type="document_finder_call",
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

        arguments_dict = {
            "queries": self.queries,
            "count": self.count
        }
        if self.results is not None:
            arguments_dict["results"] = [result.model_dump() for result in self.results]

        arguments = json.dumps(arguments_dict)

        # Create and return a ResponseFunctionToolCall
        return ResponseFunctionToolCall(
            arguments=arguments,
            call_id=self.id,
            name="document_finder",
            type="function_call",
            id=self.id,
            status="completed" if self.status == "completed" else "in_progress",
        )

    

