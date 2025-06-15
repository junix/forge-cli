# ADR-005: Response API Type System Architecture

**Status:** Active *(Updated for Typed-Only Architecture)*  
**Date:** 2025-06-14 *(Updated: 2025-06-15)*  
**Deciders:** Development Team  
**Technical Story:** Comprehensive type system for Knowledge Forge Response API  
**Updated By:** ADR-007 (Typed-Only Architecture Migration)

## Context

The Knowledge Forge Response API requires a sophisticated type system to handle:
- AI model responses with streaming capabilities
- Multiple tool integrations (file search, web search, document finder, etc.)
- Citation management and annotation tracking
- OpenAI API compatibility while extending functionality
- Real-time event-driven updates for UI components
- Type safety and validation across complex data structures

The system must support both synchronous and streaming modes while maintaining OpenAI API compatibility.

> **🔄 Update (2025-06-15)**: Following ADR-007, the system now uses **typed-only architecture**. All dict-based legacy APIs and adapter classes have been removed for improved type safety and performance.

## Decision

We implement a comprehensive, event-driven type system organized around the following architectural principles:

### 1. Hierarchical Type Organization

```
response/
├── _types/                    # Core type definitions
│   ├── response.py           # Central Response class
│   ├── request.py            # Request parameters
│   ├── parsed_response.py    # Generic structured output
│   ├── response_*_event.py   # 25+ streaming event types  
│   ├── response_*_tool_call.py # Tool integration types
│   ├── annotations.py        # Citation management
│   └── input_*.py           # Input validation models
├── chat2response.py         # Format conversion utilities
├── chat_input.py           # Chat-specific input handling
└── id_utils.py             # ID generation and validation
```

### 2. Core Type System Components

#### A. Response Class (Central Hub)
The `Response` class serves as the primary data structure with:
- **Citation Management**: Automatic installation and tracking of file/URL citations
- **Chunk Compression**: Three modes ("all", "deduplicate", "nonrefed") for context optimization
- **Tool Integration**: Unified handling of multiple tool types with result processing
- **OpenAI Compatibility**: Drop-in replacement for chat completion responses

```python
class Response(BaseModel):
    # Core response data
    id: str
    status: ResponseStatus
    output: List[ResponseOutputItem]
    
    # Advanced features
    chunks: List[Chunk]  # Tool results with citations
    tool_calls: List[ResponseToolCall]  # Executed tools
    annotations: List[ResponseAnnotation]  # Citation tracking
    
    # Methods for processing and optimization
    def install_citations(self) -> 'Response'
    def compress_chunks(self, mode: Literal["all", "deduplicate", "nonrefed"])
    def to_chat_completion(self) -> ChatCompletion
```

#### B. Tool Integration System
Unified interface for multiple tool types:

- **FileSearchTool**: Vector store document search with citation tracking
- **WebSearchTool**: Internet search with result structuring  
- **DocumentFinderTool**: Document discovery across collections
- **FunctionTool**: User-defined function calls (OpenAI compatible)
- **ComputerTool**: Computer use capabilities (screenshot, automation)
- **FileReaderTool**: Direct file content access

Each tool implements:
```python
class ResponseToolCall(BaseModel):
    def from_chat_tool_call(cls, tool_call) -> 'ResponseToolCall'
    def to_chat_tool_call(self) -> ChatCompletionMessageToolCall
    def chunkify(self) -> List[Chunk]  # Convert results to unified format
```

#### C. Event-Driven Streaming Architecture
Comprehensive event system with 25+ event types:

**Lifecycle Events:**
- `ResponseCreatedEvent`, `ResponseInProgressEvent`, `ResponseCompletedEvent`

**Content Streaming Events:**  
- `ResponseTextDeltaEvent`, `ResponseOutputItemAddedEvent`

**Tool Execution Events:**
- `ResponseFileSearchCallSearchingEvent`, `ResponseFileSearchCallCompletedEvent`
- `ResponseWebSearchCallSearchingEvent`, `ResponseWebSearchCallCompletedEvent`

**Reasoning Events:**
- `ResponseOutputItemAddedEvent` (for thinking/reasoning content)

#### D. Citation and Annotation Management
Sophisticated citation system with:

```python
class AnnotationFileCitation(BaseModel):
    file_id: str
    page_number: Optional[int]
    document_position: Optional[int]  # Not just display ID
    
    def __eq__(self, other) -> bool  # Enables deduplication
    def __hash__(self) -> int        # Set operations support

class AnnotationURLCitation(BaseModel):
    url: str
    title: Optional[str]
    metadata: Dict[str, Any]
```

**Features:**
- Automatic citation ID installation across tool results
- Cross-tool deduplication using annotation equality
- Referenced vs candidate citation tracking
- Document position-based annotations (not display-only)

### 3. Design Patterns and Principles

#### A. Type Safety and Validation
- **Pydantic v2**: Comprehensive data validation and serialization
- **Literal Types**: Controlled vocabularies for status codes, event types
- **Union Types**: Polymorphic structures with discriminators
- **Generic Types**: Reusable patterns like `ParsedResponse[T]`

#### B. Event-Driven Architecture
```
API Event Stream → StreamHandler → Event Router → Processor Registry → Display Strategy
```

