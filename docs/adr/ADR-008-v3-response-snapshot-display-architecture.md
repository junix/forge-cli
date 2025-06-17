# ADR-008: V3 Response Snapshot Display Architecture

**Status**: Accepted (Updated 2025-06-17)
**Date**: 2025-06-15 (Updated 2025-06-17)
**Decision Makers**: Development Team
**Supersedes**: ADR-006 (V2 Event-Based Display Architecture)
**Complements**: ADR-004 (Snapshot-based Streaming), ADR-007 (Typed-Only Architecture)
**Updates**: Display factory pattern, AppConfig integration, chat-first renderer configuration

## Context

The V2 event-based display architecture (ADR-006), while an improvement over V1, still had complexity issues that became apparent during the migration to typed-only APIs:

### V2 Limitations

1. **Complex Event Routing**: 20+ event types requiring specific handling logic
2. **State Synchronization**: Difficult coordination between event handlers and renderers  
3. **Error Prone**: Missed events could corrupt display state
4. **Development Overhead**: New event types required updates across multiple handler methods
5. **Testing Complexity**: Mock events and state management made testing difficult

### Architectural Realization

With the adoption of **snapshot-based streaming** (ADR-004) and **typed Response objects** (ADR-007), we realized the display system could be dramatically simplified by embracing the core principle:

> **One Response, One Render** - Everything needed is in the Response object.

## Decision

**Implement V3 Response Snapshot Display Architecture** that simplifies rendering to a single method operating on complete Response snapshots.

### 1. Core Architecture Principle

Replace complex event handling with simple Response rendering:

```python
# V2 (Complex) - Multiple event handlers
def handle_text_delta(self, event_data): ...
def handle_citation_added(self, event_data): ...  
def handle_tool_started(self, event_data): ...
def handle_tool_completed(self, event_data): ...
def handle_reasoning_update(self, event_data): ...
# + dozens more event handlers

# V3 (Simple) - One render method
def render_response(self, response: Response):
    # Everything is in the response object!
    # - response.output (messages, tool calls, reasoning)
    # - response.status 
    # - response.usage
    # - Complete citations and annotations
```

### 2. Simplified Component Structure

```python
class Renderer(Protocol):
    """Pure renderer - only handles output formatting."""
    def render_response(self, response: Response) -> None: ...
    def finalize(self) -> None: ...

class Display:
    """Display coordinator - manages renderer lifecycle."""
    def handle_response(self, response: Response) -> None:
        self._renderer.render_response(response)
    
    def complete(self) -> None:
        self._renderer.finalize()
```

### 3. Stream Handler Simplification

TypedStreamHandler becomes trivial:

```python
async def handle_stream(self, stream: AsyncIterator[tuple[str, Response | None]], query: str):
    async for event_type, response in stream:
        if response is not None:
            # Update state and render complete snapshot
            state.update_from_snapshot(response)
            self.display.handle_response(response)
```

### 4. Rich Renderer Implementations

#### JSON Renderer with Rich Live Updates

```python
class JsonRenderer(BaseRenderer):
    def render_response(self, response: Response) -> None:
        # Convert to JSON with syntax highlighting
        json_output = json.dumps(self._response_to_dict(response), indent=2)
        
        syntax = Syntax(json_output, "json", theme="monokai", line_numbers=True)
        content = Panel(syntax, title="🔍 JSON Response", border_style="blue")
        
        # Live update display
        if self._live is None:
            self._live = Live(content, console=self._console)
            self._live.start()
        else:
            self._live.update(content)
```

#### Rich Terminal Renderer

```python
class RichRenderer(BaseRenderer):
    def render_response(self, response: Response) -> None:
        # Extract everything from Response
        text = response.output_text
        tool_calls = [item for item in response.output if hasattr(item, 'type') and 'call' in item.type]
        reasoning = [item for item in response.output if item.type == 'reasoning']
        citations = self._extract_citations(response)
        
        # Render complete UI
        self._render_content(text, tool_calls, reasoning, citations, response.usage)
```

