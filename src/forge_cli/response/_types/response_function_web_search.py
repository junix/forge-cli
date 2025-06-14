# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Any, Literal, Optional

from pydantic import PrivateAttr

from .response_function_tool_call import ResponseFunctionToolCall

if TYPE_CHECKING:
    pass

    from .annotations import AnnotationURLCitation

from ._models import BaseModel

__all__ = ["ResponseFunctionWebSearch", "ResponseFunctionWebSearchResult"]


class ResponseFunctionWebSearchResult(BaseModel):
    """Structured result from a web search operation."""

    title: str | None = None
    """The title of the web page."""

    url: str | None = None
    """The URL of the web page."""

    snippet: str | None = None
    """A snippet or description of the web page content."""

    site_name: str | None = None
    """The name of the source website."""

    date_published: str | None = None
    """The publication date of the content."""

    score: float | None = None
    """The relevance score of the result - a value between 0 and 1."""

    metadata: dict[str, Any] | None = None

    @property
    def citation_id(self) -> int | str | None:
        """The citation sequence number for this result."""
        if self.metadata is None:
            return None
        return self.metadata.get("citation_id")

    @citation_id.setter
    def citation_id(self, value: int | str) -> None:
        """Set the citation sequence number for this result."""
        if self.metadata is None:
            self.metadata = {}
        self.metadata["citation_id"] = value

    def set_citation_id(self, citation_id: int | str) -> None:
        """Set the citation sequence number for this result (method interface)."""
        self.citation_id = citation_id

    def is_citable(self) -> bool:
        """Check if the web search result is citable.

        Web search results are always considered citable.

        Returns:
            bool: Always True for web search results.
        """
        return True

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
            end_index=-1,  # No document position for web results
            snippet=snippet or "",
            favicon=favicon,
        )


class ResponseFunctionWebSearch(BaseModel):
    _results: list[ResponseFunctionWebSearchResult] = PrivateAttr(default_factory=list)
    _native_tool_call: ResponseFunctionToolCall | None = PrivateAttr(default=None)
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
    def results(self) -> list[ResponseFunctionWebSearchResult]:
        return self._results

    def add_result(self, result: ResponseFunctionWebSearchResult) -> None:
        """Add a web search result.

        Args:
            result: Either a ResponseFunctionWebSearchResult object or a dict with result data
        """
        assert isinstance(result, ResponseFunctionWebSearchResult)
        self._results.append(result)

    def add_results(self, results: list[ResponseFunctionWebSearchResult]) -> None:
        """Add multiple web search results.

        Args:
            results: List of ResponseFunctionWebSearchResult objects or dicts with result data
        """
        for result in results:
            self.add_result(result)

