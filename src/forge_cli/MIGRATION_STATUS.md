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

### Migration Infrastructure
- ✅ `response/adapters.pyi` - Type stubs for adapters
- ✅ `response/migration_helpers.py` - Comprehensive migration utilities
  - Type detection (is_typed_response, is_typed_item)
  - Safe accessors (safe_get_text, safe_get_type, safe_get_status)
  - Result extraction (safe_get_results, safe_get_output_items)
  - Tool helpers (convert_tool_to_typed, extract_tool_id)
  - Message conversion (convert_message_to_typed)

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
- ✅ `tool_calls/document_finder_typed.py` - Typed document finder processor
- ✅ `tool_calls/file_reader_typed.py` - Typed file reader processor

### Main Entry Points
- ✅ `main_typed.py` - Basic typed API support
- ✅ `main_typed_v2.py` - Full typed support with TypedStreamHandler

## Pending Migrations

### Scripts
- ✅ `hello-typed-example.py` - Comprehensive typed API examples
- ✅ `migration-example.py` - Migration guide with comparisons
- ⏳ `hello-web-search.py` - To be updated
- ⏳ `hello-file-reader.py` - To be updated
- ⏳ `simple-flow.py` - To be updated
- ⏳ Other utility scripts

### Core Modules
- ✅ `main.py` - Already using typed components
- ✅ `stream/handler.py` - Migrated to handler_typed.py
- ✅ `chat/controller.py` - Full typed API support added


### Display Components
- ✅ Display v3 architecture already supports typed items

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

## Recent Progress (2024-12)

### ✅ Completed in This Migration Sprint

1. **Tool Processors**: Created typed versions of all remaining tool processors
   - `document_finder_typed.py` - Full typed implementation
   - `file_reader_typed.py` - Full typed implementation

2. **Chat Controller**: Enhanced with full typed API support
   - Added `prepare_typed_tools()` method
   - Added `extract_text_from_typed_response()` method
   - Integrated typed tools in send_message flow

3. **Migration Infrastructure**: Created comprehensive migration utilities
   - `migration_helpers.py` - Safe accessors for both APIs
   - Type detection and conversion utilities
   - Tool and message converters

4. **Example Scripts**: Created migration examples
   - `hello-typed-example.py` - Comprehensive typed API demonstrations
   - `migration-example.py` - Side-by-side comparison and migration patterns

5. **Testing**: Added compatibility test suite
   - `test_api_compatibility.py` - Tests for both APIs working together
   - Migration helper tests
   - Processor compatibility tests
   - End-to-end integration tests

6. **Documentation**: Created deprecation timeline
   - `DEPRECATION_TIMELINE.md` - Clear timeline and migration path
   - FAQ and support commitments
   - Action items for users

## Migration Statistics

- **Modules Migrated**: 15+
- **New Typed Processors**: 4
- **Migration Helpers**: 15+ utility methods
- **Test Coverage**: Both APIs tested for compatibility
- **Documentation**: Complete migration guide

## Next Steps

### Immediate (Before v0.6.0)
1. ✅ Complete remaining tool processor migrations
2. ✅ Add comprehensive migration helpers
3. ✅ Create example scripts and documentation
4. ✅ Add compatibility tests

### Short Term (v0.6.0 - v0.7.0)
1. Update all example scripts to use typed API
2. Add deprecation warnings to dict-based methods
3. Create automated migration tooling
4. Update all documentation to default to typed examples

### Medium Term (v0.7.0 - v0.8.0)
1. Move dict-based API to legacy module
2. Enhance migration tools based on user feedback
3. Create compatibility shim package
4. Complete internal migration

### Long Term (v1.0.0+)
1. Feature freeze dict-based API
2. Final deprecation warnings
3. Remove dict-based API in v2.0.0
4. Maintain legacy package separately

## Benefits Achieved

1. **Type Safety**: Full type checking with mypy/pyright
2. **IDE Support**: Complete autocomplete and inline docs
3. **Validation**: Automatic Pydantic validation
4. **Backward Compatibility**: Both APIs work during transition
5. **Migration Path**: Clear, documented, with tools
6. **Testing**: Comprehensive compatibility test suite

## Recommendations

For new code:
- Use typed API exclusively
- Import from `forge_cli.response._types`
- Follow examples in `hello-typed-example.py`

For existing code:
- Use `MigrationHelper` for compatibility
- Gradually migrate using patterns from `migration-example.py`
- Run compatibility tests to ensure correctness

The migration to typed API is well underway and provides significant benefits while maintaining full backward compatibility during the transition period.