#### Plaintext Renderer

```python
class PlaintextRenderer(BaseRenderer):
    def render_response(self, response: Response) -> None:
        # Simple text output with ANSI colors
        self._render_text_with_basic_formatting(response)
```

## Benefits Over V2

| Aspect | V2 (Complex) | V3 (Simple) |
|--------|-------------|-------------|
| **Event Handling** | 20+ event types | 1 response method |
| **State Management** | Complex synchronization | Stateless snapshots |
| **Error Recovery** | Missed events break state | Resilient snapshots |
| **Implementation** | 100s of lines per renderer | 10s of lines per renderer |
| **Debugging** | Complex event traces | Self-contained responses |
| **New Renderers** | Implement many methods | Implement one method |
| **Testing** | Mock complex event sequences | Mock single Response objects |

## Implementation Details

### Renderer Interface

```python
class BaseRenderer(ABC):
    @abstractmethod
    def render_response(self, response: Response) -> None:
        """Render a complete response snapshot."""
        pass
    
    @abstractmethod  
    def finalize(self) -> None:
        """Complete rendering and cleanup."""
        pass
```

### Display Coordinator

```python
class Display:
    def __init__(self, renderer: Renderer, mode: str = "default"):
        self._renderer = renderer
        self._mode = mode  # "default" or "chat"
    
    def handle_response(self, response: Response) -> None:
        """Route Response to renderer."""
        self._renderer.render_response(response)
    
    def complete(self) -> None:
        """Finalize display."""
        self._renderer.finalize()
```

### Display Factory Pattern (2025-06-17 Update)

The V3 architecture now uses a sophisticated `DisplayFactory` with `AppConfig` integration:

```python
class DisplayFactory:
    """Factory for creating display instances based on configuration."""

    @staticmethod
    def create_display(config: AppConfig) -> Display:
        """Create appropriate display based on configuration using v3 architecture."""
        from forge_cli.display.v3.base import Display

        # Chat mode is now the default - determine mode intelligently
        in_chat_mode = True  # Chat-first architecture
        mode = "chat" if in_chat_mode else "default"

        # Choose renderer based on configuration
        if config.render_format == "json":
            # JSON output with Rich live updates
            from forge_cli.display.v3.renderers.json import JsonDisplayConfig, JsonRenderer

            json_config = JsonDisplayConfig(
                pretty_print=True,
                include_metadata=config.debug,
                include_usage=not config.quiet,
                show_panel=not config.quiet,
                panel_title="🔍 Knowledge Forge JSON Response" if in_chat_mode else "📋 JSON Response",
                syntax_theme="monokai",
                line_numbers=not in_chat_mode and not config.quiet,
            )
            renderer = JsonRenderer(config=json_config)

        elif config.render_format == "plaintext":
            # Plain text output
            from forge_cli.display.v3.renderers.plaintext import PlaintextDisplayConfig, PlaintextRenderer

            plain_config = PlaintextDisplayConfig(
                show_reasoning=config.show_reasoning,
                show_citations=True,
                show_usage=not config.quiet,
                show_metadata=config.debug,
            )
            renderer = PlaintextRenderer(config=plain_config)

        else:
            # Rich terminal UI (default)
            from forge_cli.display.v3.renderers.rich import RichDisplayConfig, RichRenderer

            display_config = RichDisplayConfig(
                show_reasoning=config.show_reasoning,
                show_citations=True,
                show_tool_details=True,
                show_usage=not config.quiet,
                show_metadata=config.debug,
            )
            renderer = RichRenderer(config=display_config, in_chat_mode=in_chat_mode)

        # Create v3 display
        return Display(renderer, mode=mode)
```

## Renderer Configuration System (2025-06-17 Update)

Each renderer now uses Pydantic configuration models for type-safe setup:

