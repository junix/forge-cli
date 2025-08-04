# Plaintext Renderer - Simple Text Output Module

## Overview

The plaintext renderer provides simple, clean text output for the Forge CLI application. It implements the V3 snapshot-based display architecture with a modular design that supports basic terminals, automation scripts, and environments where rich formatting is not available or desired.

## Directory Structure

```
plaintext/
├── CLAUDE.md                    # This documentation file
├── README.md                    # Plaintext renderer overview
├── __init__.py                  # Module exports
├── citations.py                 # Citation formatting
├── config.py                    # Configuration and settings
├── message_content.py           # Message content rendering
├── reasoning.py                 # Reasoning block rendering
├── render.py                    # Main rendering logic
├── styles.py                    # Text styling utilities
├── usage.py                     # Usage statistics rendering
├── welcome.py                   # Welcome message rendering
└── tools/                       # Tool-specific renderers
    ├── __init__.py              # Tool renderer exports
    ├── file_search.py           # File search tool renderer
    ├── web_search.py            # Web search tool renderer
    ├── function_call.py         # Function call renderer
    └── [other tool renderers]   # Additional tool renderers
```

## Architecture & Design

### Design Principles

1. **Simplicity**: Clean, readable text output without complex formatting
2. **Compatibility**: Works in any terminal environment
3. **Automation Friendly**: Suitable for scripts and automation
4. **Modular Design**: Separate components for different content types
5. **Performance**: Fast rendering with minimal overhead

### Modular Architecture

The plaintext renderer uses a modular architecture where each component handles specific content types:

```python
# Main renderer coordinates all modules
class PlaintextRenderer:
    def __init__(self):
        self.citation_renderer = CitationRenderer()
        self.message_renderer = MessageRenderer()
        self.reasoning_renderer = ReasoningRenderer()
        self.tool_renderer = ToolRenderer()
        self.usage_renderer = UsageRenderer()
    
    def render_response(self, response: Response) -> None:
        # Coordinate rendering across modules
        for item in response.output:
            if is_message_item(item):
                self.message_renderer.render(item)
            elif is_reasoning_item(item):
                self.reasoning_renderer.render(item)
            elif is_tool_call(item):
                self.tool_renderer.render(item)
```

## Core Components

### Main Rendering (render.py)

The main rendering coordinator that orchestrates all plaintext output:

**Key Features:**
- **Response Coordination**: Manages rendering of complete responses
- **Module Integration**: Coordinates between different rendering modules
- **Output Formatting**: Applies consistent formatting across all content
- **Error Handling**: Graceful handling of rendering errors

**Usage Example:**
```python
from forge_cli.display.v3.renderers.plaintext.render import PlaintextRenderer

renderer = PlaintextRenderer()
renderer.render_response(response)
renderer.finalize()
```

### Message Content (message_content.py)

Handles rendering of final assistant messages:

**Features:**
- **Plain Text Formatting**: Clean text output without markup
- **Citation Integration**: Inline citation references
- **Content Wrapping**: Text wrapping for readability
- **Markdown Conversion**: Convert markdown to plain text

### Reasoning Display (reasoning.py)

Renders AI reasoning and thinking blocks:

**Features:**
- **Thinking Blocks**: Clear display of AI reasoning
- **Section Headers**: Organized reasoning sections
- **Content Formatting**: Readable reasoning content
- **Summary Display**: Reasoning summaries

### Citation Formatting (citations.py)

Handles citation display and reference formatting:

**Features:**
- **Citation Tables**: Simple text tables for citations
- **Reference Numbers**: Clear citation numbering
- **File Information**: Document and page references
- **Compact Display**: Space-efficient citation format

**Example Output:**
```
Citations:
[1] document1.pdf, Page 5, File: file_123
[2] document2.pdf, Page 10, File: file_456
[3] research.docx, Page 2, File: file_789
```

### Text Styling (styles.py)

Provides text styling utilities for plaintext output:

**Features:**
- **ASCII Art**: Simple ASCII decorations
- **Text Alignment**: Left, center, right alignment
- **Borders**: Simple text borders and separators
- **Emphasis**: Basic text emphasis using characters

**Example Styling:**
```python
def create_section_header(title: str) -> str:
    """Create a section header with ASCII decoration."""
    border = "=" * len(title)
    return f"\n{border}\n{title}\n{border}\n"

def create_subsection_header(title: str) -> str:
    """Create a subsection header."""
    return f"\n--- {title} ---\n"

def emphasize_text(text: str) -> str:
    """Add emphasis to text using asterisks."""
    return f"*{text}*"
```

### Configuration (config.py)

Configuration options for plaintext rendering:

**Configuration Options:**
- **Line Width**: Maximum line width for text wrapping
- **Indentation**: Indentation levels for nested content
- **Separators**: Character choices for separators and borders
- **Timestamps**: Whether to show timestamps
- **Verbose Mode**: Level of detail in output

