# ADR-007: Migration to Typed-Only Architecture

**Status**: Accepted  
**Date**: 2025-06-15  
**Decision Makers**: Development Team  
**Supersedes**: Portions of ADR-005 (Response API Type System Architecture)

## Context

The Forge CLI codebase had evolved to support both dict-based (legacy) and typed Response API systems for backward compatibility during the migration period. This dual support led to:

1. **Code Complexity**: Dual handling paths in stream handlers, displays, and processors
2. **Type Safety Issues**: Mixed usage of `Any`, `dict`, and typed `Response` objects
3. **Maintenance Burden**: Legacy adapter classes and migration helpers
4. **Performance Overhead**: Unnecessary type conversions and adapter calls
5. **Developer Experience**: Confusing APIs with multiple ways to accomplish the same tasks

### Legacy Components Identified

- `ResponseAdapter`, `StreamEventAdapter`, `ToolAdapter` classes
- `astream_response()` function with dual dict/typed modes
- Mixed type signatures: `dict[str, Any] | Response | None`
- Legacy event handling in `TypedStreamHandler`
- Migration helper utilities in adapters module

## Decision

**Complete migration to typed-only architecture**, removing all legacy dict-based response handling and adapter classes.

### 1. Remove Legacy Response Functions

**Removed:**
```python
# Legacy streaming function
async def astream_response(
    input_messages: str | list[dict[str, str]],
    typed: bool = False,  # Dual mode support
) -> AsyncIterator[tuple[str, dict[str, Any] | ResponseStreamEvent]]
```

**Keep Only:**
```python
# Pure typed streaming function  
async def astream_typed_response(
    request: Request,
    debug: bool = False,
) -> AsyncIterator[tuple[str, Response | None]]
```

### 2. Remove Adapter Classes

**Eliminated:**
- `ResponseAdapter` class - was just `Response(**data)` wrapper
- `StreamEventAdapter` class - unused in typed API
- `ToolAdapter` class - replaced with direct tool constructors
- `MigrationHelper` class - no longer needed

**Direct Construction:**
```python
# Before (via adapter)
response = ResponseAdapter.from_dict(api_data)
tool = ToolAdapter.create_file_search_tool(vector_store_ids)

# After (direct typed construction)
response = Response(**api_data)
tool = FileSearchTool(type="file_search", vector_store_ids=vector_store_ids)
```

### 3. Simplify Stream Handler

**TypedStreamHandler** now exclusively handles typed `Response` objects:

```python
async def handle_stream(
    self, 
    stream: AsyncIterator[tuple[str, Response | None]], 
    initial_request: str
) -> StreamState:
    """Handle streaming events from typed API only."""
    async for event_type, event_data in stream:
        if event_data is not None and isinstance(event_data, Response):
            # Update state from Response
            state.update_from_snapshot(event_data)
            
            # Render complete Response snapshot using v3 display
            self.display.handle_response(event_data)
```

**Removed complex event routing logic** - all processing moved to v3 renderers.

### 4. Update Display Architecture

**V3 Display System** now works exclusively with `Response` snapshots:

```python
class Renderer(Protocol):
    def render_response(self, response: Response) -> None: ...

class Display:
    def handle_response(self, response: Response) -> None:
        self._renderer.render_response(response)
```

### 5. Enhanced JSON Renderer

Replaced basic logger output with **Rich Live + Syntax Highlighting**:

```python
class JsonRenderer(BaseRenderer):
    def render_response(self, response: Response) -> None:
        # Create Rich syntax highlighting
        syntax = Syntax(json_output, "json", theme="monokai")
        
        # Create panel with live updates
        if self._live is None:
            self._live = Live(content, console=self._console)
            self._live.start()
        else:
            self._live.update(content)
```

## Consequences

### ✅ Positive

1. **Type Safety**: All APIs now use proper typed objects with IDE support
2. **Simplified Codebase**: Removed ~500 lines of adapter and migration code
3. **Performance**: Eliminated unnecessary type conversions and adapter overhead
4. **Maintainability**: Single source of truth for Response handling
5. **Developer Experience**: Clear, consistent APIs with better error messages
6. **Rich JSON Output**: Beautiful syntax highlighting instead of plain text

### ⚠️ Considerations

1. **Breaking Change**: Legacy dict-based consumers must migrate to typed API
2. **Migration Required**: External integrations need to update to `astream_typed_response`
3. **Testing Updates**: Test mocks must use typed `Response` objects

### 🔄 Migration Path

For external consumers still using legacy APIs:

```python
# Before (legacy)
async for event_type, event_data in astream_response(messages):
    text = event_data.get("text", "")

# After (typed)
request = Request(input=[InputMessage(role="user", content=message)])
async for event_type, response in astream_typed_response(request):
    text = response.output_text if response else ""
```

## Implementation Notes

### Removed Files
- `src/forge_cli/response/adapters.py` - Migration helpers no longer needed
- Legacy `astream_response()` function from SDK
- `stream/handler.py` - Replaced by `handler_typed.py`

### Updated Files
- `sdk.py`: Only typed functions remain
- `stream/handler_typed.py`: Simplified to Response-only handling
- `main.py`: Enhanced display creation with JSON renderer selection
- `display/v3/renderers/json.py`: Rich Live + Syntax highlighting

### Configuration Changes
```python
# JSON output now supports Rich rendering
SearchConfig(
    json_output=True,    # Enables JsonRenderer with Rich Live updates
    quiet=False,         # Shows panel borders and formatting
    debug=True           # Includes session metadata
)
```

## Validation

### Testing Strategy
1. **Unit Tests**: All tests updated to use typed `Response` objects
2. **Integration Tests**: Full CLI testing with `--json` flag
3. **Type Checking**: `mypy` validation with strict typing enabled
4. **Performance Tests**: Verify improved performance without adapters

### Success Criteria
- [x] All imports work without adapter dependencies
- [x] `--json` flag produces Rich syntax-highlighted output
- [x] Chat mode works with typed API
- [x] No type safety warnings or `Any` usage
- [x] Performance improvement in stream processing

## Future Considerations

1. **OpenAPI Generation**: Consider auto-generating types from OpenAPI schema
2. **Validation Enhancement**: Add runtime Pydantic validation at API boundaries  
3. **Additional Renderers**: HTML, Markdown renderers following same pattern
4. **Error Typing**: Specific error types instead of generic exceptions

## Related ADRs

- **ADR-004**: Snapshot-based Streaming Design (unchanged - still valid)
- **ADR-005**: Response API Type System (updated to reflect typed-only)
- **ADR-006**: V2 Event-Based Display Architecture (superseded by V3)

---

**Migration Complete**: The Forge CLI now exclusively uses typed Response APIs, providing better type safety, performance, and developer experience while maintaining all functionality through the new architecture.