### Rich Renderer Configuration
```python
class RichDisplayConfig(BaseModel):
    show_reasoning: bool = Field(True, description="Whether to show reasoning/thinking content")
    show_citations: bool = Field(True, description="Whether to show citation details")
    show_tool_details: bool = Field(True, description="Whether to show detailed tool information")
    show_usage: bool = Field(True, description="Whether to show token usage statistics")
    show_metadata: bool = Field(False, description="Whether to show response metadata")
    max_text_preview: int = Field(100, description="Maximum characters for text previews")
    refresh_rate: int = Field(10, description="Live update refresh rate (per second)")
```

### JSON Renderer Configuration
```python
class JsonDisplayConfig(BaseModel):
    pretty_print: bool = Field(True, description="Whether to format JSON with indentation")
    indent: int = Field(2, description="Number of spaces for indentation")
    include_metadata: bool = Field(False, description="Whether to include response metadata")
    include_usage: bool = Field(True, description="Whether to include token usage")
    show_panel: bool = Field(True, description="Whether to show Rich panel around JSON")
    panel_title: str = Field("JSON Response", description="Title for the panel")
    syntax_theme: str = Field("monokai", description="Syntax highlighting theme")
    line_numbers: bool = Field(True, description="Whether to show line numbers")
```

### Plaintext Renderer Configuration
```python
class PlaintextDisplayConfig(BaseModel):
    show_reasoning: bool = Field(True, description="Whether to show reasoning content")
    show_citations: bool = Field(True, description="Whether to show citations")
    show_usage: bool = Field(True, description="Whether to show token usage")
    show_metadata: bool = Field(False, description="Whether to show metadata")
    use_colors: bool = Field(True, description="Whether to use ANSI colors")
    max_width: int = Field(80, description="Maximum line width for text wrapping")
```

## Response Object Richness

The Response object contains everything needed for rendering:

```python
response = Response(
    id="resp_123",
    status="completed",
    model="gpt-4o",
    output=[
        ResponseOutputMessage(
            content=[
                ResponseOutputText(
                    text="The answer is...",
                    annotations=[...]  # Citations inline
                )
            ]
        ),
        FileSearchToolCall(
            status="completed",
            queries=["search term"],
            results=[...]
        )
    ],
    usage=ResponseUsage(
        input_tokens=100,
        output_tokens=200
    )
)
```

## Migration from V2

### Before (V2 Event Handlers)
```python
class V2Renderer:
    def handle_text_delta(self, text): ...
    def handle_tool_start(self, tool_data): ...
    def handle_tool_complete(self, tool_data): ...
    def handle_citation_added(self, citation): ...
    def handle_usage_update(self, usage): ...
    def handle_status_change(self, status): ...
    # ... 15 more methods
```

### After (V3 Single Method)
```python
class V3Renderer:
    def render_response(self, response: Response):
        # Extract all needed data from response
        text = response.output_text
        tools = self._extract_tools(response)
        citations = self._extract_citations(response)
        usage = response.usage
        status = response.status
        
        # Render everything at once
        self._render_complete_ui(text, tools, citations, usage, status)
```

## JSON Renderer Enhancements

The V3 JSON renderer provides rich features:

### Rich Syntax Highlighting
```python
syntax = Syntax(json_output, "json", theme="monokai", line_numbers=True, word_wrap=True)
```

### Live Updates
```python
if self._live is None:
    self._live = Live(content, console=self._console, refresh_per_second=4)
    self._live.start()
else:
    self._live.update(content)
```

### Configurable Display
```python
JsonDisplayConfig(
    pretty_print=True,
    show_panel=True,           # Rich panel with borders
    panel_title="🔍 JSON Response",
    syntax_theme="monokai",    # Syntax highlighting theme
    line_numbers=True,         # Show line numbers
    include_usage=True,        # Include token usage
    include_metadata=False     # Debug session metadata
)
```

## Testing Strategy

V3 testing is dramatically simpler:

