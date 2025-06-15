from collections.abc import Callable
from typing import Literal, TypedDict

# Import annotation types from their proper location
from forge_cli.response._types.annotations import (
    AnnotationFileCitation,
    AnnotationFilePath,
    AnnotationURLCitation,
)

# Create the union type from the proper imports
AnnotationUnion = AnnotationFileCitation | AnnotationURLCitation | AnnotationFilePath


# FileSearchResult is actually used in file_search_typed.py
class FileSearchResult(TypedDict, total=False):
    file_id: str
    filename: str
    citation_id: int | None


# A generic result type for processed tool call data
class AnyCitable(TypedDict, total=False):
    set_citation_id: Callable[[int], None] | None  # Simplified representation
    as_annotation: Callable[[], AnnotationUnion | None] | None
    file_id: str | None
    filename: str | None
    url: str | None
    title: str | None
    snippet: str | None
    document_id: str | None
    text: str | None
    type: str | None  # To discriminate if needed
    citation_id: int | None


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
    raw_item: AnyCitable | None  # Or the specific ResponseFileSearchToolCall type


# Generic processed tool call data type (used by file_reader and document_finder processors)
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
