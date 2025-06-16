# ADR-011: Tool Call and Tool Call Result Architecture

Date: 2024-12-16
Status: Accepted

## Context

The Knowledge Forge CLI integrates with various AI tools and services that require a structured approach to tool definition, execution, and result handling. The system needs to support multiple tool types including file search, web search, function calls, computer automation, and document processing.

Previously, tool handling was scattered across different modules with inconsistent patterns:

1. **Mixed tool definitions**: Tool configurations and execution results were not clearly separated
2. **Inconsistent status tracking**: Different tools used different status enums and progress tracking
3. **No unified result handling**: Each tool type had its own result format without common interfaces
4. **Limited traceability**: No standardized way to track tool execution progress and debugging information
5. **Type safety issues**: Weak typing made it difficult to handle different tool types safely

The system needed a comprehensive architecture that could:

- Clearly separate tool definitions from execution results
- Provide consistent status tracking and progress monitoring
- Support both simple tools and complex traceable operations
- Enable type-safe tool handling with proper discriminated unions
- Support streaming updates and real-time progress tracking

## Decision

We will implement a two-tier architecture separating **Tool Definitions** from **Tool Call Results**, with a unified type system and consistent execution patterns.

### Architecture Overview

```
Tool Definitions (Input)          Tool Call Results (Output)
├── FileSearchTool               ├── ResponseFileSearchToolCall
├── WebSearchTool                ├── ResponseFunctionWebSearch  
├── FunctionTool                 ├── ResponseFunctionToolCall
├── ComputerTool                 ├── ResponseComputerToolCall
├── ListDocumentsTool            ├── ResponseListDocumentsToolCall
├── FileReaderTool               ├── ResponseFunctionFileReader
└── TraceableToolCall (base)     └── ResponseCodeInterpreterToolCall
```

### 1. Tool Definition Classes

Tool definition classes specify **what tools are available** and **how to configure them**:

```python
# Tool definitions specify capabilities and configuration
class FileSearchTool(BaseModel):
    type: Literal["file_search"]
    vector_store_ids: list[str]
    max_num_results: int | None = None
    ranking_options: RankingOptions | None = None

class WebSearchTool(BaseModel):
    type: Literal["web_search_preview", "web_search_preview_2025_03_11", "web_search"]
    search_context_size: Literal["low", "medium", "high"] | None = None
    user_location: UserLocation | None = None
```

### 2. Tool Call Result Classes

Tool call result classes represent **execution state and results** after tools are invoked:

```python
# Tool call results track execution and contain results
class ResponseFileSearchToolCall(BaseModel):
    id: str
    type: Literal["file_search_call"]
    status: Literal["in_progress", "searching", "completed", "incomplete", "failed"]
    queries: list[str]
    # Results are accessed through separate mechanisms

class ResponseFunctionWebSearch(BaseModel):
    id: str
    type: Literal["web_search_call"] 
    status: Literal["in_progress", "searching", "completed", "failed"]
    queries: list[str]
    results: list[WebSearchResult] | None = None  # Actual result data
```

### 3. Traceable Tool Call Base Class

For complex operations requiring progress tracking and execution logging:

```python
class TraceableToolCall(BaseModel):
    progress: float | None = Field(default=None, ge=0.0, le=1.0)
    execution_trace: str | None = Field(default=None)
    
    def append_trace(self, message: str, step_name: str | None = None) -> None:
        """Append timestamped execution trace entry"""
        
    def set_progress(self, progress: float) -> None:
        """Update execution progress (0.0 to 1.0)"""
```

### 4. Unified Type System

All tool types are unified through discriminated unions:

```python
# Tool definitions union
Tool: TypeAlias = Annotated[
    FileSearchTool | FunctionTool | WebSearchTool | ComputerTool | 
    ListDocumentsTool | FileReaderTool,
    PropertyInfo(discriminator="type"),
]

# Tool call results union  
ResponseOutputItem: TypeAlias = Annotated[
    ResponseOutputMessage | ResponseFileSearchToolCall | ResponseFunctionToolCall |
    ResponseFunctionWebSearch | ResponseListDocumentsToolCall |
    ResponseFunctionFileReader | ResponseComputerToolCall | ResponseReasoningItem,
    PropertyInfo(discriminator="type"),
]
```

## Consequences

### Positive

