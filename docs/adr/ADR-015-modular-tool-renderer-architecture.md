# ADR-015: Modular Tool Renderer Architecture

**Status**: Superseded by ADR-016  
**Date**: 2025-01-20  
**Decision Makers**: Development Team  
**Complements**: ADR-008 (v3 Response Snapshot Display Architecture)  
**Superseded By**: ADR-016 (Simplified Tool Renderer Architecture)

## Context

The original v3 Rich renderer implemented all tool rendering logic within large monolithic functions in `tool_methods.py`. As the system evolved to support more tool types and complex rendering requirements, this approach exhibited several limitations:

### Original Architecture Problems

1. **Monolithic Tool Rendering**: All tool rendering logic concentrated in a single `get_tool_result_summary()` function (200+ lines)
2. **Poor Maintainability**: Modifying one tool's display logic required understanding all other tools
3. **Limited Extensibility**: Adding new tool types required modifying core rendering functions
4. **Testing Complexity**: Difficult to test individual tool renderers in isolation
5. **Code Coupling**: Tool-specific logic tightly coupled with generic rendering infrastructure
6. **Inconsistent Patterns**: Different tools implemented ad-hoc rendering approaches

### Growing Tool Complexity

The system evolved to support increasingly sophisticated tool displays:
- File reader tools with progress, file metadata, and status
- Web search tools with query formatting and result counts
- Code interpreter tools with language detection and output previews
- Function calls with argument previews and result summaries
- Page readers with document identification and page ranges

## Decision

**Implement a modular tool renderer architecture** where each tool type has its dedicated renderer class with consistent interfaces and builder patterns.

### 1. Individual Tool Renderer Classes

Create specialized renderer classes for each tool type:

```
src/forge_cli/display/v3/renderers/rich/tools/
├── __init__.py              # Tool renderer exports
├── file_reader.py           # FileReaderToolRender
├── web_search.py            # WebSearchToolRender  
├── code_interpreter.py      # CodeInterpreterToolRender
├── page_reader.py           # PageReaderToolRender
├── function_call.py         # FunctionCallToolRender
└── file_search.py           # FileSearchToolRender
```

### 2. Consistent Tool Renderer Interface

All tool renderers follow a standard pattern:

```python
class ToolNameToolRender:
    """Specialized renderer for [tool_name] tool calls."""
    
    def __init__(self):
        """Initialize the tool renderer."""
        self._parts = []
        self._status = "in_progress"
    
    def with_property(self, property_value) -> "ToolNameToolRender":
        """Add property display to the render (builder pattern)."""
        # Process and format property
        return self
    
    def with_status(self, status: str) -> "ToolNameToolRender":
        """Add status display to the render."""
        self._status = status
        return self
    
    def render(self) -> str:
        """Build and return the final rendered string."""
        # Combine parts and return formatted result
        pass
    
    @classmethod
    def from_tool_item(cls, tool_item) -> str:
        """Factory method for backward compatibility."""
        # Extract properties and build renderer
        pass
```

### 3. Builder Pattern Implementation

Support fluent interfaces for flexible tool rendering:

```python
# Manual construction with method chaining
result = (FileReaderToolRender()
          .with_filename("document.pdf")
          .with_file_size(1024000)
          .with_progress(0.75)
          .with_status("completed")
          .render())

# Factory method for existing code compatibility
result = FileReaderToolRender.from_tool_item(tool_item)
```

## Implementation Details

### FileReaderToolRender Example

```python
class FileReaderToolRender:
    """Specialized renderer for file reader tool calls."""
    
    def __init__(self):
        self._parts = []
        self._status = "in_progress"
    
    def with_filename(self, filename: str | None) -> "FileReaderToolRender":
        if filename:
            ext = filename.split(".")[-1].lower() if "." in filename else "file"
            name_short = filename[:30] + "..." if len(filename) > 30 else filename
            self._parts.append(f'{ICONS["file_reader_call"]}"{name_short}" [{ext.upper()}]')
        return self
    
    def with_file_size(self, file_size: int | None) -> "FileReaderToolRender":
        if file_size is not None:
            if file_size < 1024:
                size_str = f"{file_size}B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size // 1024}KB"
            else:
                size_str = f"{file_size // (1024 * 1024)}MB"
            self._parts.append(f"{ICONS['file_reader_call']}{size_str}")
        return self
    
    def with_progress(self, progress: float | None) -> "FileReaderToolRender":
        if progress is not None:
            progress_percent = int(progress * 100)
            self._parts.append(f"{ICONS['processing']}{progress_percent}%")
        return self
    
    def render(self) -> str:
        if self._parts:
            return f" {ICONS['bullet']} ".join(self._parts)
        return f"{ICONS['processing']}loading file..."
    
    @classmethod
    def from_tool_item(cls, tool_item) -> str:
        renderer = cls()
        
        if hasattr(tool_item, 'file_name'):
            renderer.with_filename(tool_item.file_name)
        
        if hasattr(tool_item, 'file_size'):
            renderer.with_file_size(tool_item.file_size)
            
        progress = getattr(tool_item, 'progress', None)
        if progress is not None:
            renderer.with_progress(progress)
        
        return renderer.render()
```

