# V3 Renderers - Pluggable Display Components

## Overview

The V3 renderers directory contains pluggable display components that implement the V3 snapshot-based display architecture (ADR-008). These renderers provide different output formats for the same response data, enabling flexible presentation options while maintaining consistent functionality.

## Directory Structure

```
renderers/
├── CLAUDE.md                    # This documentation file
├── __init__.py                  # Renderer exports and registry
├── json.py                      # JSON format renderer
├── json_example.py              # JSON renderer usage examples
├── plaintext.py                 # Simple plaintext renderer
├── plaintext_example.py         # Plaintext renderer examples
├── rendable.py                  # Renderable architecture components
├── rich.py                      # Rich terminal UI renderer (main)
├── plaintext/                   # Modular plaintext renderer
│   ├── __init__.py              # Plaintext module exports
│   ├── README.md                # Plaintext renderer documentation
│   ├── citations.py             # Citation formatting
│   ├── config.py                # Configuration and settings
│   ├── message_content.py       # Message content rendering
│   ├── reasoning.py             # Reasoning block rendering
│   ├── render.py                # Main rendering logic
│   ├── styles.py                # Text styling utilities
│   ├── usage.py                 # Usage statistics rendering
│   ├── welcome.py               # Welcome message rendering
│   └── tools/                   # Tool-specific renderers
└── rich/                        # Rich terminal renderer
    ├── __init__.py              # Rich module exports
    ├── citations.py             # Rich citation formatting
    ├── message_content.py       # Rich message rendering
    ├── reason.py                # Rich reasoning rendering
    ├── render.py                # Main Rich rendering logic
    ├── usage.py                 # Rich usage display
    ├── welcome.py               # Rich welcome screen
    └── tools/                   # Rich tool renderers
```

## Architecture & Design

### V3 Renderer Architecture (ADR-008)

The V3 architecture uses snapshot-based rendering instead of event-based processing:

**Key Benefits:**
- **Simplified State Management**: No complex event synchronization
- **Consistent Rendering**: Complete response snapshots ensure consistency
- **Easy Testing**: Deterministic rendering from response objects
- **Pluggable Design**: Easy to add new output formats

### Renderer Protocol

All renderers implement the same base protocol:

```python
from typing import Protocol
from forge_cli.response._types.response import Response

class Renderer(Protocol):
    """Protocol for V3 renderers."""
    
    def render_response(self, response: Response) -> None:
        """Render a complete response snapshot."""
        ...
    
    def finalize(self) -> None:
        """Finalize rendering (cleanup, summary, etc.)."""
        ...
```

## Core Renderers

### Rich Renderer (rich.py)

The primary renderer providing rich terminal UI with colors, formatting, and live updates:

**Features:**
- **Rich Terminal UI**: Colors, formatting, progress bars
- **Live Updates**: Real-time display updates during streaming
- **Citation Tables**: Formatted citation tables with markdown
- **Tool Visualization**: Visual representation of tool execution
- **Status Indicators**: Clear status indicators for operations

**Usage:**
```python
from forge_cli.display.v3.renderers.rich import RichRenderer

renderer = RichRenderer()
renderer.render_response(response)
renderer.finalize()
```

