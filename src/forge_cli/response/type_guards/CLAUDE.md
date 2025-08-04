# Type Guards - Safe Type Narrowing Functions

## Overview

The type guards module provides TypeGuard functions that enable safe type narrowing for Response API objects. These functions eliminate the need for defensive programming patterns and provide type-safe access to API response data with full IDE support. This implementation follows ADR-010 (Response Type Guards) design principles.

## Directory Structure

```
type_guards/
├── CLAUDE.md                    # This documentation file
├── __init__.py                  # TypeGuard exports and public API
├── annotations.py               # Citation and annotation type guards
├── content.py                   # Content type guards
├── events.py                    # Streaming event type guards
├── input_content.py             # Input content type guards
├── output_items.py              # Output item type guards
├── status.py                    # Status and state type guards
├── tools.py                     # Tool definition type guards
└── utilities.py                 # Helper functions and utilities
```

## Architecture & Design

### Design Principles (ADR-010)

1. **Type Safety**: Proper type narrowing ensures compile-time and runtime safety
2. **IDE Support**: Full autocomplete and type hints within conditional blocks
3. **Code Clarity**: Intent is clear - checking type, not defensive programming
4. **Performance**: Simple string comparison, no runtime overhead
5. **Maintainability**: Centralized type checking logic

### TypeGuard Benefits

**Compared to Defensive Programming:**

```python
# ❌ BAD: Defensive programming patterns
if hasattr(item, "queries") and item.queries:  # No type information
    for query in item.queries:  # No autocomplete
        process_query(query)

# ✅ GOOD: Using TypeGuard functions
from forge_cli.response.type_guards.output_items import is_file_search_call

if is_file_search_call(item):
    # Type checker knows item is ResponseFileSearchToolCall
    for query in item.queries:  # Full autocomplete!
        process_query(query)
```

## Core TypeGuard Modules

### output_items.py - Output Item Type Guards

Provides type guards for all response output items:

**Message and Content Guards:**

- `is_message_item()` - ResponseOutputMessage detection
- `is_reasoning_item()` - ResponseReasoningItem detection
- `is_output_text()` - ResponseOutputText detection
- `is_output_refusal()` - ResponseOutputRefusal detection

**Tool Call Guards:**

- `is_file_search_call()` - ResponseFileSearchToolCall detection
- `is_web_search_call()` - ResponseFunctionWebSearch detection
- `is_function_call()` - ResponseFunctionToolCall detection
- `is_computer_call()` - ResponseComputerToolCall detection
- `is_list_documents_call()` - ResponseListDocumentsToolCall detection
- `is_file_reader_call()` - ResponseFunctionFileReader detection
- `is_page_reader_call()` - ResponseFunctionPageReader detection
- `is_code_interpreter_call()` - ResponseCodeInterpreterToolCall detection

**Usage Example:**

```python
from forge_cli.response.type_guards.output_items import (
    is_file_search_call, is_message_item, is_reasoning_item
)

def process_output_items(items: list[ResponseOutputItem]) -> None:
    for item in items:
        if is_file_search_call(item):
            # Type checker knows item is ResponseFileSearchToolCall
            print(f"File search queries: {item.queries}")
            print(f"Status: {item.status}")
        elif is_message_item(item):
            # Type checker knows item is ResponseOutputMessage
            print(f"Message: {item.content}")
        elif is_reasoning_item(item):
            # Type checker knows item is ResponseReasoningItem
            print(f"Reasoning: {item.content}")
```

### annotations.py - Citation Type Guards

Provides type guards for citation and annotation types:

**Citation Guards:**

- `is_file_citation()` - AnnotationFileCitation detection
- `is_url_citation()` - AnnotationURLCitation detection
- `is_file_path()` - AnnotationFilePath detection

**Usage Example:**

```python
from forge_cli.response.type_guards.annotations import is_file_citation, is_url_citation

def process_annotations(annotations: list[Annotation]) -> None:
    for annotation in annotations:
        if is_file_citation(annotation):
            # Type checker knows annotation has file_citation
            print(f"File: {annotation.file_citation.file_name}")
            print(f"Quote: {annotation.file_citation.quote}")
        elif is_url_citation(annotation):
            # Type checker knows annotation has url_citation
            print(f"URL: {annotation.url_citation.url}")
            print(f"Title: {annotation.url_citation.title}")
```

### events.py - Streaming Event Type Guards

Provides type guards for streaming event types:

**Core Event Guards:**

- `is_text_delta_event()` - ResponseTextDeltaEvent detection
- `is_response_completed_event()` - ResponseCompletedEvent detection
- `is_response_error_event()` - ResponseErrorEvent detection
- `is_output_item_added_event()` - ResponseOutputItemAddedEvent detection

**Tool Event Guards:**

- `is_file_search_completed_event()` - File search completion events
- `is_web_search_searching_event()` - Web search progress events
- `is_function_call_arguments_delta_event()` - Function call updates

**Usage Example:**

```python
from forge_cli.response.type_guards.events import (
    is_text_delta_event, is_response_completed_event
)

def process_stream_event(event: ResponseStreamEvent) -> None:
    if is_text_delta_event(event):
        # Type checker knows event is ResponseTextDeltaEvent
        print(event.delta, end="", flush=True)
    elif is_response_completed_event(event):
        # Type checker knows event is ResponseCompletedEvent
        print(f"\nResponse completed: {event.response.id}")
```

