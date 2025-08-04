# Rich Renderer - Advanced Terminal UI Module

## Overview

The Rich renderer provides advanced terminal UI capabilities for the Forge CLI application. It implements the V3 snapshot-based display architecture with rich formatting, colors, live updates, progress bars, and interactive elements that create an engaging user experience in modern terminals.

## Directory Structure

```
rich/
├── CLAUDE.md                    # This documentation file
├── __init__.py                  # Module exports
├── citations.py                 # Rich citation table formatting
├── message_content.py           # Rich message content rendering
├── reason.py                    # Rich reasoning block display
├── render.py                    # Main Rich rendering logic
├── usage.py                     # Rich usage statistics display
├── welcome.py                   # Rich welcome screen
└── tools/                       # Rich tool-specific renderers
    ├── __init__.py              # Tool renderer exports
    ├── file_search.py           # Rich file search renderer
    ├── web_search.py            # Rich web search renderer
    ├── function_call.py         # Rich function call renderer
    └── [other tool renderers]   # Additional rich tool renderers
```

## Architecture & Design

### Design Principles

1. **Rich Visual Experience**: Leverage Rich library for beautiful terminal UI
2. **Live Updates**: Real-time display updates during streaming responses
3. **Interactive Elements**: Progress bars, status indicators, and visual feedback
4. **Color and Typography**: Thoughtful use of colors and text styling
5. **Responsive Design**: Adapts to different terminal sizes and capabilities

### Rich Library Integration

The Rich renderer leverages the Rich Python library for advanced terminal features:

```python
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.progress import Progress
from rich.markdown import Markdown

class RichRenderer:
    def __init__(self):
        self.console = Console()
        self.live = None
        self.progress = Progress()
    
    def render_response(self, response: Response) -> None:
        with Live(console=self.console, refresh_per_second=10) as live:
            self._render_with_live_updates(response, live)
```

## Core Components

### Main Rendering (render.py)

The main Rich rendering coordinator with live update capabilities:

**Key Features:**
- **Live Display**: Real-time updates using Rich Live display
- **Layout Management**: Organized layout with panels and sections
- **Color Theming**: Consistent color scheme throughout
- **Progress Tracking**: Visual progress indicators for operations
- **Error Display**: Rich error formatting and display

**Usage Example:**
```python
from forge_cli.display.v3.renderers.rich.render import RichRenderer

renderer = RichRenderer()
renderer.render_response(response)
renderer.finalize()
```

### Citation Display (citations.py)

Rich table formatting for citations and references:

**Features:**
- **Rich Tables**: Beautiful tables with borders and styling
- **Color Coding**: Color-coded citation information
- **Sortable Columns**: Organized citation data
- **Compact Display**: Efficient use of terminal space

**Example Implementation:**
```python
from rich.table import Table
from rich.console import Console

def create_citation_table(citations: List[Citation]) -> Table:
    """Create a rich table for citations."""
    table = Table(title="📚 Citations", show_header=True, header_style="bold blue")
    
    table.add_column("#", style="dim", width=3)
    table.add_column("Document", style="cyan")
    table.add_column("Page", justify="center", style="magenta")
    table.add_column("File ID", style="dim")
    
    for i, citation in enumerate(citations, 1):
        table.add_row(
            f"[{i}]",
            citation.document_name or "Unknown",
            str(citation.page_number) if citation.page_number else "N/A",
            citation.file_id or "N/A"
        )
    
    return table
```

### Message Content (message_content.py)

Rich formatting for assistant messages:

**Features:**
- **Markdown Rendering**: Rich markdown display with syntax highlighting
- **Code Blocks**: Syntax-highlighted code blocks
- **Inline Citations**: Styled citation references
- **Typography**: Beautiful text formatting and spacing

### Reasoning Display (reason.py)

Rich display for AI reasoning and thinking:

**Features:**
- **Collapsible Sections**: Expandable reasoning blocks
- **Syntax Highlighting**: Highlighted reasoning content
- **Visual Hierarchy**: Clear visual organization
- **Progress Indicators**: Show reasoning progress

### Usage Statistics (usage.py)

Rich display for usage and performance metrics:

**Features:**
- **Metrics Dashboard**: Visual metrics display
- **Progress Bars**: Token usage progress bars
- **Color Coding**: Color-coded performance indicators
- **Charts**: Simple ASCII charts for trends

**Example Implementation:**
```python
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn

def create_usage_panel(usage: ResponseUsage) -> Panel:
    """Create a rich panel for usage statistics."""
    content = []
    
    # Token usage
    if usage.total_tokens:
        content.append(f"🔢 Total Tokens: [bold cyan]{usage.total_tokens}[/bold cyan]")
    
    if usage.prompt_tokens:
        content.append(f"📝 Prompt Tokens: [green]{usage.prompt_tokens}[/green]")
    
    if usage.completion_tokens:
        content.append(f"💬 Completion Tokens: [blue]{usage.completion_tokens}[/blue]")
    
    # Create progress bar for token usage
    if usage.total_tokens and usage.total_tokens > 0:
        progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )
        
        # Add token usage progress
        task = progress.add_task("Token Usage", total=100)
        progress.update(task, completed=min(usage.total_tokens / 1000 * 100, 100))
    
    return Panel(
        "\n".join(content),
        title="📊 Usage Statistics",
        border_style="green"
    )
```

### Welcome Screen (welcome.py)

Rich welcome screen and branding:

**Features:**
- **ASCII Art**: Stylized logo and branding
- **Color Gradients**: Beautiful color transitions
- **Animation**: Subtle animations and effects
- **Information Display**: Version and configuration info

