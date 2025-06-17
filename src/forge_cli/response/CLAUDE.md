# Response Module (`response/`)

## Overview

The `response` module implements the Response API, providing OpenAI-compatible types and structures while adding advanced features for RAG systems, tool calling, citations, and streaming events. It serves as the type foundation for all response handling in Knowledge Forge, with comprehensive TypeGuard functions for type-safe access to response data.

## Module Structure

```
response/
├── Core Utilities
│   ├── chat2response.py              # Chat to Response format conversion
│   ├── chat2response_enhanced.py     # Enhanced conversion with citations
│   ├── response2chat.py              # Response to Chat format conversion
│   ├── chat_input.py                 # Input processing utilities
│   ├── id_utils.py                   # ID generation and management
│   ├── citation_utils.py             # Citation processing utilities
│   ├── chunk_deduplicator.py         # Chunk deduplication logic
│   └── response_differ.py            # Response comparison utilities
├── Type Definitions (_types/)
│   ├── Core Types
│   │   ├── request.py                # Request structure
│   │   ├── response.py               # Response structure with citation methods
│   │   ├── response_status.py        # Status enumeration
│   │   └── response_usage.py         # Token usage tracking
├── Type Guards (type_guards/)
│   ├── __init__.py                   # Type guard exports
│   ├── output_items.py               # Output item type guards
│   ├── annotations.py                # Annotation type guards
│   └── events.py                     # Event type guards
│   ├── Tool Types
│   │   ├── file_search_tool*.py      # File search tool definitions
│   │   ├── web_search_tool*.py       # Web search tool definitions
│   │   ├── list_documents_tool*.py  # Document finder definitions
│   │   ├── function_tool*.py         # Function tool definitions
│   │   └── computer_tool*.py         # Computer use tool definitions
│   ├── Event Types
│   │   ├── response_*_event.py       # Streaming event definitions
│   │   └── response_stream_event.py  # Base streaming event
│   └── Content Types
│       ├── input_*.py                # Input content types
│       ├── response_output_*.py      # Output content types
│       └── response_reasoning_*.py   # Reasoning content types
├── Documentation
│   ├── README.md                     # Module overview
│   └── CHUNK_DEDUPLICATION_DESIGN.md # Deduplication design
└── Tests
    ├── test_response2chat.py         # Conversion tests
    └── chunk_deduplication_example.py # Deduplication examples
```

## Core Concepts

### Response API Design

The Response API provides:
- **OpenAI Compatibility**: Drop-in replacement for Chat Completion API
- **Streaming First**: Built for real-time interaction with SSE
- **Tool Integration**: Native support for multiple tool types
- **Citation Management**: Built-in citation tracking and formatting
- **Event System**: Rich events for UI updates and progress tracking

### Type System Architecture

```
Request → Processing → Response → Events
    ↓         ↓           ↓         ↓
  Tools    Services    Output    Stream
```

## Key Components

### Request Structure

The request encapsulates all input parameters:

**Core Fields:**
- `user` - User identifier
- `input` - List of input content (text, files, images)
- `instructions` - System instructions
- `tools` - Available tools for the request
- `model` - Model selection
- `stream` - Enable streaming

**Input Types:**
- `InputTextContent` - Text messages
- `InputFileContent` - File references
- `InputImageContent` - Image data

### Response Structure

The response contains all output data and chunk compression capabilities:

**Core Fields:**
- `id` - Unique response identifier
- `status` - Processing status
- `output` - List of output items (tool results, text, reasoning)
- `usage` - Token usage statistics
- `metadata` - Additional metadata

**Status Values:**
- `in_progress` - Currently processing
- `completed` - Successfully completed
- `failed` - Processing failed
- `incomplete` - Partial completion

**🆕 Chunk Compression Features:**
- Context optimization through three compression strategies
- Annotation-based reference tracking for citations
- Deep copy operations maintaining response immutability
- Magic method support for annotation equality comparisons

### Tool System

#### Built-in Tool Types

**File Search:**
- Search documents in vector stores
- Returns ranked results with scores
- Supports metadata filtering

**Web Search:**
- Search the web via Bing API
- Returns URLs with snippets
- Includes date and relevance

**List Documents:**
- Discover relevant documents
- Cross-collection search
- Document-level results

**Function Tool:**
- User-defined functions
- OpenAI-compatible schema
- External execution required

#### Tool Execution Flow

1. Tool specified in request
2. Internal tools executed automatically
3. External tools marked for user execution
4. Results included in response
5. Citations generated from results

