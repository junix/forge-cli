# Migration Status: Dict-based to Typed API

## Overview

This document tracks the migration progress from the legacy dict-based `astream_response` API to the new type-safe `astream_typed_response` API.

## Migration Goals

1. **Type Safety**: Use Pydantic Response objects instead of dicts
2. **Better IDE Support**: Full autocomplete and type checking
3. **Backward Compatibility**: Support both APIs during transition
4. **Gradual Migration**: Module-by-module approach

## Completed Migrations

### Core SDK (`sdk.py`)
- ✅ Fixed `astream_typed_response` to yield Response objects
- ✅ Added ResponseAdapter for dict-to-Response conversion
- ✅ Proper parameter mapping between Request and astream_response

### Migration Infrastructure (`response/adapters.py`)
- ✅ Created MigrationHelper with safe accessor methods
- ✅ Type detection utilities (is_typed_response, is_typed_item)
- ✅ Safe text extraction (safe_get_text)
- ✅ Safe output access (safe_get_output_items)

### Scripts
- ✅ `hello-async.py` - Migrated to typed API with compatibility
- ✅ `hello-file-search-typed.py` - Full typed example with tools
- ✅ `hello-file-search-typed-v2.py` - Uses TypedStreamHandler

### Stream Handling (`stream/handler_typed.py`)
- ✅ TypedStreamHandler supports both dict and Response
- ✅ StreamState works with both APIs
- ✅ Tool state management for both formats
- ✅ Event extraction utilities

### Processors
- ✅ `base_typed.py` - Base classes for typed processors
- ✅ `message.py` - Already supports both dict and typed
- ✅ `reasoning.py` - Already supports both dict and typed
- ✅ `registry_typed.py` - Registry supporting both processor types
- ✅ `tool_calls/base_typed.py` - Base for typed tool processors
- ✅ `tool_calls/file_search_typed.py` - Typed file search processor
- ✅ `tool_calls/web_search_typed.py` - Typed web search processor

### Main Entry Points
- ✅ `main_typed.py` - Basic typed API support
- ✅ `main_typed_v2.py` - Full typed support with TypedStreamHandler

## Pending Migrations

### Scripts
- ⏳ `hello-web-search.py`
- ⏳ `hello-file-reader.py`
- ⏳ `simple-flow.py`
- ⏳ Other utility scripts

### Core Modules
- ⏳ `main.py` - Update to use typed components
- ⏳ `stream/handler.py` - Update to use handler_typed.py
- ⏳ `chat/controller.py` - Add typed API support

### Processors
- ⏳ `tool_calls/file_reader.py` - Create typed version
- ⏳ `tool_calls/document_finder.py` - Create typed version

### Display Components
- ⏳ Update display strategies to better support typed items

## Migration Pattern

### For Scripts

```python
# Old pattern
async for event_type, event_data in astream_response(...):
    if event_type == "response.output_text.delta":
        text = event_data.get("text", "")

# New pattern
from forge_cli.response.adapters import MigrationHelper

async for event_type, event_data in astream_typed_response(request):
    if event_type == "response.output_text.delta":
        text = MigrationHelper.safe_get_text(event_data)
```

### For Processors

```python
# Support both dict and typed items
def process(self, item: Any) -> dict[str, Any] | None:
    # Handle typed event
    if isinstance(item, ResponseOutputMessage):
        # Process typed object
        return {"text": item.output_text}
    
    # Handle dict for backward compatibility
    elif isinstance(item, dict):
        # Process dict
        return {"text": item.get("text", "")}
```

### For Stream Handlers

```python
# Use TypedStreamHandler which supports both
from forge_cli.stream.handler_typed import TypedStreamHandler

handler = TypedStreamHandler(display, debug=True)
state = await handler.handle_stream(stream, query)
```

## Testing Strategy

1. **Dual Testing**: Test each component with both APIs
2. **Compatibility Tests**: Ensure old code works with new infrastructure
3. **Type Tests**: Verify type annotations are correct
4. **Integration Tests**: Full end-to-end with typed API

## Benefits Achieved

1. **Type Safety**: Full type checking with mypy
2. **IDE Support**: Autocomplete for all Response properties
3. **Error Prevention**: Catch type errors at development time
4. **Maintainability**: Clearer interfaces and contracts
5. **Gradual Migration**: No breaking changes, smooth transition

## Next Steps

1. Continue migrating remaining scripts
2. Update main.py to use typed components by default
3. Add typed API option to chat controller
4. Create typed versions of remaining tool processors
5. Update documentation with typed examples
6. Consider deprecation timeline for dict-based API