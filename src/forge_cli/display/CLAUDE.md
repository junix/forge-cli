# Display Module - Output Formatting Strategies

## Overview

The display module implements the Strategy pattern to provide multiple output formatting options for the Forge CLI. It separates presentation logic from business logic, allowing users to choose between rich terminal UI, plain text, or JSON output while maintaining consistent functionality across all formats.

## Directory Structure

```
display/
├── __init__.py          # Module exports
├── base.py              # Base display interface
├── rich_display.py      # Rich terminal UI with live updates
├── plain_display.py     # Simple text output
└── json_display.py      # Machine-readable JSON format
```

## Architecture & Design

### Design Patterns

1. **Strategy Pattern**: Core pattern - different display strategies for same content
2. **Template Method**: Base class defines structure, subclasses implement details
3. **Observer Pattern**: Displays react to processor events
4. **Facade Pattern**: Unified interface for complex display operations

### Display Strategy Selection

```python
# Strategy selection based on configuration
if config.json_output:
    display = JsonDisplay(config)
elif config.no_color or not sys.stdout.isatty():
    display = PlainDisplay(config)
else:
    display = RichDisplay(config)
```

## Component Details

### base.py - Base Display Interface

Defines the contract all display strategies must implement:

```python
class BaseDisplay(ABC):
    """Abstract base class for display strategies."""
    
    def __init__(self, config: SearchConfig):
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
    
    @abstractmethod
    def handle_reasoning_start(self) -> None:
        """Handle start of reasoning/thinking."""
        pass
    
    @abstractmethod
    def handle_reasoning_delta(self, text: str) -> None:
        """Handle reasoning text updates."""
        pass
    
    @abstractmethod
    def handle_tool_start(self, tool_type: str, tool_id: str, **kwargs) -> None:
        """Handle tool execution start."""
        pass
    
    @abstractmethod
    def handle_tool_complete(self, tool_id: str, results_count: int) -> None:
        """Handle tool completion."""
        pass
    
    @abstractmethod
    def handle_citation(self, citation_num: int, citation: Annotation) -> None:
        """Handle citation display."""
        pass
    
    @abstractmethod
    def handle_stream_complete(self) -> None:
        """Called when stream ends."""
        pass
    
    @abstractmethod
    def handle_error(self, error: str) -> None:
        """Handle error display."""
        pass
```

### rich_display.py - Rich Terminal UI

Provides an interactive, visually appealing terminal interface using the Rich library.

**Key Features:**

- Live updating panels
- Progress indicators
- Syntax highlighting
- Citation tables
- Tool execution visualization
- Markdown rendering

**Components:**

```python
class RichDisplay(BaseDisplay):
    def __init__(self, config: SearchConfig):
        super().__init__(config)
        self.console = Console(
            force_terminal=True,
            force_jupyter=False,
            width=120
        )
        self.layout = self._create_layout()
        self.live = Live(
            self.layout,
            console=self.console,
            refresh_per_second=10
        )
```

**Layout Structure:**

```
┌─────────────────────────────────────┐
│         Header (Title)              │
├─────────────────────────────────────┤
│     Thinking/Reasoning Panel        │
├─────────────────────────────────────┤
│      Tool Execution Panel           │
├─────────────────────────────────────┤
│        Response Panel               │
├─────────────────────────────────────┤
│       Citations Table               │
└─────────────────────────────────────┘
```

**Key Methods:**

```python
def handle_text_delta(self, text: str):
    """Update response panel with streaming text."""
    self.response_text += text
    self._update_response_panel()
    
def handle_tool_start(self, tool_type: str, tool_id: str, **kwargs):
    """Show tool execution with spinner."""
    self.active_tools[tool_id] = {
        "type": tool_type,
        "status": "running",
        "params": kwargs
    }
    self._update_tool_panel()

def handle_citation(self, citation_num: int, citation: Annotation):
    """Add citation to table."""
    self.citations.append({
        "num": citation_num,
        "citation": citation
    })
    self._update_citation_table()
```

**Visual Elements:**

- **Spinners**: Show active operations
- **Progress bars**: Display completion status
- **Tables**: Format citations and results
- **Panels**: Organize content sections
- **Markdown**: Render formatted text

### plain_display.py - Plain Text Output

Simple, non-interactive text output suitable for logging, piping, and non-TTY environments.

**Key Features:**

- No color codes or formatting
- Linear output flow
- Minimal visual indicators
- Suitable for automation

**Implementation:**

```python
class PlainDisplay(BaseDisplay):
    def handle_text_delta(self, text: str):
        """Direct text output."""
        print(text, end="", flush=True)
    
    def handle_tool_start(self, tool_type: str, tool_id: str, **kwargs):
        """Simple status message."""
        print(f"\n[{tool_type.upper()}] Starting...")
    
    def handle_citation(self, citation_num: int, citation: Annotation):
        """Plain citation format."""
        print(f"\n[{citation_num}] {self._format_citation(citation)}")
```

**Output Format:**

```
Thinking...
[FILE_SEARCH] Starting...
[FILE_SEARCH] Complete (found 5 results)

Here is the response text with citations [1] and [2].

Citations:
[1] document.pdf (page 42): "Quote from document"
[2] report.md: "Another quote"
```

### json_display.py - JSON Format Output

Machine-readable JSON output for programmatic consumption.

**Key Features:**

- Structured data output
- Event stream capture
- Complete state serialization
- API-compatible format

**Implementation:**