**Status Progression (per ADR-007):**
- File Search: `in_progress` → `searching` → `completed`/`incomplete`
- Web Search: `in_progress` → `searching` → `completed`/`failed`  
- Function Tools: `in_progress` → `completed`/`incomplete`

#### C. Bidirectional Compatibility
- **Chat ↔ Response**: Full-fidelity format conversion
- **OpenAI Compatibility**: Maintains API compatibility while extending functionality
- **Message Folding**: Conversation management with validation

#### D. Context Optimization Strategies
The Response class provides chunk compression modes:

1. **"all"**: Compress all content to reduce token usage
2. **"deduplicate"**: Remove duplicate results across tool calls  
3. **"nonrefed"**: Remove unreferenced chunks based on actual usage

### 4. Tool Call Processing Pipeline

```python
# Internal tool execution flow
1. Request.tool_calls → [ResponseToolCall] (validation)
2. Tool execution → Results + Status events
3. Results.chunkify() → [Chunk] (unified format)
4. Chunk.as_annotation() → Citations (if applicable)
5. Response.install_citations() → Final response with references
```

### 5. Input/Output Model Architecture

**Input Models:**
- `InputMessage`: Structured message with content validation
- `ResponseCreateParams`: Request parameters with tool selection
- `EasyInputMessage`: Simplified interface for common use cases

**Output Models:**
- `ResponseOutputMessage`: Final assistant response
- `ResponseOutputText`: Text content with annotation support  
- `ResponseReasoningItem`: Reasoning/thinking content from advanced models

## Rationale

### Why This Architecture?

1. **Type Safety**: Prevents runtime errors through comprehensive validation
2. **Extensibility**: Plugin architecture supports new tool types without core changes
3. **Performance**: Streaming architecture with context optimization reduces latency
4. **Compatibility**: Maintains OpenAI API compatibility while adding enterprise features
5. **Citation Management**: Advanced reference tracking exceeds typical RAG implementations
6. **Real-time Updates**: Event-driven system enables rich UI experiences

### Key Design Decisions

#### Event-Driven vs Request-Response
**Chosen**: Event-driven streaming architecture  
**Alternative**: Traditional request-response  
**Reason**: Enables real-time UI updates, progress tracking, and better user experience for long-running operations

#### Unified Tool Interface vs Tool-Specific APIs  
**Chosen**: Unified interface with tool-specific implementations  
**Alternative**: Separate APIs per tool type  
**Reason**: Consistent processing pipeline, easier testing, and simplified client code

#### Citation Installation vs Lazy Loading
**Chosen**: Explicit citation installation with caching  
**Alternative**: Lazy loading of citations  
**Reason**: Predictable behavior, better performance for batch operations, and clearer API

#### Pydantic v2 vs Custom Validation
**Chosen**: Pydantic v2 for all data structures  
**Alternative**: Custom validation classes  
**Reason**: Industry standard, excellent error messages, automatic serialization, and IDE support

## Consequences

### Positive
- **Type Safety**: Comprehensive validation prevents runtime errors
- **Developer Experience**: Rich IDE support with auto-completion and type checking
- **Maintainability**: Clear separation of concerns and consistent patterns
- **Performance**: Streaming architecture with context optimization
- **Extensibility**: Easy to add new tool types and display strategies
- **Citation Quality**: Advanced reference tracking exceeds typical implementations

### Negative  
- **Complexity**: Large number of types requires learning curve
- **Memory Usage**: Rich object models consume more memory than primitive types
- **Compilation Time**: Extensive type checking may slow development iteration

### Risk Mitigation
- **Documentation**: Comprehensive ADRs and inline documentation
- **Examples**: Rich set of example scripts demonstrating usage patterns  
- **Testing**: Type-driven testing ensures validation coverage
- **Performance Monitoring**: Chunk compression and streaming reduce memory impact

## Implementation Notes

### Critical Type Relationships
```python
Request → Response → ParsedResponse[T]  # Core flow
ToolCall → Chunk → Annotation  # Tool result processing  
Event → Processor → Display  # Streaming pipeline
```

### Validation Strategy
- **Fail-Fast**: Invalid data causes immediate exceptions rather than silent failures
- **Rich Errors**: Pydantic provides detailed error messages with field-level validation
- **Runtime Safety**: All external data validated at API boundaries

### Extension Points
- **New Tool Types**: Implement `ResponseToolCall` interface
- **Custom Processors**: Register in processor registry  
- **Display Strategies**: Implement base display interface
- **Event Handlers**: Subscribe to event types in stream handler

## Related ADRs

- **ADR-002**: Reasoning Event Handling in Streaming
- **ADR-003**: File Search Citation Display Architecture  
- **ADR-004**: Snapshot-Based Streaming Design
- **ADR-007**: Tool Call Status Progression Design

## Future Considerations

1. **GraphQL Integration**: Type system could support GraphQL schema generation
2. **OpenAPI Specification**: Automatic API documentation from type definitions
3. **Multi-Model Support**: Type system extensible for different AI providers
4. **Caching Layer**: Response objects suitable for caching and persistence
5. **Batch Processing**: Type system supports batch operations for efficiency