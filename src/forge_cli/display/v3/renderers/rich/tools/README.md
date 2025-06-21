# Modular Tool Renderer Architecture

This directory implements the modular tool renderer architecture as described in [ADR-015](../../../../../../../docs/adr/ADR-015-modular-tool-renderer-architecture.md).

## Overview

The modular tool renderer architecture replaces the original monolithic tool rendering approach with specialized renderer classes for each tool type. Each renderer follows a consistent builder pattern and provides both programmatic access and factory methods for backward compatibility.

## Architecture Principles

### 1. One Tool, One Renderer
Each tool type has its own dedicated renderer class:
- `FileReaderToolRender` - File reading operations
- `WebSearchToolRender` - Web search queries
- `FileSearchToolRender` - File system search
- `PageReaderToolRender` - Document page reading
- `CodeInterpreterToolRender` - Code execution
- `FunctionCallToolRender` - Function invocation
- `ListDocumentsToolRender` - Document listing

### 2. Builder Pattern
All renderers support fluent method chaining:

```python
result = (FileReaderToolRender()
          .with_filename("document.pdf")
          .with_file_size(1024000)
          .with_progress(0.75)
          .render())
```

### 3. Factory Methods
Each renderer provides a `from_tool_item()` factory method for backward compatibility:

```python
# Direct usage
result = FileReaderToolRender.from_tool_item(tool_item)
```

### 4. Consistent Interface
All renderers implement the same core interface:
- `__init__()` - Initialize empty renderer
- `render()` - Build and return formatted string
- `from_tool_item(cls, tool_item)` - Factory method
- `with_status(status)` - Add status display
- `with_execution_trace(trace)` - Add trace (handled separately)

## Usage Examples

### FileReaderToolRender

```python
from forge_cli.display.v3.renderers.rich.tools import FileReaderToolRender

# Manual construction
renderer = FileReaderToolRender()
result = (renderer
          .with_filename("research.pdf")
          .with_file_size(2048000)
          .with_progress(0.85)
          .render())
# Output: " 󰈈 "research.pdf" [PDF]  •   󰈈 1MB  •   ⚡ 85%"

# Factory method
result = FileReaderToolRender.from_tool_item(file_reader_item)
```

### WebSearchToolRender

```python
from forge_cli.display.v3.renderers.rich.tools import WebSearchToolRender

# Multiple queries
result = (WebSearchToolRender()
          .with_queries(["Python tutorial", "FastAPI guide", "async programming"])
          .with_results_count(25)
          .render())
# Output: "   Python tutorial  FastAPI guide  async programming  •   ✓ 25 results"
```

### CodeInterpreterToolRender

```python
from forge_cli.display.v3.renderers.rich.tools import CodeInterpreterToolRender

code = """
import pandas as pd
data = pd.read_csv('file.csv')
print(data.head())
"""

result = (CodeInterpreterToolRender()
          .with_code(code)
          .with_output("   A  B  C\n0  1  2  3")
          .render())
# Output: " 󰌠 Python: `import pandas as pd`  •   󰌠 3 lines  •   ↓ output:    A  B  C..."
```

## Implementation Details

### Icon Usage
All renderers use consistent icons from `../../../style.py`:
- `ICONS['file_reader_call']` - File operations
- `ICONS['web_search_call']` - Web searches  
- `ICONS['code']` - Code and arguments
- `ICONS['processing']` - Progress indicators
- `ICONS['check']` - Completion/results
- `ICONS['bullet']` - Part separators

### Text Formatting
Consistent text formatting rules:
- Filenames truncated at 30 characters + "..."
- Query text truncated at 25-40 characters depending on context
- Multiple queries use `pack_queries()` helper function
- Progress shown as percentages (e.g., "75%")
- File sizes formatted as B/KB/MB

### Status Handling
All renderers support status display:
- `"in_progress"` - Default, shows processing indicators
- `"completed"` - Shows completion markers
- `"searching"` - Shows "init" status
- `"failed"` - Shows error indicators

## Testing

Comprehensive test coverage in `tests/display/test_tool_renderers.py`:

```python
# Run all tool renderer tests
python -m pytest tests/display/test_tool_renderers.py -v

# Run specific renderer tests
python -m pytest tests/display/test_tool_renderers.py::TestFileReaderToolRender -v
```

## Demo

Interactive demonstration available:

```python
# Run the demo
PYTHONPATH=src python tests/display/demo_tool_renderers.py
```

## Migration from Monolithic Rendering

The old monolithic approach in `tool_methods.py`:

```python
# Before - inline logic
def get_tool_result_summary(tool_item):
    if is_file_reader_call(tool_item):
        # 50+ lines of inline rendering logic
        parts = []
        if tool_item.file_name:
            # ... complex formatting
        return " • ".join(parts)
```

New modular approach:

```python
# After - dedicated renderer
def get_tool_result_summary(tool_item):
    if is_file_reader_call(tool_item):
        return FileReaderToolRender.from_tool_item(tool_item)
```

## Benefits

### Maintainability
- Each tool's display logic is isolated
- Changes to one tool don't affect others
- Clear separation of concerns

### Testability  
- Individual renderers can be tested in isolation
- Builder pattern enables fine-grained testing
- Mock objects easy to create and use

### Extensibility
- New tools only require new renderer classes
- Existing tools unaffected by additions
- Plugin system foundation established

### Consistency
- All tools follow same architectural patterns
- Unified icon and formatting standards
- Predictable API across all renderers

## Future Enhancements

- **Theme Support**: Multiple visual themes per renderer
- **Plugin System**: External tools can provide custom renderers  
- **Performance Optimization**: Individual renderer caching
- **Custom Formatting**: Per-context rendering options 