```python
class JsonDisplay(BaseDisplay):
    def __init__(self, config: SearchConfig):
        super().__init__(config)
        self.events = []
        self.state = {
            "status": "started",
            "text": "",
            "tools": {},
            "citations": [],
            "reasoning": ""
        }
    
    def handle_text_delta(self, text: str):
        """Accumulate text."""
        self.state["text"] += text
        self._add_event("text_delta", {"text": text})
    
    def handle_stream_complete(self):
        """Output final JSON."""
        self.state["status"] = "completed"
        self.state["duration"] = time.time() - self.start_time
        
        output = {
            "response": self.state,
            "events": self.events if self.config.debug else []
        }
        
        print(json.dumps(output, indent=2))
```

**Output Structure:**

```json
{
  "response": {
    "status": "completed",
    "text": "Response text here",
    "tools": {
      "file_search_123": {
        "type": "file_search",
        "status": "completed",
        "results": 5
      }
    },
    "citations": [
      {
        "num": 1,
        "type": "file_citation",
        "file_id": "file_abc",
        "quote": "Citation text"
      }
    ],
    "reasoning": "Thinking process...",
    "duration": 3.456
  },
  "events": []  // Full event stream if debug=true
}
```

## Usage Guidelines

### For Language Models

When implementing or extending displays:

1. **Creating a new display strategy**:

```python
from .base import BaseDisplay
from forge_cli.config import SearchConfig

class CustomDisplay(BaseDisplay):
    def __init__(self, config: SearchConfig):
        super().__init__(config)
        # Initialize display-specific state
    
    def handle_text_delta(self, text: str):
        # Implement text handling
        pass
    
    # Implement all abstract methods
```

2. **Handling different content types**:

```python
def handle_tool_start(self, tool_type: str, tool_id: str, **kwargs):
    if tool_type == "file_search":
        query = kwargs.get("query", "")
        stores = kwargs.get("vector_stores", [])
        # Display file search info
    elif tool_type == "web_search":
        query = kwargs.get("query", "")
        location = kwargs.get("location", {})
        # Display web search info
```

3. **Managing state**:

```python
class StatefulDisplay(BaseDisplay):
    def __init__(self, config: SearchConfig):
        super().__init__(config)
        self.response_text = ""
        self.citations = []
        self.active_tools = {}
        self.reasoning_text = ""
    
    def handle_text_delta(self, text: str):
        self.response_text += text
        self._render()  # Update display
```

## Development Guidelines

### Adding New Display Strategies

1. **Inherit from BaseDisplay**:

```python
from .base import BaseDisplay

class NewDisplay(BaseDisplay):
    """New display strategy description."""
    pass
```

2. **Implement all abstract methods**:

- Use IDE to generate method stubs
- Ensure consistent behavior with other displays

3. **Export from **init**.py**:

```python
from .new_display import NewDisplay
__all__ = [..., "NewDisplay"]
```

4. **Add to strategy selection**:

```python
# In main.py or config handler
if config.new_format:
    display = NewDisplay(config)
```

### Display Best Practices

1. **State Management**:
   - Track all relevant state
   - Update incrementally for performance
   - Clear state between sessions

2. **Error Handling**:

```python
def handle_error(self, error: str):
    # Always show errors clearly
    self._show_error(f"Error: {error}")
    
    # Log for debugging
    if self.config.debug:
        self._show_traceback()
```

3. **Performance Optimization**:
   - Batch updates when possible
   - Throttle refresh rates
   - Minimize redraws

4. **User Experience**:
   - Provide clear feedback
   - Show progress for long operations
   - Format output readably

### Common Patterns

#### Progress Indication

```python
def show_progress(self, current: int, total: int, message: str):
    if isinstance(self, RichDisplay):
        self.progress_bar.update(task_id, completed=current)
    elif isinstance(self, PlainDisplay):
        print(f"\r{message}: {current}/{total}", end="")
    elif isinstance(self, JsonDisplay):
        self._add_event("progress", {
            "current": current,
            "total": total,
            "message": message
        })
```

#### Citation Formatting

```python
def format_citation(self, citation: Annotation) -> str:
    if isinstance(citation, FileCitationAnnotation):
        return f"{citation.file_name} (page {citation.page_number}): \"{citation.quote}\""
    elif isinstance(citation, UrlCitationAnnotation):
        return f"{citation.title} - {citation.url}"
```

## Testing Display Strategies

```python
import pytest
from io import StringIO
from unittest.mock import Mock, patch

def test_plain_display_text_output():
    config = Mock(debug=False)
    display = PlainDisplay(config)
    
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        display.handle_text_delta("Hello ")
        display.handle_text_delta("World")
        
        output = mock_stdout.getvalue()
        assert output == "Hello World"

def test_json_display_structure():
    config = Mock(debug=False)
    display = JsonDisplay(config)
    
    display.handle_text_delta("Test")
    display.handle_citation(1, Mock(spec=FileCitationAnnotation))
    display.handle_stream_complete()
    
    # Verify JSON structure
    assert display.state["text"] == "Test"
    assert len(display.state["citations"]) == 1
```

## Configuration Options

Displays respect these configuration options:

```python
class SearchConfig:
    # Display selection
    json_output: bool = False
    no_color: bool = False
    
    # Display behavior
    debug: bool = False
    quiet: bool = False
    throttle_ms: int = 0
    
    # Rich display options
    show_reasoning: bool = True
    show_citations: bool = True
    markdown_rendering: bool = True
```

## Performance Considerations

1. **Rich Display**:
   - Higher CPU usage for rendering
   - Best for interactive use
   - Throttle updates for remote terminals

2. **Plain Display**:
   - Minimal overhead
   - Best for logging/automation
   - No buffering needed

3. **JSON Display**:
   - Memory usage grows with events
   - Batch output at end
   - Consider streaming JSON for large responses

The display module provides flexible output options while maintaining a consistent interface, allowing users to choose the most appropriate format for their use case without changing the underlying functionality.