1. **Clear Separation of Concerns**: Tool definitions focus on configuration, results focus on execution state
2. **Consistent Status Tracking**: All tool calls use standardized status enums and progress tracking
3. **Type Safety**: Discriminated unions enable safe handling of different tool types
4. **Traceability**: TraceableToolCall provides detailed execution logging for complex operations
5. **Extensibility**: Easy to add new tool types following established patterns
6. **Streaming Support**: Progress tracking enables real-time updates during tool execution
7. **Developer Experience**: Clear interfaces with full IDE support and type checking
8. **Unified Result Handling**: Common patterns for accessing results across all tool types

### Negative

1. **Complexity**: Two-tier architecture requires understanding both tool definitions and results
2. **Code Duplication**: Some properties appear in both tool definitions and results
3. **Learning Curve**: Developers need to understand discriminated unions and type guards
4. **Import Overhead**: Multiple imports required for different tool types

### Neutral

1. **File Count**: Architecture requires many files but organizes them logically
2. **Type System Dependency**: Benefits require modern Python with type checking enabled

## Implementation Details

### Tool Definition Patterns

All tool definitions follow consistent patterns:

```python
class ToolName(BaseModel):
    type: Literal["tool_type"]  # Discriminator field
    # Configuration parameters specific to tool
    param1: Type
    param2: Type | None = None  # Optional parameters
```

### Tool Call Result Patterns

All tool call results follow consistent patterns:

```python
class ResponseToolCall(BaseModel):
    id: str                     # Unique execution ID
    type: Literal["call_type"]  # Discriminator field  
    status: Literal[...]        # Standardized status values
    # Execution-specific data
    queries: list[str] | None = None    # For search tools
    results: list[Result] | None = None # Actual result data
```

### Status Value Standards

Standardized status values across all tools:

- `"in_progress"`: Tool execution started
- `"searching"`: Tool is actively searching/processing  
- `"completed"`: Tool execution finished successfully
- `"incomplete"`: Tool execution finished but incomplete results
- `"failed"`: Tool execution failed with error

### Progress Tracking for Complex Tools

Tools inheriting from `TraceableToolCall` gain:

```python
# Progress tracking (0.0 to 1.0)
tool_call.set_progress(0.5)  # 50% complete

# Execution logging with timestamps
tool_call.append_trace("Starting document analysis", "analysis")
tool_call.append_trace("Processing page 1 of 10", "processing")

# Access trace history
trace_lines = tool_call.get_trace_lines()
```

### Result Data Structures

Actual result data is stored in specialized classes:

```python
class Chunk(BaseModel):
    """File search result chunk"""
    id: str
    content: str
    index: int | None = None  # For citations
    metadata: dict[str, Any]

class AnnotationFileCitation(BaseModel):
    """File citation for referencing results"""
    file_id: str
    index: int
    type: Literal["file_citation"]
    snippet: str | None = None
    filename: str | None = None
```

## Usage Patterns

### 1. Tool Definition and Request Creation

```python
# Define tools for request
file_search = FileSearchTool(
    type="file_search",
    vector_store_ids=["vs_123", "vs_456"],
    max_num_results=10
)

web_search = WebSearchTool(
    type="web_search_preview",
    search_context_size="medium"
)

# Create request with tools
request = create_typed_request(
    input_messages="Find information about AI",
    tools=[file_search, web_search]
)
```

### 2. Tool Call Result Processing

```python
from forge_cli.response.type_guards import (
    is_file_search_call, is_web_search_call, is_file_reader_call
)

def process_tool_results(response: Response):
    for item in response.output:
        if is_file_search_call(item):
            # Type checker knows item is ResponseFileSearchToolCall
            print(f"File search: {item.queries}")
            if item.status == "completed":
                # Access results through response methods
                results = response.get_file_search_results(item.id)
                
        elif is_web_search_call(item):
            # Type checker knows item is ResponseFunctionWebSearch  
            print(f"Web search: {item.queries}")
            if item.results:
                for result in item.results:
                    print(f"Found: {result.title}")
                    
        elif is_file_reader_call(item):
            # Type checker knows item is ResponseFunctionFileReader
            print(f"Reading progress: {item.progress}")
            if item.execution_trace:
                print("Execution log:")
                for line in item.get_trace_lines():
                    print(f"  {line}")
```

### 3. Streaming Progress Updates

```python
async def stream_with_progress(request: Request):
    async for event_type, response_snapshot in astream_typed_response(request):
        # Check for tool progress updates
        for item in response_snapshot.output:
            if is_file_reader_call(item) and item.progress is not None:
                print(f"Reading progress: {item.progress:.1%}")
                
            if hasattr(item, 'status') and item.status == "completed":
                print(f"Tool {item.type} completed")
```

