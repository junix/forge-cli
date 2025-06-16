# Data Models

This section describes the core data structures used by Knowledge Forge APIs. These models are presented as Python Pydantic models to clearly show their structure, types, and field descriptions. Understanding these models helps users integrate with Knowledge Forge's Response API architecture.

## Core Response API Models

Knowledge Forge implements a Response API (not Chat Completions API). Here are the core models:

### Request Model

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Union, Any, Literal

class Request(BaseModel):
    """Request parameters for generating a response."""
    
    model: str = Field(..., description="Model ID used to generate the response")
    user: str = Field(..., description="User identifier for request tracking")
    input: Union[str, List[Union[InputMessage, str]]] = Field(
        ..., description="Input text or array of input items"
    )
    effort: Literal["low", "medium", "high", "dev"] = Field(
        default="low", description="Response generation effort level"
    )
    
    # Optional parameters
    instructions: Optional[str] = Field(None, description="System instructions")
    tools: Optional[List[Tool]] = Field(None, description="Available tools")
    tool_choice: Optional[Union[str, Dict]] = Field("auto", description="Tool usage control")
    temperature: Optional[float] = Field(1.0, description="Sampling temperature (0-2)")
    max_output_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    previous_response_id: Optional[str] = Field(None, description="Previous response for continuation")
    stream: Optional[bool] = Field(False, description="Enable SSE streaming")
    store: Optional[bool] = Field(True, description="Store response for history")
```

### Response Model

```python
class Response(BaseModel):
    """Main response object containing AI-generated content and tool results."""
    
    id: str = Field(..., description="Unique response identifier")
    object: Literal["response"] = Field("response", description="Object type - always 'response'")
    created_at: float = Field(..., description="Unix timestamp when response was created")
    status: Literal["in_progress", "completed", "failed", "incomplete"] = Field(
        ..., description="Response generation status"
    )
    model: str = Field(..., description="Model used for generation")
    
    # Core content
    output: List[ResponseOutputItem] = Field(
        default_factory=list, description="Array of output items (tool calls, messages)"
    )
    
    # Metadata
    usage: Optional[ResponseUsage] = Field(None, description="Token usage statistics")
    tools: Optional[List[Tool]] = Field(None, description="Tools available for this response")
    parallel_tool_calls: bool = Field(True, description="Whether tools can run in parallel")
    
    # Optional fields
    error: Optional[ResponseError] = Field(None, description="Error details if status is 'failed'")
    instructions: Optional[str] = Field(None, description="System instructions used")
    temperature: Optional[float] = Field(None, description="Sampling temperature used")
    max_output_tokens: Optional[int] = Field(None, description="Token limit used")
    user: Optional[str] = Field(None, description="User identifier")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional metadata")
```

### Output Item Types

```python
from typing import Union

# Union of all possible output items in a Response
ResponseOutputItem = Union[
    ResponseOutputMessage,        # Assistant messages with content
    ResponseFileSearchToolCall,   # File search tool execution results  
    ResponseFunctionWebSearch,    # Web search tool execution results
    ResponseListDocumentsToolCall, # Document finder tool execution results
    ResponseFunctionToolCall,     # Generic function tool calls
    ResponseComputerToolCall,     # Computer use tool calls
    ResponseReasoningItem,        # Reasoning content
]

class ResponseOutputMessage(BaseModel):
    """Assistant message with rich content."""
    
    type: Literal["message"] = "message"
    role: Literal["assistant"] = "assistant"
    content: List[Union[ResponseOutputText, ResponseOutputRefusal]] = Field(
        default_factory=list, description="Message content items"
    )

class ResponseOutputText(BaseModel):
    """Text content with annotations and citations."""
    
    type: Literal["output_text"] = "output_text"
    text: str = Field(..., description="The generated text content")
    annotations: Optional[List[Union[AnnotationFileCitation, AnnotationURLCitation]]] = Field(
        default_factory=list, description="Citations and references"
    )
```

### Tool Call Models

```python
class ResponseFileSearchToolCall(BaseModel):
    """File search tool execution results."""
    
    type: Literal["file_search_call"] = "file_search_call"
    id: str = Field(..., description="Unique tool call identifier")
    status: Literal["in_progress", "searching", "completed", "incomplete"] = Field(
        ..., description="Tool execution status"
    )
    queries: List[str] = Field(..., description="Search queries used")
    results: Optional[List[ResponseFileSearchToolCallResult]] = Field(
        None, description="Search results"
    )

