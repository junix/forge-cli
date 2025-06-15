from typing import Callable, Literal, Protocol, TypedDict, Union


# Forward reference for Annotation types, actual import might be needed if used directly
# For now, assume they are defined elsewhere and will be imported by consumers
class AnnotationFileCitation: ...


class AnnotationURLCitation: ...


class AnnotationFilePath: ...


AnnotationUnion = Union[AnnotationFileCitation, AnnotationURLCitation, AnnotationFilePath]


class Citable(Protocol):
    citation_id: int | None  # Assuming citation_id is an attribute

    def set_citation_id(self, citation_id: int) -> None:
        # In a real protocol, you might not define the body,
        # but for TypedDicts that will use this, it's more of a structural guide.
        # Alternatively, make result TypedDicts directly define this.
        # For now, let's assume result types will have this method.
        ...

    def as_annotation(self) -> AnnotationUnion | None: ...

    # Common data fields (optional, include if consistently present)
    # text: Optional[str] = None
    # snippet: Optional[str] = None
    # type: Optional[str] = None # e.g. 'file_result', 'web_result'


# Using TypedDicts for specific result item structures
# These will structurally match the Citable protocol where methods are concerned,
# or we might need to adjust how Citable is used if methods are an issue for TypedDicts.
# For simplicity, methods like set_citation_id and as_annotation might exist on the
# actual class instances that these TypedDicts represent, not on the TypedDicts themselves.
# The protocol is more for functions that expect objects matching this shape.


class BaseSearchResult(TypedDict, total=False):
    citation_id: int | None
    # text: Optional[str] # Example common field
    # snippet: Optional[str] # Example common field
    # type: str # Example: 'file_result'


class FileSearchResult(BaseSearchResult):
    file_id: str
    filename: str
    # Assuming methods like set_citation_id and as_annotation are present on the objects
    # that this TypedDict describes, rather than being part of the TypedDict itself.
    # text: Optional[str] # from a chunk of the file
    # score: Optional[float]


class WebSearchResult(BaseSearchResult):
    url: str
    title: str
    snippet: str | None  # Snippet is more common for web results
    # score: Optional[float]


class DocumentFinderResult(BaseSearchResult):
    document_id: str  # Or similar identifier
    # text: Optional[str]
    # score: Optional[float]


# A generic result type for lists, if specific type is not known
AnyCitable = TypedDict(
    "AnyCitable",
    {
        "set_citation_id": Callable[[int], None] | None,  # Simplified representation
        "as_annotation": Callable[[], AnnotationUnion | None] | None,
        "file_id": str | None,
        "filename": str | None,
        "url": str | None,
        "title": str | None,
        "snippet": str | None,
        "document_id": str | None,
        "text": str | None,
        "type": str | None,  # To discriminate if needed
        "citation_id": int | None,
    },
    total=False,
)


# Type for the 'processed' dictionary in FileSearchProcessor
class ProcessedFileSearchData(TypedDict, total=False):
    type: Literal["file_search"]  # from BaseToolCallProcessor
    tool_name: str  # from BaseToolCallProcessor
    status: str  # from BaseToolCallProcessor
    action_text: str  # from BaseToolCallProcessor
    queries: list[str]  # from BaseToolCallProcessor
    results_count: int | None  # from BaseToolCallProcessor
    error_message: str | None  # from BaseToolCallProcessor
    file_id: str | None  # Specific to file search
    vector_store_ids: list[str] | None  # Specific to file search
    # Potentially other fields from BaseToolCallProcessor's process method
    raw_item: AnyCitable | None  # Or the specific ResponseFileSearchToolCall type


class ProcessedWebSearchData(TypedDict, total=False):  # Define similarly
    type: Literal["web_search"]
    tool_name: str
    status: str
    action_text: str
    queries: list[str]
    results_count: int | None
    error_message: str | None
    raw_item: AnyCitable | None  # Or ResponseFunctionWebSearch


class ProcessedDocumentFinderData(TypedDict, total=False):  # Define similarly
    type: Literal["document_finder"]
    tool_name: str
    status: str
    action_text: str
    queries: list[str]
    results_count: int | None
    error_message: str | None
    raw_item: AnyCitable | None  # Or ResponseDocumentFinderToolCall


# For MessageProcessor
class ProcessedMessage(TypedDict):
    type: Literal["message"]
    text: str
    annotations: list[AnnotationUnion]  # Or List[Annotation] if Annotation is already the union
    id: str
    status: str


# Generic processed tool call data type
class ProcessedToolCallData(TypedDict, total=False):
    type: str  # tool type
    tool_name: str
    status: str
    action_text: str
    queries: list[str]
    results_count: int | None
    error_message: str | None
    raw_item: AnyCitable | None
    # Additional tool-specific fields can be added by specific processors
    file_id: str | None
    doc_ids: list[str] | None
    query: str | None
    navigation: str | None
    vector_store_ids: list[str] | None
    count: int | None
