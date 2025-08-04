# Style Module - Formatting and Presentation Utilities

## Overview

The style module provides formatting and presentation utilities for the Forge CLI application. It contains functions and classes for styling text output, markdown processing, and visual formatting that enhance the user experience across different display modes.

## Directory Structure

```
style/
├── CLAUDE.md                    # This documentation file
├── __init__.py                  # Module exports
└── markdowns.py                 # Markdown processing and formatting
```

## Architecture & Design

### Design Principles

1. **Consistent Styling**: Standardized formatting across all output modes
2. **Markdown Support**: Rich markdown processing for enhanced readability
3. **Cross-Platform Compatibility**: Works across different terminal environments
4. **Performance**: Efficient text processing for real-time applications
5. **Extensibility**: Easy to add new formatting styles and options

### Core Components

#### markdowns.py - Markdown Processing

Provides comprehensive markdown processing and formatting capabilities:

**Key Features:**
- **Citation Processing**: Convert citation markers to formatted references
- **Table Formatting**: Format markdown tables for different output modes
- **Text Styling**: Apply consistent text styling and formatting
- **Link Processing**: Handle URLs and file references
- **Code Highlighting**: Syntax highlighting for code blocks

## Markdown Processing

### Citation Formatting

The style module handles citation processing for file search results:

```python
def process_citations(text: str, citations: List[Citation]) -> str:
    """Process citation markers in text and format references."""
    
    # Convert Unicode citation markers to markdown format
    # ⟦⟦1⟧⟧ → [1]
    citation_pattern = r'⟦⟦(\d+)⟧⟧'
    
    def replace_citation(match):
        citation_num = match.group(1)
        return f"[{citation_num}]"
    
    # Replace citation markers
    formatted_text = re.sub(citation_pattern, replace_citation, text)
    
    # Add citation table if citations exist
    if citations:
        citation_table = format_citation_table(citations)
        formatted_text += "\n\n" + citation_table
    
    return formatted_text

def format_citation_table(citations: List[Citation]) -> str:
    """Format citations as a markdown table."""
    if not citations:
        return ""
    
    table = "| Citation | Document | Page | File ID |\n"
    table += "|----------|----------|------|---------|\n"
    
    for i, citation in enumerate(citations, 1):
        doc_name = citation.document_name or "Unknown"
        page = citation.page_number or "N/A"
        file_id = citation.file_id or "N/A"
        
        table += f"| [{i}] | {doc_name} | {page} | {file_id} |\n"
    
    return table
```

### Text Styling Utilities

```python
def apply_text_styling(text: str, style: str = "default") -> str:
    """Apply text styling based on style type."""
    
    styling_rules = {
        "default": {
            "bold": "**{}**",
            "italic": "*{}*",
            "code": "`{}`",
            "header": "## {}",
        },
        "rich": {
            "bold": "[bold]{}[/bold]",
            "italic": "[italic]{}[/italic]",
            "code": "[code]{}[/code]",
            "header": "[bold blue]## {}[/bold blue]",
        },
        "plain": {
            "bold": "{}",
            "italic": "{}",
            "code": "{}",
            "header": "## {}",
        }
    }
    
    rules = styling_rules.get(style, styling_rules["default"])
    
    # Apply styling rules to text
    # Implementation depends on specific styling needs
    return apply_styling_rules(text, rules)

def apply_styling_rules(text: str, rules: Dict[str, str]) -> str:
    """Apply styling rules to text content."""
    # Pattern matching and replacement logic
    # This would include regex patterns for different markdown elements
    pass
```

### Code Block Processing

```python
def format_code_blocks(text: str, language: str = None) -> str:
    """Format code blocks with optional syntax highlighting."""
    
    # Detect code blocks
    code_block_pattern = r'```(\w+)?\n(.*?)\n```'
    
    def format_code_block(match):
        lang = match.group(1) or language or "text"
        code = match.group(2)
        
        # Apply syntax highlighting if available
        if has_syntax_highlighting():
            return highlight_code(code, lang)
        else:
            return f"```{lang}\n{code}\n```"
    
    return re.sub(code_block_pattern, format_code_block, text, flags=re.DOTALL)

def highlight_code(code: str, language: str) -> str:
    """Apply syntax highlighting to code."""
    try:
        from pygments import highlight
        from pygments.lexers import get_lexer_by_name
        from pygments.formatters import TerminalFormatter
        
        lexer = get_lexer_by_name(language)
        formatter = TerminalFormatter()
        return highlight(code, lexer, formatter)
    except ImportError:
        # Fallback to plain code block
        return f"```{language}\n{code}\n```"
```

## Formatting Utilities

### Table Formatting