## Tool Type Reference

### Search and Retrieval Tools

1. **FileSearchTool** → **ResponseFileSearchToolCall**
   - Vector store document search
   - Ranking and filtering options
   - Results accessed via response methods

2. **ListDocumentsTool** → **ResponseListDocumentsToolCall**
   - Advanced document listing with metadata filtering
   - Deduplication and score thresholding
   - Cross-vector-store search capabilities

3. **WebSearchTool** → **ResponseFunctionWebSearch**
   - Web search with location context
   - Configurable context window size
   - Direct result access via `results` property

### Content Processing Tools

4. **FileReaderTool** → **ResponseFunctionFileReader** (extends TraceableToolCall)
   - Direct document reading by ID
   - Progress tracking and navigation history
   - Detailed execution tracing
   - Results are accessed through separate mechanisms

### Automation Tools

5. **ComputerTool** → **ResponseComputerToolCall**
   - Computer interface automation
   - Screen interaction (click, type, screenshot)
   - Safety check integration

6. **FunctionTool** → **ResponseFunctionToolCall**
   - Custom function execution
   - JSON schema parameter validation
   - Flexible output handling

### Development Tools

7. **CodeInterpreterTool** → **ResponseCodeInterpreterToolCall**
   - Code execution environment
   - File and log output handling
   - Multi-step code execution

## Migration Guide

### From Legacy Tool Handling

1. **Separate tool definitions from results**:

   ```python
   # Before: Mixed definition and result
   class FileSearchConfig:
       vector_stores: list[str]
       status: str  # Mixed concerns!

   # After: Separate concerns
   file_search_tool = FileSearchTool(vector_store_ids=["vs_123"])
   # Results come back as ResponseFileSearchToolCall
   ```

2. **Use type guards for result processing**:

   ```python
   # Before: String comparison with cast
   if item.type == "file_search_call":
       file_search = cast(ResponseFileSearchToolCall, item)

   # After: Type guards
   if is_file_search_call(item):
       # item is automatically typed correctly
   ```

3. **Adopt traceable tools for complex operations**:

   ```python
   # Before: Manual progress tracking
   class CustomTool:
       def __init__(self):
           self.progress = 0.0
           self.log = []

   # After: Inherit from TraceableToolCall
   class CustomTool(TraceableToolCall):
       # Progress and tracing built-in
   ```

### Best Practices

1. **Always use type guards** when processing tool call results
2. **Check status before accessing results** to avoid incomplete data
3. **Use TraceableToolCall** for operations that benefit from progress tracking
4. **Leverage discriminated unions** for type-safe tool handling
5. **Access results through response methods** when available for consistency

## File Organization

The tool architecture is organized across multiple files in `src/forge_cli/response/_types/`:

### Tool Definition Files

- `file_search_tool.py` - File search configuration
- `web_search_tool.py` - Web search configuration
- `function_tool.py` - Custom function configuration
- `computer_tool.py` - Computer automation configuration
- `list_documents_tool.py` - List documents configuration
- `file_reader_tool.py` - File reader configuration
- `tool.py` - Unified tool type alias

### Tool Call Result Files

- `response_file_search_tool_call.py` - File search execution results
- `response_function_web_search.py` - Web search execution results
- `response_function_tool_call.py` - Function call execution results
- `response_computer_tool_call.py` - Computer tool execution results
- `response_list_documents_tool_call.py` - List documents execution results
- `response_function_file_reader.py` - File reader execution results
- `response_code_interpreter_tool_call.py` - Code interpreter execution results

### Supporting Files

- `traceable_tool.py` - Base class for progress tracking
- `response_output_item.py` - Unified output item type alias
- `chunk.py` - Result data structures
- `annotations.py` - Citation and reference types

### Parameter Files

- `*_param.py` files - TypedDict versions for API compatibility

## Related ADRs

- **ADR-010**: Response Type Guards (enables safe tool result handling)
- **ADR-004**: Snapshot-based Streaming Design (tool results in response snapshots)
- **ADR-008**: V3 Response Snapshot Display Architecture (tool result display)

## References

- [Pydantic Discriminated Unions](https://docs.pydantic.dev/latest/usage/types/unions/#discriminated-unions)
- [OpenAI Tools API](https://platform.openai.com/docs/guides/tools) (inspiration for tool patterns)
- [TypeScript Discriminated Unions](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#discriminated-unions)