### Tool Renderers (tools/)

Rich renderers for different tool types:

#### File Search Renderer (tools/file_search.py)
```python
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

def render_file_search_rich(call: ResponseFileSearchToolCall) -> Panel:
    """Render file search with rich formatting."""
    content = []
    
    # Status indicator
    if call.status == "completed":
        status_icon = "✅"
        status_color = "green"
    elif call.status == "in_progress":
        status_icon = "⏳"
        status_color = "yellow"
    else:
        status_icon = "❌"
        status_color = "red"
    
    content.append(f"Status: [{status_color}]{status_icon} {call.status.title()}[/{status_color}]")
    
    # Queries
    content.append("\n[bold]Queries:[/bold]")
    for query in call.queries:
        content.append(f"  • [cyan]{query}[/cyan]")
    
    return Panel(
        "\n".join(content),
        title="📄 File Search",
        border_style="blue"
    )
```

#### Web Search Renderer (tools/web_search.py)
```python
def render_web_search_rich(call: ResponseFunctionWebSearch) -> Panel:
    """Render web search with rich formatting."""
    content = []
    
    # Search queries
    content.append("[bold]Search Queries:[/bold]")
    for query in call.queries:
        content.append(f"  🔍 [green]{query}[/green]")
    
    # Status
    content.append(f"\nStatus: [yellow]{call.status}[/yellow]")
    
    return Panel(
        "\n".join(content),
        title="🌐 Web Search",
        border_style="cyan"
    )
```

## Advanced Features

### Live Updates

```python
from rich.live import Live
from rich.layout import Layout

class LiveRichRenderer:
    """Rich renderer with live updates."""
    
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        
    def render_with_live_updates(self, response_stream):
        """Render with live updates during streaming."""
        with Live(self.layout, console=self.console, refresh_per_second=10) as live:
            for event in response_stream:
                if is_text_delta_event(event):
                    self.update_text_display(event.delta)
                elif is_tool_event(event):
                    self.update_tool_display(event)
                
                live.update(self.layout)
```

### Progress Tracking

```python
from rich.progress import Progress, TaskID

class ProgressTracker:
    """Track progress for long-running operations."""
    
    def __init__(self):
        self.progress = Progress()
        self.tasks: Dict[str, TaskID] = {}
    
    def start_task(self, task_id: str, description: str, total: int = 100):
        """Start tracking a task."""
        task = self.progress.add_task(description, total=total)
        self.tasks[task_id] = task
    
    def update_task(self, task_id: str, completed: int):
        """Update task progress."""
        if task_id in self.tasks:
            self.progress.update(self.tasks[task_id], completed=completed)
```

### Theming and Customization

```python
from rich.theme import Theme
from rich.console import Console

# Custom theme
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "success": "green bold",
    "citation": "blue",
    "tool": "magenta",
    "reasoning": "dim cyan"
})

# Create console with theme
console = Console(theme=custom_theme)
```

## Usage Examples

### Basic Rich Rendering

```python
from forge_cli.display.v3.renderers.rich import RichRenderer

# Create rich renderer
renderer = RichRenderer()

# Render response with rich formatting
renderer.render_response(response)
renderer.finalize()
```

### Custom Styling

```python
from rich.console import Console
from rich.theme import Theme

# Custom theme
theme = Theme({
    "primary": "bold blue",
    "secondary": "cyan",
    "success": "green",
    "warning": "yellow",
    "error": "red bold"
})

# Create renderer with custom theme
console = Console(theme=theme)
renderer = RichRenderer(console=console)
```

### Live Streaming Display

```python
from forge_cli.display.v3.renderers.rich import RichRenderer
from rich.live import Live

renderer = RichRenderer()

# Stream response with live updates
with Live(console=renderer.console) as live:
    for event in response_stream:
        renderer.handle_stream_event(event)
        live.update(renderer.get_current_display())
```

## Integration Points

### V3 Display Architecture

```python
from forge_cli.display.v3.base import Display
from forge_cli.display.v3.renderers.rich import RichRenderer

# Create display with rich renderer
renderer = RichRenderer()
display = Display(renderer)

# Handle response with rich formatting
display.handle_response(response)
display.complete()
```

### CLI Integration

```python
# In main CLI
if args.render == "rich" or (args.render is None and supports_rich()):
    renderer = RichRenderer()
else:
    renderer = PlaintextRenderer()  # Fallback
```

## Related Components

- **V3 Base Display** (`../base.py`) - Display coordinator
- **Plaintext Renderer** (`../plaintext/`) - Simple text alternative
- **JSON Renderer** (`../json.py`) - Machine-readable alternative
- **Rich Library** - External dependency for rich terminal features

## Best Practices

### Rich Design

1. **Visual Hierarchy**: Use colors and styling to create clear visual hierarchy
2. **Performance**: Optimize for smooth live updates and responsiveness
3. **Accessibility**: Ensure colors work for users with color vision differences
4. **Graceful Degradation**: Fallback to simpler display when Rich features unavailable
5. **Consistent Theming**: Apply consistent color scheme and styling throughout

### Implementation

1. **Modular Components**: Keep Rich components focused and reusable
2. **Error Handling**: Handle Rich rendering errors gracefully
3. **Terminal Detection**: Detect terminal capabilities and adjust accordingly
4. **Memory Management**: Manage Rich objects efficiently for performance
5. **Testing**: Test across different terminal types and sizes

The Rich renderer provides a beautiful, interactive terminal experience that makes the Forge CLI engaging and professional while maintaining the reliability and functionality of the V3 display architecture.