```python
def format_table(headers: List[str], rows: List[List[str]], style: str = "markdown") -> str:
    """Format data as a table in specified style."""
    
    if style == "markdown":
        return format_markdown_table(headers, rows)
    elif style == "ascii":
        return format_ascii_table(headers, rows)
    elif style == "simple":
        return format_simple_table(headers, rows)
    else:
        return format_markdown_table(headers, rows)

def format_markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    """Format as markdown table."""
    if not headers or not rows:
        return ""
    
    # Calculate column widths
    col_widths = [len(header) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Format header
    header_row = "| " + " | ".join(header.ljust(col_widths[i]) for i, header in enumerate(headers)) + " |"
    separator = "|" + "|".join("-" * (width + 2) for width in col_widths) + "|"
    
    # Format data rows
    data_rows = []
    for row in rows:
        formatted_row = "| " + " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)) + " |"
        data_rows.append(formatted_row)
    
    return "\n".join([header_row, separator] + data_rows)

def format_ascii_table(headers: List[str], rows: List[List[str]]) -> str:
    """Format as ASCII art table."""
    # ASCII table formatting with borders
    pass

def format_simple_table(headers: List[str], rows: List[List[str]]) -> str:
    """Format as simple aligned text."""
    # Simple column alignment without borders
    pass
```

### Text Alignment and Wrapping

```python
def wrap_text(text: str, width: int = 80, indent: int = 0) -> str:
    """Wrap text to specified width with optional indentation."""
    import textwrap
    
    wrapper = textwrap.TextWrapper(
        width=width,
        initial_indent=" " * indent,
        subsequent_indent=" " * indent,
        break_long_words=False,
        break_on_hyphens=False
    )
    
    return wrapper.fill(text)

def align_text(text: str, alignment: str = "left", width: int = 80) -> str:
    """Align text within specified width."""
    lines = text.split('\n')
    aligned_lines = []
    
    for line in lines:
        if alignment == "center":
            aligned_lines.append(line.center(width))
        elif alignment == "right":
            aligned_lines.append(line.rjust(width))
        else:  # left alignment (default)
            aligned_lines.append(line.ljust(width))
    
    return '\n'.join(aligned_lines)
```

## Color and Terminal Support

### Color Utilities

```python
class Colors:
    """ANSI color codes for terminal output."""
    
    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    
    # Reset
    RESET = '\033[0m'

def colorize(text: str, color: str, style: str = None) -> str:
    """Apply color and style to text."""
    color_code = getattr(Colors, color.upper(), '')
    style_code = getattr(Colors, style.upper(), '') if style else ''
    
    return f"{style_code}{color_code}{text}{Colors.RESET}"

def strip_colors(text: str) -> str:
    """Remove ANSI color codes from text."""
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)
```

### Terminal Detection

```python
def supports_color() -> bool:
    """Check if terminal supports color output."""
    import os
    import sys
    
    # Check environment variables
    if os.getenv('NO_COLOR'):
        return False
    
    if os.getenv('FORCE_COLOR'):
        return True
    
    # Check if output is a TTY
    if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
        return False
    
    # Check TERM environment variable
    term = os.getenv('TERM', '')
    if term in ('dumb', 'unknown'):
        return False
    
    return True

def get_terminal_width() -> int:
    """Get terminal width in characters."""
    import shutil
    return shutil.get_terminal_size().columns
```

## Usage Examples

### Citation Processing

```python
from forge_cli.style.markdowns import process_citations

# Process text with citations
text_with_citations = "This is important ⟦⟦1⟧⟧ and so is this ⟦⟦2⟧⟧."
citations = [
    Citation(document_name="doc1.pdf", page_number=5, file_id="file_123"),
    Citation(document_name="doc2.pdf", page_number=10, file_id="file_456")
]

formatted_text = process_citations(text_with_citations, citations)
print(formatted_text)
```

### Table Formatting

```python
from forge_cli.style.markdowns import format_table

# Format data as table
headers = ["Name", "Type", "Size"]
rows = [
    ["document1.pdf", "PDF", "1.2MB"],
    ["document2.txt", "Text", "45KB"],
    ["document3.docx", "Word", "890KB"]
]

table = format_table(headers, rows, style="markdown")
print(table)
```

### Text Styling

```python
from forge_cli.style.markdowns import colorize, wrap_text

# Apply colors and wrapping
colored_text = colorize("Important message", "red", "bold")
wrapped_text = wrap_text("Long text that needs to be wrapped...", width=60, indent=4)
```

## Related Components

- **Display Renderers** (`../display/v3/renderers/`) - Use styling utilities for output formatting
- **Response Processing** (`../response/`) - Apply styling to response content
- **Chat Mode** (`../chat/`) - Use styling for chat interface elements
- **CLI** (`../cli/`) - Apply styling to command-line output

## Best Practices

### Styling Guidelines

1. **Consistent Formatting**: Use standardized formatting across all components
2. **Accessibility**: Ensure styling works across different terminal environments
3. **Performance**: Optimize text processing for real-time applications
4. **Fallbacks**: Provide fallbacks for environments without advanced formatting
5. **Testing**: Test styling across different terminal types and configurations

### Implementation Standards

1. **Type Safety**: Use proper type annotations for all functions
2. **Error Handling**: Handle formatting errors gracefully
3. **Configuration**: Support configuration for styling preferences
4. **Documentation**: Include examples and usage information
5. **Modularity**: Keep styling functions focused and reusable

The style module provides essential formatting and presentation capabilities that enhance the user experience across all display modes of the Forge CLI application.