class ResponseFileSearchToolCallResult(BaseModel):
    """Individual file search result."""
    
    file_id: Optional[str] = Field(None, description="Source file identifier")
    filename: Optional[str] = Field(None, description="Source filename")
    text: Optional[str] = Field(None, description="Retrieved text content")
    score: Optional[float] = Field(None, description="Relevance score (0-1)")
    attributes: Optional[Dict[str, Union[str, float, bool, int]]] = Field(
        None, description="Additional metadata including segment_index and citation_id"
    )

class ResponseFunctionWebSearch(BaseModel):
    """Web search tool execution results."""

    type: Literal["web_search_call"] = "web_search_call"
    id: str = Field(..., description="Unique tool call identifier")
    status: Literal["in_progress", "searching", "completed", "failed"] = Field(
        ..., description="Tool execution status"
    )
    queries: List[str] = Field(..., description="Search queries used")
    # Results are accessed through separate mechanisms

class ResponseFunctionWebSearchResult(BaseModel):
    """Individual web search result."""
    
    title: Optional[str] = Field(None, description="Page title")
    url: Optional[str] = Field(None, description="Page URL")
    snippet: Optional[str] = Field(None, description="Content snippet")
    site_name: Optional[str] = Field(None, description="Source website name")
    date_published: Optional[str] = Field(None, description="Publication date")
    score: Optional[float] = Field(None, description="Relevance score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
```

### Citation and Annotation Models

```python
class AnnotationFileCitation(BaseModel):
    """File-based citation annotation."""
    
    type: Literal["file_citation"] = "file_citation"
    file_id: str = Field(..., description="Source file identifier")
    index: int = Field(..., description="Document segment index")
    snippet: str = Field(..., description="Quoted text snippet")
    filename: Optional[str] = Field(None, description="Source filename")

class AnnotationURLCitation(BaseModel):
    """URL-based citation annotation."""
    
    type: Literal["url_citation"] = "url_citation"
    url: str = Field(..., description="Source URL")
    title: Optional[str] = Field(None, description="Page title")
    snippet: str = Field(..., description="Quoted text snippet")
    start_index: int = Field(..., description="Start position in source")
    end_index: int = Field(..., description="End position in source")
```

### Usage and Error Models

```python
class ResponseUsage(BaseModel):
    """Token usage statistics for a response."""
    
    input_tokens: int = Field(..., description="Tokens in the input")
    output_tokens: int = Field(..., description="Tokens in the output")
    total_tokens: int = Field(..., description="Total tokens used")
    input_tokens_details: Optional[InputTokensDetails] = Field(None)
    output_tokens_details: Optional[OutputTokensDetails] = Field(None)

class ResponseError(BaseModel):
    """Error information when response generation fails."""
    
    type: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    code: Optional[str] = Field(None, description="Error code")
```

## Tool Definition Models

```python
class FileSearchTool(BaseModel):
    """File search tool definition."""
    
    type: Literal["file_search"] = "file_search"
    vector_store_ids: List[str] = Field(..., description="Vector stores to search")
    max_num_results: Optional[int] = Field(10, description="Maximum results (1-50)")
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")
    ranking_options: Optional[Dict[str, Any]] = Field(None, description="Ranking configuration")

class WebSearchTool(BaseModel):
    """Web search tool definition."""
    
    type: Literal["web_search", "web_search_preview"] = "web_search"
    search_context_size: Optional[Literal["low", "medium", "high"]] = Field(
        "medium", description="Context window size for search"
    )
    user_location: Optional[Dict[str, Any]] = Field(None, description="User location hints")

class ListDocumentsTool(BaseModel):
    """List documents tool definition."""

    type: Literal["list_documents"] = "list_documents"
    vector_store_ids: List[str] = Field(..., description="Vector stores to search")
    max_num_results: Optional[int] = Field(20, description="Maximum results (1-50)")
    score_threshold: Optional[float] = Field(None, description="Minimum relevance score")
    deduplicate: Optional[bool] = Field(True, description="Remove duplicate documents")
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")
```

## Document and File Models

```python
class FileResponse(BaseModel):
    """Response from file upload."""
    
    id: str = Field(..., description="Unique file identifier")
    object: str = Field(default="file", description="Object type - always 'file'")
    bytes: int = Field(..., description="File size in bytes")
    created_at: int = Field(..., description="Upload timestamp")
    filename: str = Field(..., description="Original filename")
    purpose: str = Field(..., description="File purpose (e.g., 'qa', 'general')")
    task_id: str = Field(..., description="Background processing task ID")

class Document(BaseModel):
    """Processed document with content and metadata."""
    
    id: str = Field(..., description="Unique document identifier (UUID4)")
    md5sum: str = Field(..., description="MD5 checksum of original content")
    mime_type: str = Field(..., description="MIME type of original file")
    title: str = Field(..., description="Document title")
    author: Optional[str] = Field(None, description="Document author")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    url: Optional[str] = Field(None, description="Original URL if applicable")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Custom metadata"
    )
    vector_store_ids: Optional[List[str]] = Field(
        default_factory=list, description="Associated vector store IDs"
    )
    content: Optional[DocumentContent] = Field(None, description="Parsed document content")