### Integration with Existing Code

Tool renderers integrate seamlessly with existing rendering pipeline:

```python
# In tool_methods.py - before
elif is_file_reader_call(tool_item):
    # 50+ lines of inline rendering logic
    parts = []
    if tool_item.file_name:
        # ... complex formatting logic
    return " • ".join(parts)

# In tool_methods.py - after  
elif is_file_reader_call(tool_item):
    from .tools import FileReaderToolRender
    return FileReaderToolRender.from_tool_item(tool_item)
```

## Benefits

### 1. Modularity and Separation of Concerns
- **Tool-Specific Logic**: Each tool renderer handles only its own display logic
- **Clear Boundaries**: Well-defined interfaces between tool types
- **Independent Evolution**: Tool renderers can evolve independently

### 2. Enhanced Maintainability  
- **Focused Changes**: Modifications affect only relevant tool renderer
- **Easier Debugging**: Tool-specific issues isolated to specific classes
- **Code Organization**: Related functionality grouped together

### 3. Improved Testability
- **Unit Testing**: Each tool renderer can be tested in isolation
- **Mock Objects**: Easy to create mock tool items for testing
- **Edge Cases**: Comprehensive testing of tool-specific scenarios

### 4. Extensibility and Flexibility
- **New Tools**: Adding new tools requires only creating new renderer classes
- **Feature Addition**: New properties easily added via new `with_*` methods
- **Customization**: Different rendering styles possible for different contexts

### 5. Consistent User Experience
- **Unified Patterns**: All tools follow same rendering patterns
- **Icon Consistency**: Shared icon dictionary ensures visual consistency
- **Text Formatting**: Consistent text length limits and formatting rules

## Migration Strategy

### Phase 1: Foundation
- [x] Create modular directory structure
- [x] Implement FileReaderToolRender as reference implementation
- [x] Create migration guides and documentation
- [x] Establish testing patterns

### Phase 2: Core Tools Migration
- [x] WebSearchToolRender implementation
- [ ] FileSearchToolRender migration
- [ ] CodeInterpreterToolRender migration
- [ ] PageReaderToolRender migration

### Phase 3: Advanced Tools
- [ ] FunctionCallToolRender migration
- [ ] ListDocumentsToolRender migration
- [ ] Custom tool renderer support

### Phase 4: Cleanup
- [ ] Remove old monolithic rendering functions
- [ ] Update all integration points
- [ ] Comprehensive testing and validation

## Testing Strategy

Each tool renderer includes comprehensive test coverage:

```python
def test_file_reader_basic():
    renderer = FileReaderToolRender()
    result = (renderer
              .with_filename("test.pdf")
              .with_file_size(1024)
              .render())
    assert "test.pdf" in result
    assert "1KB" in result

def test_file_reader_factory():
    tool_item = MockFileReaderItem(file_name="doc.pdf", file_size=2048)
    result = FileReaderToolRender.from_tool_item(tool_item)
    assert "doc.pdf" in result
    assert "2KB" in result
```

## Documentation and Guidance

Comprehensive documentation ensures smooth adoption:

- **TOOL_RENDERER_GUIDE.md**: Detailed implementation guide with templates
- **MIGRATION_EXAMPLE.md**: Step-by-step migration examples
- **README.md**: Quick start guide and overview

## Consequences

### Positive
- **Code Quality**: Better organized, more maintainable codebase
- **Developer Experience**: Easier to add new tools and modify existing ones
- **Testing**: Comprehensive test coverage for individual components
- **Performance**: No performance impact, potentially better due to reduced complexity

### Negative  
- **Initial Complexity**: More files and classes to understand initially
- **Migration Effort**: Requires systematic migration of existing tools

### Neutral
- **File Count**: More files but better organization
- **Learning Curve**: New patterns to learn but consistent across tools

## Compliance

This decision aligns with existing architectural principles:

- **ADR-008 Compliance**: Maintains v3 snapshot-based rendering approach
- **Modular Design**: Follows established patterns from chat command system (ADR-013)
- **Type Safety**: Continues strong typing established in ADR-007
- **Testing Standards**: Maintains comprehensive testing requirements

## Future Considerations

- **Plugin System**: Tool renderers provide foundation for plugin-based tool system
- **Theme Support**: Renderer classes can support multiple display themes
- **Performance Optimization**: Individual renderers can be optimized independently
- **Custom Tools**: External tools can provide their own renderer implementations 