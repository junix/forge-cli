# ADR-010: Type Guards for Response Output Items

Date: 2024-01-15
Status: Accepted

## Context

The Knowledge Forge Response API returns a discriminated union of output items in the `response.output` array. Each item has a `type` field that determines its actual type:

- `"message"` → `ResponseOutputMessage`
- `"reasoning"` → `ResponseReasoningItem`
- `"file_search_call"` → `ResponseFileSearchToolCall`
- `"web_search_call"` → `ResponseFunctionWebSearch`
- `"list_documents_call"` → `ResponseListDocumentsToolCall`
- `"file_reader_call"` → `ResponseFunctionFileReader`
- `"code_interpreter_call"` → `ResponseCodeInterpreterToolCall`
- `"function_call"` → `ResponseFunctionToolCall`
- `"computer_tool_call"` → `ResponseComputerToolCall`

Previously, code handling these items used various approaches:
1. **String comparison with cast**: `if item.type == "file_search_call": file_search = cast(ResponseFileSearchToolCall, item)`
2. **Defensive hasattr checks**: `if hasattr(item, "queries") and item.queries:`
3. **Generic Any typing**: Lost all type safety benefits

These approaches had several problems:
- Type checkers couldn't narrow types properly
- No IDE autocomplete support within conditional blocks
- Runtime safety concerns with cast (assertion without verification)
- Defensive programming with hasattr made code verbose and unclear

## Decision

We will implement TypeGuard functions for all Response output item types and place them in `response/type_guards.py`. These guards will:

1. **Provide proper type narrowing** using Python's TypeGuard protocol
2. **Enable IDE support** with full autocomplete and type hints
3. **Centralize type checking** logic in one reusable module
4. **Follow discriminated union** patterns properly

Example implementation:
```python
from typing import TypeGuard

def is_file_search_call(item: ResponseOutputItem) -> TypeGuard[ResponseFileSearchToolCall]:
    """Check if output item is a file search tool call."""
    return item.type == "file_search_call"
```

Usage pattern:
```python
# Type narrowing with full IDE support
if is_file_search_call(item):
    # Type checker knows item is ResponseFileSearchToolCall
    for query in item.queries:  # Full autocomplete!
        process_query(query)
```

## Consequences

### Positive

1. **Type Safety**: Proper type narrowing ensures compile-time and runtime safety
2. **Developer Experience**: Full IDE support with autocomplete, go-to-definition, and refactoring
3. **Code Clarity**: Intent is clear - checking type, not defensive programming
4. **Reusability**: Type guards available to all modules via `forge_cli.response.type_guards`
5. **Maintainability**: Changes to types automatically flow through type system
6. **Performance**: Simple string comparison, no runtime overhead vs other approaches

### Negative

1. **Additional Module**: One more file to maintain (but centralizes related logic)
2. **Import Requirements**: Must import type guards to use them
3. **Learning Curve**: Developers need to know about type guards pattern

### Neutral

1. **Python 3.10+ Feature**: TypeGuard requires modern Python (project already requires 3.8+)
2. **Static Analysis**: Benefits mainly visible with type checkers enabled

## Implementation Details

The `response/type_guards.py` module provides:

### Type Guards for Output Items
- `is_message_item()` → `ResponseOutputMessage`
- `is_reasoning_item()` → `ResponseReasoningItem`
- `is_file_search_call()` → `ResponseFileSearchToolCall`
- `is_web_search_call()` → `ResponseFunctionWebSearch`
- `is_list_documents_call()` → `ResponseListDocumentsToolCall`
- `is_file_reader_call()` → `ResponseFunctionFileReader`
- `is_code_interpreter_call()` → `ResponseCodeInterpreterToolCall`
- `is_function_call()` → `ResponseFunctionToolCall`
- `is_computer_tool_call()` → `ResponseComputerToolCall`

### Type Guards for Annotations
- `is_file_citation()` → `AnnotationFileCitation`
- `is_url_citation()` → `AnnotationURLCitation`
- `is_file_path()` → `AnnotationFilePath`

### Helper Functions
- `get_tool_queries()` - Extract queries from any tool type
- `get_tool_results()` - Extract results from any tool type
- `get_tool_content()` - Extract content from tools that have it
- `get_tool_output()` - Extract output from tools that have it
- `get_tool_function_name()` - Extract function name from function calls
- `get_tool_arguments()` - Extract arguments from function calls

## Examples

### Before (with cast)
```python
from typing import cast

def process_tool(item: ResponseOutputItem):
    if item.type == "file_search_call":
        file_search = cast(ResponseFileSearchToolCall, item)
        # No actual type checking, just assertion
        queries = file_search.queries  # Could fail at runtime
```

### Before (with hasattr)
```python
def process_tool(item: Any):  # Lost type info!
    if hasattr(item, "queries") and item.queries:
        # Defensive but unclear intent
        for query in item.queries:  # No type hints
            print(query)
```

### After (with type guards)
```python
from forge_cli.response.type_guards import is_file_search_call

def process_tool(item: ResponseOutputItem):
    if is_file_search_call(item):
        # Type checker knows item is ResponseFileSearchToolCall
        for query in item.queries:  # Full type support!
            print(f"Searching: {query}")
        
        # Access all type-specific attributes safely
        if item.status == "completed" and item.results:
            return process_results(item.results)
```

## Migration Guide

To migrate existing code:

1. **Remove cast imports**: Delete `from typing import cast`
2. **Remove type-specific imports**: No need to import individual tool types
3. **Import type guards**: `from forge_cli.response.type_guards import is_*`
4. **Replace conditionals**:
   - `if item.type == "x":` → `if is_x(item):`
   - `cast(TypeX, item)` → Remove cast, use item directly
   - `hasattr(item, "attr")` → Access item.attr directly after guard

## Related ADRs

- **ADR-004**: Snapshot-based streaming design (establishes Response object pattern)
- **ADR-011**: Citation design for RAG system (uses type guards for annotations)
- **ADR-043**: Type-based tool call detection (motivation for type safety)

## References

- [PEP 647 - User-Defined Type Guards](https://www.python.org/dev/peps/pep-0647/)
- [TypeScript Type Guards](https://www.typescriptlang.org/docs/handbook/2/narrowing.html) (similar concept)
- [Discriminated Unions in Python](https://docs.pydantic.dev/latest/usage/types/unions/#discriminated-unions)