class DocumentContent(BaseModel):
    """Detailed parsed content of a document."""
    
    id: str = Field(..., description="Content identifier (MD5 of binary content)")
    abstract: Optional[str] = Field(None, description="Generated abstract")
    summary: Optional[str] = Field(None, description="Generated summary")
    outline: Optional[str] = Field(None, description="Generated outline")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    language: Optional[str] = Field(None, description="Detected language")
    page_count: Optional[int] = Field(None, description="Number of pages")
    file_type: Optional[str] = Field(None, description="File format type")
    encoding: Optional[str] = Field(None, description="Text encoding")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Content-specific metadata"
    )
    segments: Optional[List[Union[Page, Chunk]]] = Field(
        default_factory=list, description="Content segments (pages/chunks)"
    )

class Chunk(BaseModel):
    """Text chunk with position and metadata."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique chunk ID")
    content: Optional[str] = Field(None, description="Text content")
    index: Optional[int] = Field(None, description="Position index in document")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Chunk-specific metadata"
    )

class Page(Chunk):
    """Document page (specialized chunk)."""
    
    url: str = Field(..., description="Page-specific URL or reference")
```

## Vector Store Models

```python
class VectorStore(BaseModel):
    """Vector store (collection) for semantic search."""
    
    id: str = Field(..., description="Unique vector store identifier")
    object: str = Field(default="vector_store", description="Object type")
    created_at: int = Field(..., description="Creation timestamp")
    name: Optional[str] = Field(None, description="Vector store name")
    description: Optional[str] = Field(None, description="Vector store description")
    bytes: Optional[int] = Field(None, description="Total size in bytes")
    file_counts: Optional[FileCountStats] = Field(None, description="File statistics")

class FileCountStats(BaseModel):
    """File processing statistics."""
    
    in_progress: int = Field(0, description="Files being processed")
    completed: int = Field(0, description="Successfully processed files")
    failed: int = Field(0, description="Failed processing files")
    cancelled: int = Field(0, description="Cancelled processing files")
    total: int = Field(0, description="Total files in vector store")
```

## Task Management Models

```python
class Trace(BaseModel):
    """Background task tracking."""
    
    id: str = Field(..., description="Unique task identifier")
    status: Optional[str] = Field(None, description="Task status")
    progress: float = Field(default=0.0, description="Completion progress (0.0-1.0)")
    data: Optional[Union[str, int, float, list, Dict[str, Any]]] = Field(
        None, description="Task-specific data"
    )
    failure_reason: Optional[str] = Field(None, description="Failure reason if status is 'failed'")
    created_at: Optional[int] = Field(None, description="Task creation timestamp")
    updated_at: Optional[int] = Field(None, description="Last update timestamp")
```

## Input Content Models

```python
class InputTextContent(BaseModel):
    """Text input content."""
    
    type: Literal["input_text"] = "input_text"
    text: str = Field(..., description="Input text content")

class InputFileContent(BaseModel):
    """File input content."""
    
    type: Literal["input_file"] = "input_file"
    file_id: str = Field(..., description="Reference to uploaded file")

class InputImageContent(BaseModel):
    """Image input content."""
    
    type: Literal["input_image"] = "input_image"
    image_url: str = Field(..., description="Image URL or data URI")
```

---

## Model Relationships

```
Request
├── tools: List[Tool]
├── input: List[InputContent]
└── → generates → Response
                  ├── output: List[ResponseOutputItem]
                  │   ├── ResponseOutputMessage
                  │   │   └── content: List[ResponseOutputText]
                  │   │       └── annotations: List[Citation]
                  │   ├── ResponseFileSearchToolCall
                  │   │   └── results: List[FileSearchResult]
                  │   └── ResponseFunctionWebSearch
                  │       └── results: List[WebSearchResult]
                  └── usage: ResponseUsage

VectorStore
├── file_counts: FileCountStats
└── contains → Document
               ├── content: DocumentContent
               │   └── segments: List[Chunk|Page]
               └── processed_by → FileResponse
                                  └── task_id → Trace
```

This data model documentation helps users understand Knowledge Forge's Response API architecture and integrate effectively with the system's rich type system.
