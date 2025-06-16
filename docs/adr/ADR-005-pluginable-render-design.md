# ADR-005: Pluggable Render Architecture

## Status

Accepted - **Superseded by ADR-006 (V2 Event-Based Display Architecture)**

## Note

This ADR describes the v1 pluggable render system. The architecture has been significantly enhanced in v2 with an event-based system. See **ADR-006** for the current implementation.

## Context

The Knowledge Forge CLI supports multiple output display formats including plain text, rich terminal UI with live updates, and JSON output for machine parsing. As the project grows, additional render styles will likely be needed to support various use cases and environments. The existing approach embedded display selection logic directly in the `create_display` function, making it difficult to extend with new rendering options without modifying existing code.

## Decision

We will implement a pluginable render architecture following these design principles:

### 1. Registry Pattern

Centralize display implementations in a registry that allows dynamic registration of render modes:

```python
# DisplayRegistry class for managing and retrieving display implementations
DisplayRegistry.register_display(
    "json", 
    JsonDisplay, 
    condition=lambda config: config.json_output is True
)
```

### 2. Factory Pattern

Use a factory method to create display instances based on configuration:

```python
# Create appropriate display based on configuration
display = DisplayRegistry.get_display_for_config(config)
```

### 3. Condition-Based Selection

Determine the appropriate display mode using condition functions:

```python
# Each display mode defines when it should be used
condition=lambda config: (
    getattr(config, "use_rich", False) is True and 
    getattr(config, "quiet", False) is False
)
```

### 4. Consistent Interface (v1 - Legacy)

**Note**: This v1 interface has been replaced by the v2 event-based system.

All v1 display implementations conformed to a common `BaseDisplay` interface:

```python
class BaseDisplay(ABC):  # v1 - Legacy
    """Abstract base class for all display implementations."""
    
    @abstractmethod
    async def show_request_info(self, info: dict[str, Any]) -> None:
        """Display request information at the start."""
        pass
    
    @abstractmethod
    async def update_content(self, content: str, metadata: Optional[dict[str, Any]] = None) -> None:
        """Update the main content display."""
        pass
    
    # Additional required methods...
```

**Current v2 interface**:

```python
class Display:  # v2 - Current
    """Display coordinator for event-based architecture."""
    
    def handle_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Route events to renderer."""
        
    def complete(self) -> None:
        """Finalize display."""

class Renderer(Protocol):  # v2 - Current
    """Pure renderer protocol."""
    
    def render_stream_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Render a single stream event."""
        
    def finalize(self) -> None:
        """Complete rendering and cleanup."""
```

### 5. Custom Factory Functions

Support specialized initialization through factory functions:

```python
# Factory function for creating Rich display with custom console
factory=lambda **kwargs: RichDisplay(console=kwargs.get("console", None))
```

### 6. Fallback Mechanism

Implement fallback strategies when preferred display modes are unavailable:

```python
try:
    return DisplayRegistry.get_display_for_config(config)
except (ValueError, ImportError) as e:
    # Fallback to plain display if there's an error
    return PlainDisplay()
```

## Consequences

### Positive

- **Extensibility**: New render styles can be added without changing existing code
- **Separation of Concerns**: Display logic is isolated from application logic
- **Configuration Driven**: Display selection is determined by configuration
- **Graceful Degradation**: System falls back to simpler displays when needed
- **Testability**: Different display implementations can be tested independently

### Negative

- **Additional Complexity**: Registry pattern introduces more abstraction
- **Runtime Registration**: Display modes must be registered before use
- **Configuration Coordination**: Display conditions must be coordinated to avoid conflicts

## Examples

### Adding a New Display Implementation (v1 - Legacy)

**Note**: This shows the v1 approach. For v2 examples, see ADR-006.

To add a new HTML render mode in v1:

```python
# 1. Create your display implementation (v1 - Legacy)
class HtmlDisplay(BaseDisplay):
    """HTML display implementation for web output."""
    
    def __init__(self):
        self.content = ""
        
    async def show_request_info(self, info: dict[str, Any]) -> None:
        # HTML-specific implementation
        
    # Implement other required methods...

# 2. Register your display with the registry (v1 - Legacy)
DisplayRegistry.register_display(
    "html",
    HtmlDisplay,
    condition=lambda config: getattr(config, "html_output", False) is True
)
```

### Adding a New Renderer (v2 - Current)

```python
# 1. Create your renderer implementation (v2 - Current)
class HtmlRenderer(BaseRenderer):
    """HTML renderer for web output."""
    
    def render_stream_event(self, event_type: str, data: Dict[str, Any]) -> None:
        if event_type == "text_delta":
            self._handle_text(data.get("text", ""))
        elif event_type == "stream_start":
            self._handle_start(data.get("query", ""))
        # Handle other events...
    
    def finalize(self) -> None:
        # Output final HTML
        pass

# 2. Register in the display factory (v2 - Current)
def create_html_display(**kwargs):
    renderer = HtmlRenderer()
    return Display(renderer)

DisplayRegistry.register_display(
    "html",
    Display,
    factory=create_html_display,
    condition=lambda config: getattr(config, "html_output", False) is True
)
```

### Using Display Registry in Application Code

```python
# v1 approach (Legacy)
def create_display(config: SearchConfig) -> BaseDisplay:
    """Create appropriate display based on configuration using the display registry."""
    # Initialize default displays
    initialize_default_displays()
    
    # Get the appropriate display from the registry based on config
    try:
        return DisplayRegistry.get_display_for_config(config)
    except (ValueError, ImportError):
        # Fallback to plain display if there's an error
        return PlainDisplay()

# v2 approach (Current)
def create_display(config: SearchConfig) -> Display:
    """Create appropriate v2 display based on configuration."""
    initialize_default_displays()
    
    try:
        # Get v2 display directly from registry
        display = DisplayRegistry.get_display_for_config(config)
        return display
    except (ValueError, ImportError) as e:
        # Fallback to v2 plain renderer
        from forge_cli.display.v2.renderers.plain import PlainRenderer
        renderer = PlainRenderer()
        return Display(renderer)
```

## Migration to v2

The v1 system has been successfully migrated to v2. Key changes:

1. **Event-Based Architecture**: Replaced direct method calls with event handling
2. **Renderer Separation**: Split display coordination from rendering logic  
3. **Mode Support**: Added native support for chat mode with renderer reuse
4. **Performance**: Eliminated async overhead in display calls
5. **Backward Compatibility**: V1ToV2Adapter maintains compatibility during transition

See **ADR-006** for complete details on the v2 architecture.