### Tool Renderers (tools/)

Specialized renderers for different tool types:

#### File Search Renderer (tools/file_search.py)
```python
def render_file_search(call: ResponseFileSearchToolCall) -> str:
    """Render file search tool call."""
    output = []
    output.append("📄 File Search")
    
    for query in call.queries:
        output.append(f"  Query: {query}")
    
    if call.status == "completed":
        output.append("  Status: ✅ Completed")
    elif call.status == "in_progress":
        output.append("  Status: ⏳ In Progress")
    
    return "\n".join(output)
```

#### Web Search Renderer (tools/web_search.py)
```python
def render_web_search(call: ResponseFunctionWebSearch) -> str:
    """Render web search tool call."""
    output = []
    output.append("🌐 Web Search")
    
    for query in call.queries:
        output.append(f"  Query: {query}")
    
    output.append(f"  Status: {call.status}")
    
    return "\n".join(output)
```

## Usage Examples

### Basic Rendering

```python
from forge_cli.display.v3.renderers.plaintext import PlaintextRenderer

# Create renderer
renderer = PlaintextRenderer()

# Render response
renderer.render_response(response)

# Finalize output
renderer.finalize()
```

### Custom Configuration

```python
from forge_cli.display.v3.renderers.plaintext.config import PlaintextConfig
from forge_cli.display.v3.renderers.plaintext import PlaintextRenderer

# Custom configuration
config = PlaintextConfig(
    max_width=100,
    show_timestamps=True,
    verbose_mode=True,
    indent_size=4
)

# Create renderer with config
renderer = PlaintextRenderer(config=config)
```

### Standalone Component Usage

```python
from forge_cli.display.v3.renderers.plaintext.citations import format_citations
from forge_cli.display.v3.renderers.plaintext.styles import create_section_header

# Format citations
citation_text = format_citations(citations)
print(citation_text)

# Create styled headers
header = create_section_header("Results")
print(header)
```

## Output Examples

### Complete Response Output

```
=====================================
Response from Knowledge Forge API
=====================================

📄 File Search
  Query: machine learning algorithms
  Status: ✅ Completed

--- Assistant Response ---

Machine learning algorithms can be broadly categorized into three main types: supervised learning, unsupervised learning, and reinforcement learning [1].

Supervised learning algorithms learn from labeled training data to make predictions on new, unseen data. Common examples include linear regression, decision trees, and neural networks [2].

Citations:
[1] ml_textbook.pdf, Page 15, File: file_123
[2] algorithms_guide.pdf, Page 42, File: file_456

--- Usage Statistics ---
Tokens Used: 150
Processing Time: 2.3 seconds
```

### Tool Execution Display

```
🌐 Web Search
  Query: latest AI developments 2024
  Status: ⏳ Searching...

📄 File Search  
  Query: neural network architectures
  Status: ✅ Completed

⚙️ Function Call: analyze_data
  Arguments: {"dataset": "research_data.csv"}
  Status: ✅ Completed
```

## Integration Points

### V3 Display Architecture

The plaintext renderer integrates with the V3 display system:

```python
from forge_cli.display.v3.base import Display
from forge_cli.display.v3.renderers.plaintext import PlaintextRenderer

# Create display with plaintext renderer
renderer = PlaintextRenderer()
display = Display(renderer)

# Handle response
display.handle_response(response)
display.complete()
```

### CLI Integration

```python
# In main CLI
if args.render == "plaintext":
    renderer = PlaintextRenderer()
elif args.render == "rich":
    renderer = RichRenderer()
else:
    renderer = PlaintextRenderer()  # Default fallback
```

## Related Components

- **V3 Base Display** (`../base.py`) - Display coordinator
- **Rich Renderer** (`../rich/`) - Rich terminal alternative
- **JSON Renderer** (`../json.py`) - Machine-readable alternative
- **Style Module** (`../../../../style/`) - Shared styling utilities

## Best Practices

### Plaintext Design

1. **Keep It Simple**: Avoid complex formatting that might not render correctly
2. **Wide Compatibility**: Ensure output works in all terminal environments
3. **Readable Layout**: Use whitespace and simple separators effectively
4. **Consistent Formatting**: Apply consistent patterns across all content types
5. **Automation Friendly**: Design output that's easy to parse programmatically

### Implementation

1. **Modular Components**: Keep rendering components focused and reusable
2. **Configuration Support**: Allow customization of formatting options
3. **Error Handling**: Handle rendering errors gracefully
4. **Performance**: Optimize for fast text processing
5. **Testing**: Include tests for different terminal environments

The plaintext renderer provides a reliable, simple alternative for environments where rich formatting is not available, ensuring that the Forge CLI works effectively across all terminal types and automation scenarios.