### content.py - Content Type Guards

Provides type guards for content types:

**Content Guards:**

- `is_text_content()` - Text content detection
- `is_image_content()` - Image content detection
- `is_file_content()` - File content detection

### tools.py - Tool Definition Type Guards

Provides type guards for tool definition types:

**Tool Guards:**

- `is_file_search_tool()` - FileSearchTool detection
- `is_web_search_tool()` - WebSearchTool detection
- `is_function_tool()` - FunctionTool detection
- `is_computer_tool()` - ComputerTool detection

### utilities.py - Helper Functions

Provides utility functions that work with TypeGuards:

**Helper Functions:**

- `get_tool_queries()` - Extract queries from tool calls
- `get_tool_results()` - Extract results from completed tools
- `get_tool_content()` - Extract content from tool outputs
- `collect_citations()` - Collect all citations from response
- `filter_by_status()` - Filter tool calls by status

**Usage Example:**

```python
from forge_cli.response.type_guards.utilities import get_tool_queries, collect_citations

def analyze_response(response: Response) -> dict:
    """Analyze response using utility functions."""
    return {
        'queries': get_tool_queries(response.output),
        'citations': collect_citations(response.output),
        'tool_count': len([item for item in response.output if is_tool_call(item)])
    }
```

## Implementation Patterns

### TypeGuard Function Structure

```python
from typing import TypeGuard
from forge_cli.response._types.response import ResponseOutputItem, ResponseFileSearchToolCall

def is_file_search_call(item: ResponseOutputItem) -> TypeGuard[ResponseFileSearchToolCall]:
    """Check if item is a file search tool call.
    
    Args:
        item: Response output item to check
        
    Returns:
        True if item is ResponseFileSearchToolCall, False otherwise
        
    Example:
        >>> if is_file_search_call(item):
        ...     # Type checker knows item is ResponseFileSearchToolCall
        ...     print(f"Queries: {item.queries}")
    """
    return hasattr(item, 'type') and item.type == "file_search_call"
```

### Compound Type Guards

```python
def is_tool_call(item: ResponseOutputItem) -> TypeGuard[
    ResponseFileSearchToolCall | ResponseFunctionWebSearch | ResponseFunctionToolCall
]:
    """Check if item is any type of tool call."""
    return (
        is_file_search_call(item) or
        is_web_search_call(item) or
        is_function_call(item) or
        is_computer_call(item) or
        is_list_documents_call(item)
    )

def is_completed_tool_call(item: ResponseOutputItem) -> bool:
    """Check if item is a completed tool call."""
    return is_tool_call(item) and getattr(item, 'status', None) == 'completed'
```

### Status-Based Guards

```python
from forge_cli.response.type_guards.status import is_completed, is_in_progress, is_failed

def process_tool_by_status(item: ResponseOutputItem) -> None:
    """Process tool call based on its status."""
    if is_tool_call(item):
        if is_completed(item):
            print(f"Tool {item.id} completed successfully")
        elif is_in_progress(item):
            print(f"Tool {item.id} is still running")
        elif is_failed(item):
            print(f"Tool {item.id} failed")
```

## Usage Guidelines

### Best Practices

1. **Use TypeGuards First**: Always prefer TypeGuards over hasattr() checks
2. **Import Specifically**: Import only the guards you need
3. **Combine Guards**: Use compound guards for complex type checking
4. **Handle All Cases**: Use exhaustive pattern matching when possible
5. **Document Usage**: Include examples in docstrings

### Performance Considerations

1. **Efficient Checks**: TypeGuards use simple string comparisons
2. **No Runtime Overhead**: Type checking is optimized by Python
3. **Lazy Evaluation**: Use short-circuit evaluation in compound guards
4. **Cache Results**: Cache guard results for repeated checks

### Error Handling

```python
def safe_process_item(item: ResponseOutputItem) -> None:
    """Safely process output item with error handling."""
    try:
        if is_file_search_call(item):
            process_file_search(item)
        elif is_message_item(item):
            process_message(item)
        else:
            logger.warning(f"Unknown item type: {getattr(item, 'type', 'unknown')}")
    except Exception as e:
        logger.error(f"Error processing item: {e}")
```

## Related Components

- **Response Types** (`../_types/`) - Types that TypeGuards check
- **SDK** (`../../sdk/`) - Uses TypeGuards for response processing
- **Display** (`../../display/`) - Uses TypeGuards for rendering decisions
- **Stream Handler** (`../../stream/`) - Uses TypeGuards for event processing

## Best Practices

### TypeGuard Design

1. **Simple Checks**: Use simple, fast type identification
2. **Clear Names**: Use descriptive function names
3. **Comprehensive Coverage**: Cover all important type distinctions
4. **Documentation**: Include usage examples and type information
5. **Testing**: Test all TypeGuard functions thoroughly

### Integration

1. **Centralized Imports**: Import from type_guards module
2. **Consistent Usage**: Use TypeGuards consistently across codebase
3. **Type Safety**: Leverage full type safety benefits
4. **IDE Support**: Take advantage of autocomplete and type hints
5. **Maintainability**: Keep TypeGuard logic centralized and testable

The type guards module provides the foundation for type-safe, maintainable code throughout the Forge CLI application, eliminating defensive programming patterns while ensuring robust type checking.
