# Display Module - Output Formatting Strategies

## Overview

The display module implements the Strategy pattern to provide multiple output formatting options for the Forge CLI. It separates presentation logic from business logic, allowing users to choose between rich terminal UI, plain text, or JSON output while maintaining consistent functionality across all formats.

The module has evolved through multiple versions:

- **v1**: Original display implementations (legacy, removed)
- **v2**: Event-based display architecture (legacy, deprecated)
- **v3**: Current snapshot-based architecture with simplified renderer design

## Directory Structure

```
display/
├── __init__.py          # Module exports
├── registry.py          # Display registry for strategy selection/registration
├── v2/                  # Legacy v2 event-based display architecture (deprecated)
│   ├── __init__.py
│   ├── base.py          # v2 base display and renderer classes
│   ├── events.py        # Event type definitions
│   └── renderers/       # Legacy pluggable renderers
│       ├── __init__.py
│       ├── plain.py     # Plain text renderer
│       ├── rich.py      # Rich UI renderer
│       └── json.py      # JSON renderer
└── v3/                  # Current snapshot-based display architecture
    ├── __init__.py
    ├── base.py          # v3 display coordinator and renderer protocol
    ├── example.py       # Usage examples and demos
    └── renderers/       # Current pluggable renderers
        ├── __init__.py
        ├── plain.py     # Plain text renderer
        ├── rich.py      # Rich UI renderer with live updates
        ├── json.py      # JSON renderer
        └── json_example.py # JSON usage examples
```

## Architecture & Design

### Design Patterns

1. **Strategy Pattern**: Core pattern - different display strategies for same content
2. **Protocol Pattern**: V3 uses Protocol classes for renderer interfaces
3. **Registry Pattern**: DisplayRegistry manages available displays and selection logic
4. **Snapshot Pattern**: V3 uses response snapshots instead of event streaming
5. **Facade Pattern**: Display coordinator provides unified interface

### Display Registry & Factory System

The `DisplayRegistry` class manages the registration and creation of display implementations:

```python
# From registry.py
class DisplayRegistry:
    """Registry for display implementations."""
    
    _displays: dict[str, type[BaseDisplay]] = {}
    _factories: dict[str, Callable[..., BaseDisplay]] = {}
    _conditions: dict[str, Callable[[Any], bool]] = {}
    
    @classmethod
    def register_display(
        cls,
        name: str,
        display_cls: type[BaseDisplay],
        factory: Callable[..., BaseDisplay] = None,
        condition: Callable[[Any], bool] = None,
    ):
        """Register a display implementation."""
        # ...

    @classmethod
    def get_display_for_config(cls, config: Any) -> BaseDisplay:
        """Get the appropriate display for the given configuration."""
        for name, condition in cls._conditions.items():
            if condition(config):
                return cls.create_display(name, config=config)
        # ...
```

Display selection occurs automatically based on configuration:

```python
# Display strategy selection via registry
display = DisplayRegistry.get_display_for_config(config)
```

## v1 Component Details (Legacy)

### v1/base.py - Base Display Interface

Defines the contract all v1 display strategies must implement:

```python
class BaseDisplay(ABC):
    """Abstract base class for display strategies."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.start_time = time.time()
    
    @abstractmethod
    def handle_stream_start(self) -> None:
        """Called when stream begins."""
        pass
    
    @abstractmethod
    def handle_text_delta(self, text: str) -> None:
        """Handle incremental text output."""
        pass
    
    # Additional abstract methods...
```

### v1/rich_display.py, v1/plain_display.py, v1/json_display.py

Original display implementations for various output formats.

## v3 Architecture (Current)

### v3/base.py - Component Classes

The v3 system separates concerns between display coordination and rendering:

```python
class Renderer(Protocol):
    """Pure renderer protocol - only handles output formatting."""

    def render_stream_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Render a single stream event."""
        ...

    def finalize(self) -> None:
        """Complete rendering and cleanup."""
        ...


class Display:
    """Display coordinator - manages render lifecycle."""

    def __init__(self, renderer: Renderer, mode: str = "default"):
        """Initialize display with a renderer."""
        self._renderer = renderer
        self._event_count = 0
        self._finalized = False
        self._mode = mode
        
    def handle_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Route events to renderer."""
        # ...
        
    def complete(self) -> None:
        """Finalize display."""
        # ...
```

