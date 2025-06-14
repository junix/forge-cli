"""Output type definitions matching the Knowledge Forge API response structure."""

from typing import Literal, TypedDict, Union


class SummaryItem(TypedDict):
    """Summary item within reasoning blocks."""

    text: str
    type: Literal["summary_text"]


class ReasoningItem(TypedDict):
    """Reasoning output item containing thinking/analysis."""

    id: str
    summary: list[SummaryItem]
    type: Literal["reasoning"]
    encrypted_content: str | None
    status: str


class FileSearchCall(TypedDict):
    """File search tool call output item."""

    id: str
    queries: list[str]
    status: str
    type: Literal["file_search_call"]
    file_id: str | None
    public_results: list[dict[str, str | int | float]] | None


class DocumentFinderCall(TypedDict):
    """Document finder tool call output item."""

    id: str
    queries: list[str]
    count: int
    status: str
    type: Literal["document_finder_call"]


class WebSearchCall(TypedDict):
    """Web search tool call output item."""

    id: str
    queries: list[str]
    status: str
    type: Literal["web_search_call"]
    results: list[dict[str, str | int | float]] | None


class FileReaderCall(TypedDict):
    """File reader tool call output item."""

    id: str
    query: str | None
    doc_ids: list[str]
    status: str
    type: Literal["file_reader_call"]
    execution_trace: str | None
    progress: float | None


class Annotation(TypedDict):
    """Citation annotation within message content."""

    file_id: str | None
    index: int
    type: Literal["file_citation", "url_citation"]
    snippet: str | None
    filename: str | None
    url: str | None
    title: str | None
    file: dict | None  # Can contain nested file info


class MessageContent(TypedDict):
    """Content within a message item."""

    annotations: list[Annotation]
    text: str
    type: Literal["output_text"]


class MessageItem(TypedDict):
    """Message output item containing the final response."""

    id: str
    content: list[MessageContent]
    role: Literal["assistant"]
    status: str
    type: Literal["message"]


# Union type for all possible output items
OutputItem = Union[
    ReasoningItem,
    FileSearchCall,
    DocumentFinderCall,
    WebSearchCall,
    FileReaderCall,
    MessageItem,
    dict,  # For unknown/future types
]