```python
def test_json_renderer():
    renderer = JsonRenderer()
    
    # Create mock Response (much simpler than event sequences)
    response = Response(
        id="test_123",
        status="completed", 
        output=[
            ResponseOutputMessage(content=[
                ResponseOutputText(text="Hello world")
            ])
        ]
    )
    
    # Test single method call
    renderer.render_response(response)
    
    # Verify output
    assert "Hello world" in renderer.get_output()
```

## Performance Benefits

1. **Fewer Method Calls**: Single render call vs. multiple event handlers
2. **No Event Routing**: Direct Response → Renderer without complex routing
3. **Stateless Rendering**: No state synchronization overhead
4. **Efficient Updates**: Complete snapshots eliminate partial state issues

## Future Renderer Extensions

The V3 architecture makes it trivial to add new renderers:

```python
class HtmlRenderer(BaseRenderer):
    def render_response(self, response: Response) -> None:
        html = self._response_to_html(response)
        self._write_html_file(html)

class MarkdownRenderer(BaseRenderer):
    def render_response(self, response: Response) -> None:
        markdown = self._response_to_markdown(response)
        print(markdown)

class TelegramRenderer(BaseRenderer):
    def render_response(self, response: Response) -> None:
        message = self._format_for_telegram(response)
        self._send_telegram_message(message)
```

Each requires implementing just one method: `render_response(response: Response)`!

## Consequences

### ✅ Positive

1. **Dramatic Simplification**: ~90% reduction in display code complexity
2. **Reliability**: Stateless rendering eliminates sync issues
3. **Developer Experience**: Single method to implement for new renderers
4. **Performance**: Faster rendering without event routing overhead
5. **Rich JSON**: Beautiful syntax-highlighted JSON with live updates
6. **Testing**: Much simpler unit tests with mock Response objects
7. **Maintenance**: Far fewer moving parts to maintain
8. **Type Safety**: Pydantic configuration models with validation (2025-06-17)
9. **Factory Pattern**: Clean separation of renderer creation logic (2025-06-17)
10. **Chat Integration**: Seamless integration with chat-first architecture (2025-06-17)

### ⚠️ Considerations

1. **Breaking Change**: V2 renderers must be rewritten for V3
2. **Response Completeness**: Relies on Response objects containing all needed data
3. **Memory Usage**: Complete snapshots use more memory than deltas (negligible in practice)
4. **Configuration Complexity**: More sophisticated configuration system (2025-06-17)

### 🔄 Migration Required

Existing custom renderers need migration:

```python
# V2 → V3 Migration
class CustomRenderer:
    # Remove all these V2 methods:
    # def handle_text_delta(self, text): ...
    # def handle_tool_start(self, data): ...
    # def handle_citation_added(self, citation): ...

    # Replace with single V3 method:
    def render_response(self, response: Response):
        # Extract everything from response and render
        pass

# 2025-06-17 Update: Add Pydantic configuration
class CustomDisplayConfig(BaseModel):
    show_details: bool = Field(True, description="Show detailed information")
    theme: str = Field("default", description="Display theme")

class CustomRenderer(BaseRenderer):
    def __init__(self, config: CustomDisplayConfig):
        self.config = config

    def render_response(self, response: Response):
        # Use self.config for rendering options
        pass
```

## Related ADRs

- **ADR-004**: Snapshot-based Streaming Design (foundation for V3)
- **ADR-007**: Typed-Only Architecture Migration (enables V3 simplification)
- **ADR-006**: V2 Event-Based Display Architecture (superseded)
- **ADR-012**: Chat-First Architecture Migration (influences display factory design)
- **ADR-014**: Configuration System Refactoring (enables Pydantic renderer configs)

---

**Key Insight**: V3 embraces the snapshot-based streaming design (ADR-004), making everything simpler, more reliable, and easier to extend. The complexity moves from the display layer (where it was hard to manage) to the Response object design (where it belongs).

**2025-06-17 Update**: The V3 architecture has matured with sophisticated configuration management, factory patterns, and seamless integration with the chat-first architecture, providing a robust foundation for all display scenarios.