**Rich Components:**
- **citations.py**: Rich citation table formatting
- **message_content.py**: Rich message content with markdown
- **reason.py**: Rich reasoning block display
- **usage.py**: Rich usage statistics display
- **welcome.py**: Rich welcome screen with branding
- **tools/**: Rich tool-specific renderers

### Plaintext Renderer (plaintext.py)

Simple text-based renderer for basic terminals and automation:

**Features:**
- **Simple Text Output**: Plain text without special formatting
- **Wide Compatibility**: Works in any terminal environment
- **Automation Friendly**: Suitable for scripts and automation
- **Minimal Dependencies**: No external UI dependencies

**Usage:**
```python
from forge_cli.display.v3.renderers.plaintext import PlaintextRenderer

renderer = PlaintextRenderer()
renderer.render_response(response)
renderer.finalize()
```

**Modular Plaintext (plaintext/):**
- **citations.py**: Plain text citation formatting
- **message_content.py**: Simple message rendering
- **reasoning.py**: Plain reasoning block display
- **styles.py**: Text styling utilities (ASCII art, etc.)
- **tools/**: Plain text tool renderers

### JSON Renderer (json.py)

Machine-readable JSON output for automation and integration:

**Features:**
- **Structured Output**: Complete response data in JSON format
- **API Integration**: Perfect for API consumers and automation
- **Data Preservation**: Preserves all response metadata
- **Programmatic Access**: Easy to parse and process

**Usage:**
```python
from forge_cli.display.v3.renderers.json import JsonRenderer

renderer = JsonRenderer()
renderer.render_response(response)
renderer.finalize()
```

## Modular Renderer Architecture

### Plaintext Modular Design

The plaintext renderer demonstrates modular architecture:

```python
# plaintext/render.py - Main rendering coordinator
class PlaintextRenderer:
    def __init__(self):
        self.citation_renderer = CitationRenderer()
        self.message_renderer = MessageRenderer()
        self.tool_renderer = ToolRenderer()
    
    def render_response(self, response: Response) -> None:
        # Coordinate rendering across modules
        for item in response.output:
            if is_message_item(item):
                self.message_renderer.render(item)
            elif is_tool_call(item):
                self.tool_renderer.render(item)
```

### Rich Modular Design

The Rich renderer uses similar modular patterns:

```python
# rich/render.py - Rich rendering coordinator
class RichRenderer:
    def __init__(self):
        self.console = Console()
        self.citation_renderer = RichCitationRenderer(self.console)
        self.message_renderer = RichMessageRenderer(self.console)
        self.tool_renderer = RichToolRenderer(self.console)
    
    def render_response(self, response: Response) -> None:
        # Rich-specific rendering with live updates
        with Live(console=self.console) as live:
            self._render_with_live_updates(response, live)
```

## Tool-Specific Renderers

### Tool Renderer Architecture

Each renderer type has tool-specific sub-renderers:

**Plaintext Tools (plaintext/tools/):**
- File search renderer
- Web search renderer
- Function call renderer
- Code interpreter renderer

**Rich Tools (rich/tools/):**
- Rich file search with progress bars
- Rich web search with status indicators
- Rich function calls with syntax highlighting
- Rich code interpreter with execution display

### Tool Renderer Example

```python
# Tool-specific renderer pattern
class FileSearchRenderer:
    def render_file_search(self, call: ResponseFileSearchToolCall) -> None:
        """Render file search tool call."""
        print(f"📄 Searching documents...")
        for query in call.queries:
            print(f"  Query: {query}")
        
        if call.status == "completed":
            print(f"✅ Search completed")
        elif call.status == "in_progress":
            print(f"⏳ Search in progress...")
```

## Configuration and Customization

### Renderer Configuration

```python
# Configuration for different renderers
class RendererConfig:
    # Rich renderer settings
    rich_theme: str = "default"
    show_progress: bool = True
    live_updates: bool = True
    
    # Plaintext renderer settings
    max_width: int = 80
    show_timestamps: bool = False
    ascii_art: bool = True
    
    # JSON renderer settings
    pretty_print: bool = True
    include_metadata: bool = True
```

### Styling Customization

```python
# Custom styling for renderers
class CustomRichRenderer(RichRenderer):
    def __init__(self):
        super().__init__()
        self.console = Console(theme=Theme({
            "info": "cyan",
            "warning": "yellow",
            "error": "red bold",
            "success": "green bold"
        }))
```

## Usage Examples

### Basic Renderer Usage

```python
from forge_cli.display.v3.base import Display
from forge_cli.display.v3.renderers.rich import RichRenderer

# Create display with Rich renderer
renderer = RichRenderer()
display = Display(renderer)

# Render response
display.handle_response(response)
display.complete()
```

### Renderer Selection

```python
def create_renderer(format_type: str) -> Renderer:
    """Create renderer based on format type."""
    if format_type == "rich":
        return RichRenderer()
    elif format_type == "plaintext":
        return PlaintextRenderer()
    elif format_type == "json":
        return JsonRenderer()
    else:
        raise ValueError(f"Unknown renderer type: {format_type}")
```

### Custom Renderer

```python
class CustomRenderer:
    """Custom renderer example."""
    
    def render_response(self, response: Response) -> None:
        """Custom rendering logic."""
        print(f"=== Response {response.id} ===")
        
        # Custom processing logic
        for item in response.output:
            if is_message_item(item):
                print(f"Message: {item.content}")
            elif is_file_search_call(item):
                print(f"File Search: {item.queries}")
        
        print("=== End Response ===")
    
    def finalize(self) -> None:
        """Custom finalization."""
        print("Rendering complete!")
```

## Related Components

- **Display Base** (`../base.py`) - Display coordinator that uses renderers
- **Response Types** (`../../../response/_types/`) - Data structures rendered
- **Type Guards** (`../../../response/type_guards/`) - Safe type checking for rendering
- **Main CLI** (`../../../main.py`) - Renderer selection and configuration

## Best Practices

### Renderer Development

1. **Follow Protocol**: Implement the Renderer protocol consistently
2. **Use TypeGuards**: Use TypeGuards for safe type checking
3. **Modular Design**: Break complex renderers into modules
4. **Error Handling**: Handle rendering errors gracefully
5. **Performance**: Optimize for responsive rendering

### Customization

1. **Configuration**: Support configuration for customization
2. **Theming**: Allow theme and style customization
3. **Extensibility**: Design for easy extension and modification
4. **Compatibility**: Ensure compatibility across different environments
5. **Testing**: Include comprehensive tests for rendering logic

The V3 renderers provide a flexible, maintainable approach to displaying response data across different output formats while maintaining the benefits of the snapshot-based architecture.
