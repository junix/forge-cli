"""Output type definitions matching the Knowledge Forge API response structure."""

from typing import TypedDict, List, Optional, Literal, Any, Union


class SummaryItem(TypedDict):
    """Summary item within reasoning blocks."""

    text: str
    type: Literal["summary_text"]


class ReasoningItem(TypedDict):
    """Reasoning output item containing thinking/analysis."""

    id: str
    summary: List[SummaryItem]
    type: Literal["reasoning"]
    encrypted_content: Optional[str]
    status: str


class FileSearchCall(TypedDict):
    """File search tool call output item."""

    id: str
    queries: List[str]
    status: str
    type: Literal["file_search_call"]
    file_id: Optional[str]
    public_results: Optional[Any]


class DocumentFinderCall(TypedDict):
    """Document finder tool call output item."""

    id: str
    queries: List[str]
    count: int
    status: str
    type: Literal["document_finder_call"]


class WebSearchCall(TypedDict):
    """Web search tool call output item."""

    id: str
    queries: List[str]
    status: str
    type: Literal["web_search_call"]
    results: Optional[List[Any]]


class FileReaderCall(TypedDict):
    """File reader tool call output item."""

    id: str
    query: Optional[str]
    doc_ids: List[str]
    status: str
    type: Literal["file_reader_call"]
    execution_trace: Optional[str]
    progress: Optional[float]


class Annotation(TypedDict):
    """Citation annotation within message content."""

    file_id: Optional[str]
    index: int
    type: Literal["file_citation", "url_citation"]
    snippet: Optional[str]
    filename: Optional[str]
    url: Optional[str]
    title: Optional[str]
    file: Optional[dict]  # Can contain nested file info


class MessageContent(TypedDict):
    """Content within a message item."""

    annotations: List[Annotation]
    text: str
    type: Literal["output_text"]


class MessageItem(TypedDict):
    """Message output item containing the final response."""

    id: str
    content: List[MessageContent]
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