### v2/adapter.py - Backward Compatibility

The adapter allows v2 displays to be used with v1 interfaces:

```python
class V1ToV2Adapter(BaseDisplay):
    """Adapter to make v2 Display work with v1 interface."""

    def __init__(self, display_v2: Display):
        """Initialize adapter with a v2 display."""
        self._display = display_v2
        self._start_time = time.time()

    # Implements v1 methods by mapping to v2 events
    def handle_text_delta(self, text: str) -> None:
        """Map v1 text delta to v2 event."""
        self._display.handle_event(EventType.TEXT_DELTA.value, {"text": text})
        
    # Additional v1 method implementations...
```

### v2/renderers - Output Formatting

Three primary renderer implementations:

1. **rich.py**: Interactive terminal UI with Rich library
2. **plain.py**: Simple text output for logs/non-TTY
3. **json.py**: Structured data for API/machine consumption

## Usage Guidelines

### For Language Models

When working with the display system:

1. **Using the registry**:

```python
from forge_cli.display.registry import DisplayRegistry

# Get appropriate display based on configuration
display = DisplayRegistry.get_display_for_config(config)

# Or create specific display
json_display = DisplayRegistry.create_display("json", config=config)
```

2. **Creating a new v2 renderer**:

```python
from forge_cli.display.v2.base import BaseRenderer

class CustomRenderer(BaseRenderer):
    def render_stream_event(self, event_type: str, data: dict):
        if event_type == "text_delta":
            # Handle text output
            text = data.get("text", "")
            # Custom rendering logic
        elif event_type == "tool_start":
            # Handle tool execution
            # ...
    
    def finalize(self):
        # Cleanup and finalization
```

3. **Using with v1 interface**:

```python
from forge_cli.display.v2.adapter import V1ToV2Adapter
from forge_cli.display.v2.base import Display
from forge_cli.display.v2.renderers.rich import RichRenderer

# Create v2 display with rich renderer
renderer = RichRenderer()
display_v2 = Display(renderer)

# Adapt to v1 interface
display_v1_compatible = V1ToV2Adapter(display_v2)

# Use with v1 methods
display_v1_compatible.handle_text_delta("Hello world")
```

## Development Guidelines

### Adding New V3 Renderers (Recommended)

1. **Create a V3 renderer**:

```python
from forge_cli.display.v3.base import BaseRenderer
from forge_cli.response._types.response import Response

class NewRenderer(BaseRenderer):
    """New renderer description."""

    def render_response(self, response: Response) -> None:
        # Extract what you need from response
        text = response.output_text
        status = response.status
        citations = self._extract_citations(response)

        # Implement your custom rendering logic
        self._render_content(text, status, citations)

    def finalize(self) -> None:
        # Cleanup if needed
        pass

    def _extract_citations(self, response: Response) -> list:
        # Helper method to extract citations
        return []

    def _render_content(self, text: str, status: str, citations: list) -> None:
        # Your custom rendering implementation
        pass
```

2. **Register with DisplayRegistry**:

```python
from forge_cli.display.registry import DisplayRegistry
from forge_cli.display.v3.base import Display

def create_new_display(**kwargs):
    renderer = NewRenderer()
    return Display(renderer)

DisplayRegistry.register_display(
    "new_display",
    Display,  # V3 Display class
    factory=create_new_display,
    condition=lambda config: getattr(config, "use_new_display", False) is True,
)
```

### Best Practices for V3 Development

1. **Snapshot-Based Design**:
   - Work with complete Response objects, not individual events
   - Extract all needed information from the response in `render_response()`
   - Avoid maintaining state between render calls

2. **Type Safety**:
   - Use TypeGuards to safely access response content
   - Import types from `forge_cli.response._types`
   - Leverage IDE autocomplete with proper type annotations

3. **Error Handling**:
   - Handle missing or malformed response data gracefully
   - Provide meaningful error messages for debugging
   - Support finalization even after errors

4. **Testing**:
   - Test renderers with mock Response objects
   - Create comprehensive test cases for different response types
   - Validate output format consistency

5. **Performance**:
   - Minimize processing in `render_response()` for real-time updates
   - Cache expensive computations when possible
   - Use efficient string formatting techniques