### TypeGuard Functions

The response module provides comprehensive TypeGuard functions for type-safe access to response data:

#### Output Item TypeGuards

```python
from forge_cli.response.type_guards.output_items import (
    is_file_search_call, is_message_item, is_reasoning_item,
    is_web_search_call, is_function_call
)

# Type-safe access to output items
for item in response.output:
    if is_file_search_call(item):
        # Type checker knows item is ResponseFileSearchToolCall
        print(f"File search queries: {item.queries}")
        print(f"Status: {item.status}")
    elif is_message_item(item):
        # Type checker knows item is ResponseOutputMessage
        for content in item.content:
            if hasattr(content, 'text'):
                print(content.text)
```

#### Annotation TypeGuards

```python
from forge_cli.response.type_guards.annotations import (
    is_file_citation, is_url_citation, is_file_path
)

# Type-safe annotation processing
for annotation in message.annotations:
    if is_file_citation(annotation):
        print(f"File: {annotation.file_citation.file_id}")
    elif is_url_citation(annotation):
        print(f"URL: {annotation.url_citation.url}")
```

#### Event TypeGuards

```python
from forge_cli.response.type_guards.events import (
    is_text_delta_event, is_response_completed_event
)

# Type-safe event handling
if is_text_delta_event(event):
    print(event.text, end="")
elif is_response_completed_event(event):
    print("Response completed!")
```

### Event System

#### Event Categories

**Lifecycle Events:**
- `ResponseCreatedEvent` - Response initialized
- `ResponseInProgressEvent` - Processing started
- `ResponseCompletedEvent` - Processing finished
- `ResponseFailedEvent` - Error occurred

**Content Events:**
- `ResponseTextDeltaEvent` - Text chunk streamed
- `ResponseTextDoneEvent` - Text completed
- `ResponseOutputItemAddedEvent` - New output item
- `ResponseOutputItemDoneEvent` - Output completed

**Tool Events:**
- `Response*CallInProgressEvent` - Tool execution started
- `Response*CallSearchingEvent` - Tool searching
- `Response*CallCompletedEvent` - Tool finished

**Reasoning Events:**
- `ResponseReasoningSummaryTextDeltaEvent` - Reasoning chunk
- `ResponseReasoningSummaryTextDoneEvent` - Reasoning completed

### Citation System

#### Citation Management

The Response class provides citation methods:

```python
# Install citation IDs on all citable items
citable_items = response.install_citation_id()
# Returns items with sequential IDs (1, 2, 3...)

# Collect items without installing IDs
items = response.collect_citable_items()

# Check for external tool calls
if response.contain_non_internal_tool_call():
    # Has function calls needing external execution

# 🆕 Compress chunks to optimize context usage
compressed = response.compact_retrieve_chunks(mode="deduplicate")
# Remove unreferenced chunks for clean output
pruned = response.compact_retrieve_chunks(mode="nonrefed")
# Compress all content for extreme token reduction
minimal = response.compact_retrieve_chunks(mode="all")

# 🆕 Remove duplicate results across tool calls
stats = response.compact()
deduped_response = stats["response"]
# Or use the convenience method
deduped = response.deduplicate()

# 🆕 Get referenced citations from actual usage
referenced_citations = response.get_refed_citations()
# Get all potential citations from tool results
all_citations = response.get_candidator_citations()
```

#### Citation Support

Tool results support citation IDs:

```python
# Web search results
result.citation_id  # Property getter
result.set_citation_id("1")  # Method setter

# File search results
result.citation_id = "2"  # Property setter

# Chunks from tools
chunk.citation_id = "3"
```

## Conversion Utilities

### Response ↔ Chat Format

**Response to Chat:**
```python
from response.response2chat import response_to_chat_completion

# Convert with chunk formatting
chat_completion = response_to_chat_completion(
    response,
    context=context,
    include_reasoning=False
)
```

**Chat to Response:**
```python
from response.chat2response import chat_to_response

response = chat_to_response(
    chat_completion,
    preserve_citations=True
)
```

### Enhanced Conversion

The enhanced converter handles:
- Citation preservation
- Tool call mapping
- Chunk formatting
- Metadata transfer

## Status Code Conventions

### Tool-Specific Status Codes (ADR-007)

Each tool type has specific status progressions:

**File Search:**
- `in_progress` → `searching` → `completed`/`incomplete`

**Web Search:**
- `in_progress` → `searching` → `completed`/`failed`

**Function Tool:**
- `in_progress` → `completed`/`incomplete`

