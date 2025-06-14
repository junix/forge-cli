# Migration Status: Dict-based to Typed Response API

## Overview

This document tracks the progress of migrating from the legacy dict-based `astream_response` API to the new typed `astream_typed_response` API across the forge-cli codebase.

## Migration Benefits Achieved

1. ✅ **Type Safety**: Request/Response objects with full type checking
2. ✅ **Migration Utilities**: Helper functions for gradual migration
3. ✅ **Backward Compatibility**: Can work with both APIs during transition
4. ✅ **Test Coverage**: Migration test suite validates the approach

## Completed Items

### Infrastructure (✅ Complete)
- [x] Created `astream_typed_response` function in SDK
- [x] Created `async_create_typed_response` function in SDK
- [x] Created `create_typed_request` helper function
- [x] Created migration adapters in `response/adapters.py`
- [x] Created `MigrationHelper` with safe accessors
- [x] Created comprehensive migration guide
- [x] Created test suite for migration utilities

### Scripts (🟡 In Progress)
- [x] Updated `hello-async.py` to use typed API
- [x] Created `debug_typed.py` as typed API example
- [x] Created `test_migration.py` to verify migration
- [ ] Update `hello-file-search.py`
- [ ] Update `hello-web-search.py`
- [ ] Update `hello-file-reader.py`
- [ ] Update `simple-flow.py`

### Core Modules (⏳ Not Started)
- [ ] Update `stream/handler.py`
- [ ] Update `processors/base.py`
- [ ] Update `processors/registry.py`
- [ ] Update `processors/message.py`
- [ ] Update `processors/reasoning.py`
- [ ] Update `processors/tool_calls/*.py`
- [ ] Update `display/v2/renderers/*.py`
- [ ] Update `main.py`
- [ ] Update `chat/controller.py`

## Known Issues

1. **Response.output_text property**: Fails when output items are plain dicts instead of typed objects
   - **Workaround**: MigrationHelper handles this gracefully with try/except

2. **Strict Validation**: Response objects require many fields that might not be present in all API responses
   - **Workaround**: Use MigrationHelper for safe field access

3. **Nested Type Requirements**: Output items must be properly typed Pydantic models
   - **Impact**: Full Response object features may not work until server returns proper types

## Migration Strategy

### Phase 1: Foundation (✅ Complete)
- Created typed API functions
- Built migration utilities
- Established patterns

### Phase 2: Scripts (🟡 In Progress)
- Migrating example scripts
- Testing with both APIs
- Documenting patterns

### Phase 3: Core Modules (⏳ Planned)
- Update stream processing
- Update processors
- Update display logic

### Phase 4: Finalization (⏳ Future)
- Remove dict-based code paths
- Make typed API default
- Update all documentation

## Usage Examples

### Old Pattern (Dict-based)
```python
async for event_type, event_data in astream_response(
    input_messages="Hello",
    model="qwen-max"
):
    if event_data and "text" in event_data:
        text = event_data["text"]
```

### New Pattern (Typed)
```python
request = create_typed_request(
    input_messages="Hello",
    model="qwen-max-latest"
)
async for event_type, response in astream_typed_response(request):
    if response:
        text = response.output_text  # Type-safe access
```

### Migration Pattern (Works with Both)
```python
# Use MigrationHelper for compatibility
text = MigrationHelper.safe_get_text(event_data)  # Works with dict or Response
status = MigrationHelper.safe_get_status(event_data)
usage = MigrationHelper.safe_get_usage(event_data)
```

## Next Steps

1. **Immediate**: Continue migrating scripts to establish patterns
2. **Short-term**: Update core stream processing with compatibility layer
3. **Medium-term**: Migrate all processors to support both APIs
4. **Long-term**: Deprecate dict-based API and remove legacy code

## Testing

Run the migration test suite:
```bash
python scripts/test_migration.py
```

Test individual migrated scripts:
```bash
python scripts/hello-async.py  # Uses typed API
python scripts/debug_typed.py   # Full typed example
```

## Notes

- The migration is designed to be gradual and non-breaking
- Both APIs can coexist during the transition period
- MigrationHelper provides a safety net for mixed environments
- Full Response object capabilities require properly typed server responses