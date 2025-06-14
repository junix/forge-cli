# Response Type System Migration Guide

## Overview

This guide outlines the migration from dict-based API interactions to the new typed response system in `forge_cli.response._types`.

## Benefits of Migration

1. **Type Safety**: Full type checking with mypy/pyright
2. **IDE Support**: Autocomplete and inline documentation
3. **Validation**: Automatic Pydantic validation
4. **Error Messages**: Clear validation errors
5. **OpenAI Compatibility**: Built-in conversion methods
6. **Maintainability**: Self-documenting code

## Migration Strategy

### Phase 1: Foundation (Immediate)
✅ **Status: Complete**
- Type system is fully implemented in `_types/`
- All types are properly exported
- No external dependencies (isolated module)

### Phase 2: Create Adapters (Week 1)
✅ **Status: Complete**
- Created `adapters.py` with conversion utilities
- `ResponseAdapter`: Convert between dict and typed objects
- `StreamEventAdapter`: Parse stream events
- `ToolAdapter`: Create typed tool definitions

### Phase 3: SDK Integration (Week 2-3)
**Status: In Progress**
- Enhance SDK to accept typed inputs
- Maintain backward compatibility
- Add typed return options

### Phase 4: Gradual Adoption (Week 4+)
**Status: Planned**
- Update processors to use typed events
- Migrate display components
- Convert scripts to typed API

## Code Examples

### Basic Usage

```python
from forge_cli.response.adapters import ResponseAdapter
from forge_cli.response._types import Request, Response

# Create a typed request
request = ResponseAdapter.create_request(
    input_messages="What is machine learning?",
    model="qwen-max-latest",
    temperature=0.7,
)

# Convert to OpenAI format
openai_payload = request.as_openai_chat_request()
```

### Using Tools

```python
from forge_cli.response.adapters import ToolAdapter
from forge_cli.response._types import FileSearchTool, WebSearchTool

# Create typed tools
file_search = ToolAdapter.create_file_search_tool(
    vector_store_ids=["vs_123"],
    max_search_results=10
)

web_search = WebSearchTool()

# Add to request
request = ResponseAdapter.create_request(
    input_messages="Find recent AI research",
    tools=[file_search, web_search],
)
```

### Stream Processing

```python
from forge_cli.response.adapters import StreamEventAdapter

async for event_type, event_data in original_stream():
    # Parse to typed event
    typed_event = StreamEventAdapter.parse_event(event_data)
    
    # Type-safe access
    if isinstance(typed_event, ResponseTextDeltaEvent):
        print(typed_event.text)
```

### Backward Compatibility

```python
# Old code continues to work
response_dict = await sdk.create_response(
    input_messages=[{"role": "user", "content": "Hello"}],
    model="gpt-4"
)

# New code with types
request = Request(
    input=[InputMessage(role="user", content="Hello")],
    model="gpt-4"
)
response = await sdk.create_typed_response(request)
```

## Migration Checklist

### For SDK (`sdk.py`)
- [ ] Add typed method variants (e.g., `create_typed_response`)
- [ ] Update stream handlers to emit typed events
- [ ] Add type overloads for better IDE support
- [ ] Update documentation

### For Processors (`processors/`)
- [ ] Update base processor to accept typed events
- [ ] Convert event handling to use typed objects
- [ ] Update state management with typed models
- [ ] Add type guards for event discrimination

### For Display (`display/`)
- [ ] Update interfaces to accept typed metadata
- [ ] Convert citation handling to use typed annotations
- [ ] Update event handlers

### For Models (`models/`)
- [ ] Gradually replace TypedDict with Pydantic models
- [ ] Add validation where appropriate
- [ ] Update imports to use new types

### For Scripts (`scripts/`)
- [ ] Start using typed requests in new scripts
- [ ] Update existing scripts during maintenance
- [ ] Add type hints throughout

## Common Patterns

### Type Guards

```python
from forge_cli.response._types import (
    ResponseTextDeltaEvent,
    ResponseFileSearchCallCompletedEvent,
)

def handle_event(event: ResponseStreamEvent):
    if isinstance(event, ResponseTextDeltaEvent):
        # Type checker knows this is a text delta
        process_text(event.text)
    elif isinstance(event, ResponseFileSearchCallCompletedEvent):
        # Type checker knows this has file search results
        process_results(event.results)
```

### Optional Migration

```python
# Function that accepts both old and new formats
def process_message(
    message: Union[Dict[str, Any], InputMessage]
) -> str:
    if isinstance(message, dict):
        # Legacy path
        return message.get("content", "")
    else:
        # Typed path
        return message.content or ""
```

### Validation

```python
from pydantic import ValidationError

try:
    request = Request(
        input="Hello",  # Will be converted to message list
        model="invalid-model",  # Will raise validation error
    )
except ValidationError as e:
    print(f"Invalid request: {e}")
```

## Best Practices

1. **Start with New Code**: Use types in all new code
2. **Migrate During Refactoring**: Update when touching existing code
3. **Maintain Compatibility**: Don't break existing APIs
4. **Add Type Hints**: Even without full migration, add hints
5. **Validate Early**: Use Pydantic validation at boundaries
6. **Document Changes**: Update docstrings with type information

## Troubleshooting

### Import Errors
If you see import errors, ensure you're importing from the correct location:
```python
# Correct
from forge_cli.response._types import Request

# Incorrect
from forge_cli.response import Request
```

### Type Checking
Enable strict type checking in your IDE:
```json
// pyproject.toml
[tool.mypy]
strict = true
```

### Validation Errors
Pydantic provides detailed error messages:
```python
try:
    request = Request(input=123)  # Invalid type
except ValidationError as e:
    print(e.json(indent=2))
    # Shows exactly what field failed and why
```

## Next Steps

1. **Fix Logger Imports**: Update `common.logger` to `forge_cli.common.logger`
2. **Create Type Stubs**: For better IDE support
3. **Add Tests**: Unit tests for adapters and conversions
4. **Update Documentation**: API docs with typed examples
5. **Performance Testing**: Ensure no regression from validation

## Conclusion

The new type system provides significant benefits while maintaining full backward compatibility. The phased migration approach ensures stability while gradually improving code quality and developer experience.