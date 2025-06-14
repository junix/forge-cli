# ADR-005: Pluginable Render Architecture

## Status
Accepted

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

### 4. Consistent Interface
All display implementations must conform to a common `BaseDisplay` interface:
```python
class BaseDisplay(ABC):
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

### Adding a New Display Implementation

To add a new HTML render mode:

```python
# 1. Create your display implementation
class HtmlDisplay(BaseDisplay):
    """HTML display implementation for web output."""
    
    def __init__(self):
        self.content = ""
        
    async def show_request_info(self, info: dict[str, Any]) -> None:
        # HTML-specific implementation
        
    # Implement other required methods...

# 2. Register your display with the registry
DisplayRegistry.register_display(
    "html",
    HtmlDisplay,
    condition=lambda config: getattr(config, "html_output", False) is True
)
```

### Using Display Registry in Application Code

```python
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
```
