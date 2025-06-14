# Typed API Migration Guide

## Overview

This guide explains the migration from the legacy dict-based `astream_response` API to the new type-safe `astream_typed_response` API in the Forge CLI project.

## Why Migrate?

1. **Type Safety**: Full type checking with mypy and IDE support
2. **Better Developer Experience**: Autocomplete for all Response properties
3. **Error Prevention**: Catch type errors at development time
4. **Cleaner Code**: No more dict key access and get() methods

## Migration Strategy

The migration follows a gradual approach to maintain backward compatibility:

1. **Infrastructure First**: Create adapters and helpers
2. **Core Components**: Update SDK and stream handlers
3. **Scripts**: Migrate example scripts one by one
4. **Processors**: Update to support both dict and typed items
5. **Main Entry Points**: Enable typed API in CLI

## Key Components

### 1. SDK Update (`src/forge_cli/sdk.py`)

The `astream_typed_response` function now correctly yields Response objects:

```python
async def astream_typed_response(
    request: Request,
    debug: bool = False,
) -> AsyncIterator[tuple[str, Response | None]]:
    # Convert Request to proper format
    request_dict = request.model_dump(exclude_none=True)
    
    # Stream and convert to Response objects
    async for event_type, event_data in astream_response(...):
        if event_data and isinstance(event_data, dict):
            try:
                response = ResponseAdapter.from_dict(event_data)
                yield event_type, response
            except Exception:
                yield event_type, None
```

### 2. Migration Helpers (`src/forge_cli/response/adapters.py`)

The `MigrationHelper` class provides safe methods for working with both APIs:

```python
# Check if data is typed Response
is_typed = MigrationHelper.is_typed_response(event_data)

# Extract text safely from either format
text = MigrationHelper.safe_get_text(event_data)

# Get output items
items = MigrationHelper.safe_get_output_items(event_data)
```

### 3. Typed Stream Handler (`src/forge_cli/stream/handler_typed.py`)

The `TypedStreamHandler` supports both dict and Response objects:

```python
handler = TypedStreamHandler(display, debug=True)
state = await handler.handle_stream(stream, query)
```

### 4. Processor Updates

Processors now support both dict and typed items:

```python
def process(self, item: Any) -> dict[str, Any] | None:
    # Handle typed event
    if isinstance(item, ResponseOutputMessage):
        return {"text": item.output_text}
    
    # Handle dict for backward compatibility
    elif isinstance(item, dict):
        return {"text": item.get("text", "")}
```

## Migration Examples

### Simple Script Migration

**Before (dict-based):**
```python
async for event_type, event_data in astream_response(...):
    if event_type == "response.output_text.delta":
        text = event_data.get("text", "")
        print(text, end="")
```

**After (typed):**
```python
from forge_cli.response.adapters import MigrationHelper

async for event_type, event_data in astream_typed_response(request):
    if event_type == "response.output_text.delta":
        text = MigrationHelper.safe_get_text(event_data)
        print(text, end="")
```

### Creating Typed Requests

```python
from forge_cli.response._types import Request, FileSearchTool, WebSearchTool

request = Request(
    input=[{"type": "text", "text": "Your query"}],
    model="qwen-max-latest",
    tools=[
        FileSearchTool(
            type="file_search",
            vector_store_ids=["vs_123"],
            max_num_results=5,
        ),
        WebSearchTool(
            type="web_search",
            country="US",
            city="San Francisco",
        )
    ],
    temperature=0.7,
    max_output_tokens=2000,
)
```

## Migrated Components

### ✅ Completed
- Core SDK (`sdk.py`)
- Migration utilities (`response/adapters.py`)
- Stream handler (`stream/handler_typed.py`)
- Base processors (`processors/base_typed.py`)
- Message processor (already supported both)
- Reasoning processor (already supported both)
- File search processor (`processors/tool_calls/file_search_typed.py`)
- Web search processor (`processors/tool_calls/web_search_typed.py`)
- Processor registry (`processors/registry_typed.py`)
- Example scripts:
  - `hello-async.py`
  - `hello-file-search-typed.py`
  - `hello-web-search-typed.py`
  - `simple-flow-typed.py`
- Main entry points:
  - `main_typed.py`
  - `main_typed_v2.py`

### ⏳ Pending
- Remaining tool processors
- Chat controller updates
- Display component updates
- Remaining example scripts

## Testing

Run the migration test suite:

```bash
python scripts/test_migration_utilities.py
```

This tests:
- MigrationHelper utilities
- ResponseAdapter functionality
- Type conversions
- Edge cases

## Best Practices

1. **Use MigrationHelper**: For safe access to response data
2. **Support Both APIs**: During transition period
3. **Test Thoroughly**: Both dict and typed paths
4. **Update Gradually**: Module by module
5. **Document Changes**: Update docstrings and comments

## Common Patterns

### Extracting Tool Results

```python
# Works with both dict and typed
results = MigrationHelper.safe_get_tool_calls(event_data)
for result in results:
    if hasattr(result, 'file_id'):  # Typed
        file_id = result.file_id
    elif isinstance(result, dict):  # Dict
        file_id = result.get('file_id')
```

### Handling Citations

```python
# Extract citations safely
if hasattr(item, 'annotations'):  # Typed
    citations = item.annotations
elif isinstance(item, dict):  # Dict
    citations = item.get('annotations', [])
```

## Troubleshooting

### Import Errors
- Use `forge_cli.response._types` for Response types
- Use `forge_cli.models` for Request types (if using models/)

### Validation Errors
- Response objects have many required fields
- Use ResponseAdapter.from_dict() for conversion
- Consider using mock objects for testing

### Type Checking
- Run mypy to catch type errors early
- Use proper type annotations throughout

## Next Steps

1. Continue migrating remaining modules
2. Add typed API option to all entry points
3. Update documentation with typed examples
4. Consider deprecation timeline for dict API
5. Add more comprehensive type tests

The typed API provides a much better developer experience while maintaining full backward compatibility during the transition period.