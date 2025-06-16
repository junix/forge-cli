# Display Module - Output Formatting Strategies

## Overview

The display module implements the Strategy pattern to provide multiple output formatting options for the Forge CLI. It separates presentation logic from business logic, allowing users to choose between rich terminal UI, plain text, or JSON output while maintaining consistent functionality across all formats.

The module has evolved through multiple versions:
- **v1**: Original display implementations (legacy, removed)
- **v2**: Enhanced architecture with pluggable renderers (legacy, removed)  
- **v3**: Current architecture with improved renderer capabilities and event processing

## Directory Structure

```
display/
├── __init__.py          # Module exports
├── registry.py          # Display registry for strategy selection/registration
├── v2/                  # Legacy v2 display architecture (for migration support)
│   ├── __init__.py
│   ├── base.py          # v2 base display and renderer classes
│   ├── events.py        # Event type definitions
│   └── renderers/       # Pluggable renderers
│       ├── __init__.py
│       ├── plain.py     # Plain text renderer
│       ├── rich.py      # Rich UI renderer
│       └── json.py      # JSON renderer
└── v3/                  # Current display architecture
    ├── __init__.py
    ├── base.py          # v3 base display and renderer classes  
    ├── example.py       # Usage examples
    └── renderers/       # v3 Pluggable renderers
        ├── __init__.py
        ├── plain.py     # Plain text renderer
        ├── rich.py      # Rich UI renderer
        ├── json.py      # JSON renderer
        └── json_example.py # JSON usage examples
```

## Architecture & Design

### Design Patterns

1. **Strategy Pattern**: Core pattern - different display strategies for same content
2. **Adapter Pattern**: V1ToV2Adapter connects legacy code to new rendering system
3. **Registry Pattern**: DisplayRegistry manages available displays and selection logic
4. **Observer Pattern**: Displays react to processor events
5. **Facade Pattern**: Unified interface for complex display operations

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

### Adding New Display Strategies

1. **Create a v2 renderer**:

```python
from forge_cli.display.v2.base import BaseRenderer

class NewRenderer(BaseRenderer):
    """New renderer description."""
    
    def render_stream_event(self, event_type: str, data: dict):
        # Implement rendering logic
        pass
    
    def finalize(self):
        # Cleanup and finalization
        pass
```

2. **Register with DisplayRegistry**:

```python
from forge_cli.display.registry import DisplayRegistry
from forge_cli.display.v2.adapter import V1ToV2Adapter
from forge_cli.display.v2.base import Display

def create_new_display(**kwargs):
    renderer = NewRenderer()
    display_v2 = Display(renderer)
    return V1ToV2Adapter(display_v2)

DisplayRegistry.register_display(
    "new_display",
    V1ToV2Adapter,  # Class type for registry
    factory=create_new_display,
    condition=lambda config: getattr(config, "use_new_display", False) is True,
)
```

### Best Practices

1. **State Management**:
   - Keep rendering state in the renderer
   - Use the Display class to coordinate events
   - Separate formatting from business logic

2. **Error Handling**:
   - Provide error rendering in all renderers
   - Gracefully handle unexpected event types
   - Support finalization even after errors

3. **Testing**:
   - Test renderers independently
   - Create mock events for testing rendering logic
   - Validate backward compatibility with v1 interfaces
