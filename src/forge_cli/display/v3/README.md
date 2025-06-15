# Display v3 - Simplified Snapshot-Based Rendering

The v3 display system represents a major simplification over v2, embracing the **snapshot-based streaming design** from [ADR-004](../../../docs/adr/CLAUDE-004-snapshot-based-streaming-design.md).

## Core Design Principle

**One Response, One Render** - Everything you need is in the `Response` object.

```python
def render_response(self, response: Response) -> None:
    """Render a complete response snapshot - that's it!"""
    # All information is available in the response:
    # - response.output (messages, tool calls, etc.)
    # - response.status 
    # - response.usage
    # - response.model
    # - Complete citations and annotations
```

## Why v3 is Better

### v2 Problems (Complex Event Handling)
```python
# v2 - Complex event routing and state management
def handle_text_delta(self, event_data): ...
def handle_citation_added(self, event_data): ...  
def handle_tool_started(self, event_data): ...
def handle_tool_completed(self, event_data): ...
def handle_reasoning_update(self, event_data): ...
# + dozens more event handlers
# + complex state synchronization
# + missed events can corrupt display
```

### v3 Solution (Simple Response Rendering)
```python
# v3 - One simple method
def render_response(self, response: Response):
    # Everything is in the response object!
    # No state tracking, no event synchronization
    # Resilient to missed events (snapshot-based)
```

## Architecture

```txt
Display v3 Architecture
─────────────────────

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   StreamEvent   │───▶│    Display      │───▶│   Renderer      │
│   (Response)    │    │   Coordinator   │    │  Implementation │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       handle_response()        render_response()
                                                      │
                              │                       ▼
                              ▼               ┌─────────────────┐
                         Complete()          │ Beautiful Rich  │
                                            │ Terminal Output │
                                            └─────────────────┘
```

## Key Components

### 1. Display Coordinator (`base.py`)
- Manages renderer lifecycle
- Routes responses to renderer
- Handles completion and cleanup

### 2. Renderer Protocol
```python
class Renderer(Protocol):
    def render_response(self, response: Response) -> None: ...
    def finalize(self) -> None: ...
```

### 3. Rich Renderer (`renderers/rich.py`)
- Beautiful terminal UI with live updates
- Comprehensive response rendering:
  - ✅ Message content (Markdown formatted)
  - ✅ Tool execution status with icons
  - ✅ Citations table with sources
  - ✅ Reasoning content (when available)
  - ✅ Usage statistics
  - ✅ Response metadata
  - ✅ Error handling
  - ✅ Chat mode support

## Usage Examples

### Basic Usage
```python
from forge_cli.display.v3.base import Display
from forge_cli.display.v3.renderers.rich import RichRenderer

# Create renderer and display
renderer = RichRenderer()
display = Display(renderer)

# Render responses (from streaming)
for response in response_stream:
    display.handle_response(response)

# Complete rendering
display.complete()
```

### Custom Configuration
```python
from forge_cli.display.v3.renderers.rich import RichRenderer, RichDisplayConfig

config = RichDisplayConfig(
    show_reasoning=True,
    show_citations=True, 
    show_tool_details=True,
    show_usage=True,
    refresh_rate=10
)

renderer = RichRenderer(config=config, in_chat_mode=True)
display = Display(renderer, mode="chat")
```

### Easy Renderer Switching
```python
# Switch renderers without changing display logic
display = Display(RichRenderer())      # Beautiful terminal UI
display = Display(PlainRenderer())     # Simple text output
display = Display(JsonRenderer())      # Structured JSON
display = Display(HtmlRenderer())      # Web-ready HTML
```

## Benefits Over v2

| Aspect | v2 (Complex) | v3 (Simple) |
|--------|-------------|-------------|
| **Event Handling** | 20+ event types | 1 response method |
| **State Management** | Complex synchronization | Stateless snapshots |
| **Error Recovery** | Missed events break state | Resilient snapshots |
| **Implementation** | 100s of lines | 10s of lines |
| **Debugging** | Complex event traces | Self-contained responses |
| **New Renderers** | Implement many methods | Implement one method |

## Response Object Richness

The `Response` object contains everything needed for rendering:

```python
response = Response(
    id="resp_123",
    status="completed",           # Current status
    model="gpt-4o",              # Model information  
    output=[                     # All content
        ResponseOutputMessage(
            content=[
                ResponseOutputText(
                    text="The answer is...",
                    annotations=[...]    # Citations inline
                )
            ]
        ),
        FileSearchToolCall(         # Tool execution results
            status="completed",
            queries=["search term"],
            results=[...]
        )
    ],
    usage=ResponseUsage(           # Token statistics
        input_tokens=100,
        output_tokens=200
    )
)
```

## Running the Demo

```bash
cd src/forge_cli/display/v3
python example.py
```

This will demonstrate:
- Rich terminal rendering
- Streaming updates
- Multiple renderer support
- Configuration options

## Implementing New Renderers

Creating a new renderer is simple - just implement one method:

```python
class MyRenderer(BaseRenderer):
    def render_response(self, response: Response) -> None:
        # Extract what you need from response
        text = response.output_text
        status = response.status
        citations = self._extract_citations(response)
        
        # Render however you want
        self._my_custom_output(text, status, citations)
    
    def finalize(self) -> None:
        # Cleanup if needed
        pass
```

## Future Renderers

The v3 architecture makes it easy to add:
- **PlainRenderer**: Simple text output
- **JsonRenderer**: Structured JSON output  
- **HtmlRenderer**: Web-ready HTML
- **MarkdownRenderer**: GitHub-flavored markdown
- **TelegramRenderer**: Chat bot formatting
- **SlackRenderer**: Slack message formatting

Each requires implementing just one method: `render_response(response: Response)`!

---

**Key Insight**: v3 embraces the snapshot-based streaming design, making everything simpler, more reliable, and easier to extend. The complexity moves from the display layer (where it was hard to manage) to the Response object design (where it belongs). 