**Error Status Mapping:**
```python
def error_status(tool_type: str) -> str:
    if tool_type == "web_search":
        return "failed"
    return "incomplete"
```

## Usage Patterns

### Creating Requests

Build requests with tools:

```python
request = Request(
    user="user-123",
    input=[
        InputTextContent(text="What is RAG?")
    ],
    tools=[
        FileSearchTool(
            file_search=FileSearchToolParam(
                vector_store_ids=["vs_123"],
                max_num_results=10
            )
        )
    ],
    stream=True
)
```

### Processing Responses

Handle response with citations:

```python
# Process response
response = await service.generate_response(request)

# Install citations
citable_items = response.install_citation_id()

# Format for output
formatted = response_to_chat_completion(response)
```

### Streaming Events

Process streaming events:

```python
async for event in event_stream:
    if isinstance(event, ResponseTextDeltaEvent):
        print(event.text, end="")
    elif isinstance(event, ResponseCompletedEvent):
        break
```

## Best Practices

1. **Status Management**: Always update status correctly
2. **Event Ordering**: Emit events in proper sequence
3. **Citation Tracking**: Install citation IDs before formatting
4. **Error Handling**: Use appropriate error status codes
5. **Type Safety**: Use proper type definitions
6. **Streaming**: Handle partial results gracefully

## Common Patterns

### Tool Result Processing with TypeGuards

```python
from forge_cli.response.type_guards.output_items import (
    is_file_search_call, is_web_search_call, is_message_item
)

# Type-safe tool result processing
for item in response.output:
    if is_file_search_call(item):
        # Type checker knows item is ResponseFileSearchToolCall
        print(f"File search completed: {len(item.queries)} queries")
        print(f"Status: {item.status}")
        # File search results are accessed through response methods
        # results = response.get_file_search_results(item.id)
    elif is_web_search_call(item):
        # Type checker knows item is ResponseFunctionWebSearch
        print(f"Web search completed: {item.queries}")
    elif is_message_item(item):
        # Type checker knows item is ResponseOutputMessage
        for content in item.content:
            if hasattr(content, 'text'):
                print(f"Message: {content.text}")
```

### Event Emission

```python
# Proper event sequence
await emit(ResponseCreatedEvent(response))
await emit(ResponseInProgressEvent(response))

# Stream content
for chunk in content_generator:
    await emit(ResponseTextDeltaEvent(text=chunk))

# Complete
await emit(ResponseCompletedEvent(response))
```

### Error Recovery

```python
try:
    response = await process_request(request)
except ToolError as e:
    response.status = "failed"
    response.error = ResponseError(
        type="tool_error",
        message=str(e)
    )
    await emit(ResponseFailedEvent(response))
```

## Integration Points

### With API Layer
- APIs use these types for request/response
- Event types for SSE streaming
- Status codes for progress tracking

### With Service Layer
- Services populate response objects
- Tool execution updates status
- Citation installation before output

### With Citation Module
- Citation IDs assigned to results
- Formatting applied during streaming
- Unicode symbols replace markers

## Related ADRs

### Core Design
- **ADR-001**: Response API Architecture
- **ADR-012**: API Conversion Design
- **ADR-014**: Response to Chat Conversion
- **ADR-046**: ChatCompletionChunk Field Extension

### Tool System
- **ADR-007**: Tool Response Status Codes
- **ADR-008**: Tool Call Event Types
- **ADR-043**: Type-Based Tool Call Detection

### Citation System
- **ADR-011**: Citation Design for RAG System
- **ADR-027**: Chunk Formatting with Citation ID
- **ADR-033**: Enhanced Multi-Tool Citation System
- **ADR-040**: Citation ID Management
- 🆕 **ADR-071**: Citation Display vs Reference ID Separation

### Chunk Management & Compression
- 🆕 **ADR-072**: Response Chunk Compression Strategies for Context Optimization

### Streaming
- **ADR-002**: Client Disconnect Handling
- **ADR-003**: Stop Event Mechanism
- **ADR-004**: Enhanced Disconnect Detection
- **ADR-005**: Hierarchical RAG Stop Event

## Performance Considerations

1. **Type Creation**: Use factories for complex types
2. **Event Batching**: Group related events
3. **Memory Management**: Stream large responses
4. **Serialization**: Cache serialized formats
5. **Validation**: Validate early in pipeline

## Testing

- Type validation tests
- Conversion round-trip tests
- Event sequence validation
- Status progression tests
- Citation installation tests