# Formatters Module - Data Formatting and Transformation

## Overview

The formatters module is designed to house specialized formatting functions for transforming data between different representations. While currently empty (containing only `__init__.py`), this module is reserved for future formatting utilities that handle complex data transformations, output formatting, and specialized rendering logic that goes beyond what the display strategies provide.

## Directory Structure

```
formatters/
└── __init__.py      # Module initialization (currently empty)
```

## Purpose and Design Philosophy

### Intended Use Cases

1. **Citation Formatting**: Convert citations to various academic formats
2. **Code Formatting**: Syntax highlighting and code beautification
3. **Table Formatting**: Advanced table generation and styling
4. **Export Formatting**: Convert responses to various file formats
5. **Markdown Extensions**: Custom markdown transformations
6. **Template Rendering**: Dynamic content generation
7. **Report Generation**: Structured document creation
8. **Data Serialization**: Custom serialization formats

### Design Principles

1. **Separation of Concerns**: Formatters handle pure transformation logic
2. **Composability**: Formatters can be chained together
3. **Extensibility**: Easy to add new format types
4. **Performance**: Efficient transformation algorithms
5. **Consistency**: Uniform API across formatters

## Planned Formatters

### Citation Formatter (`citation_formatter.py`)

```python
from typing import List, Dict, Any
from forge_cli.models import FileCitationAnnotation, UrlCitationAnnotation

class CitationFormatter:
    """Format citations in various academic styles."""
    
    def format_apa(self, citation: FileCitationAnnotation) -> str:
        """Format citation in APA style."""
        # Author. (Year). Title. Source. Page.
        return f"{citation.file_name}. (2024). {citation.quote[:50]}... p. {citation.page_number}"
    
    def format_mla(self, citation: FileCitationAnnotation) -> str:
        """Format citation in MLA style."""
        # Author. "Title." Source, Year, Page.
        return f'"{citation.quote[:50]}..." {citation.file_name}, 2024, p. {citation.page_number}.'
    
    def format_chicago(self, citation: FileCitationAnnotation) -> str:
        """Format citation in Chicago style."""
        # Author, "Title," Source (Year): Page.
        return f'"{citation.quote[:50]}...", {citation.file_name} (2024): {citation.page_number}.'
    
    def format_bibtex(self, citation: FileCitationAnnotation) -> str:
        """Format citation as BibTeX entry."""
        return f"""@misc{{{citation.file_id},
  title = {{{citation.file_name}}},
  year = {{2024}},
  note = {{Page {citation.page_number}}},
  howpublished = {{File ID: {citation.file_id}}}
}}"""

    def format_inline(self, citation: Any, number: int) -> str:
        """Format citation for inline display."""
        if isinstance(citation, FileCitationAnnotation):
            return f"[{number}] {citation.file_name} (p. {citation.page_number})"
        elif isinstance(citation, UrlCitationAnnotation):
            return f"[{number}] {citation.title} - {citation.url}"
        else:
            return f"[{number}] Unknown citation type"
```

### Table Formatter (`table_formatter.py`)

```python
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class TableStyle:
    """Table formatting style configuration."""
    border: str = "─"
    corner: str = "┌"
    separator: str = "│"
    header_separator: str = "═"
    padding: int = 1

class TableFormatter:
    """Advanced table formatting with various styles."""
    
    def __init__(self, style: Optional[TableStyle] = None):
        self.style = style or TableStyle()
    
    def format_markdown(self, 
                       headers: List[str], 
                       rows: List[List[str]],
                       alignment: Optional[List[str]] = None) -> str:
        """Format as markdown table."""
        # Build header
        header_row = "| " + " | ".join(headers) + " |"
        
        # Build alignment row
        alignment = alignment or ["left"] * len(headers)
        align_map = {"left": ":---", "center": ":---:", "right": "---:"}
        align_row = "| " + " | ".join(align_map.get(a, ":---") for a in alignment) + " |"
        
        # Build data rows
        data_rows = []
        for row in rows:
            data_rows.append("| " + " | ".join(str(cell) for cell in row) + " |")
        
        return "\n".join([header_row, align_row] + data_rows)
    
    def format_ascii(self,
                    headers: List[str],
                    rows: List[List[str]]) -> str:
        """Format as ASCII art table."""
        # Calculate column widths
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(str(cell)))
        
        # Add padding
        widths = [w + 2 * self.style.padding for w in widths]
        
        # Build table
        lines = []
        
        # Top border
        lines.append(self._build_border(widths, "top"))
        
        # Header
        lines.append(self._build_row(headers, widths))
        lines.append(self._build_border(widths, "middle"))
        
        # Data rows
        for row in rows:
            lines.append(self._build_row(row, widths))
        
        # Bottom border
        lines.append(self._build_border(widths, "bottom"))
        
        return "\n".join(lines)
    
    def format_csv(self,
                  headers: List[str],
                  rows: List[List[str]],
                  delimiter: str = ",") -> str:
        """Format as CSV."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output, delimiter=delimiter)
        
        writer.writerow(headers)
        writer.writerows(rows)
        
        return output.getvalue()
    
    def format_html(self,
                   headers: List[str],
                   rows: List[List[str]],
                   table_class: str = "data-table") -> str:
        """Format as HTML table."""
        html = [f'<table class="{table_class}">']
        
        # Header
        html.append("  <thead>")
        html.append("    <tr>")
        for header in headers:
            html.append(f"      <th>{header}</th>")
        html.append("    </tr>")
        html.append("  </thead>")
        
        # Body
        html.append("  <tbody>")
        for row in rows:
            html.append("    <tr>")
            for cell in row:
                html.append(f"      <td>{cell}</td>")
            html.append("    </tr>")
        html.append("  </tbody>")
        
        html.append("</table>")
        
        return "\n".join(html)
```

### Markdown Formatter (`markdown_formatter.py`)

```python
import re
from typing import Dict, List, Optional

class MarkdownFormatter:
    """Enhanced markdown formatting utilities."""
    
    def add_toc(self, markdown: str, max_level: int = 3) -> str:
        """Add table of contents to markdown."""
        lines = markdown.split('\n')
        headers = []
        
        # Extract headers
        for line in lines:
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                level = len(match.group(1))
                if level <= max_level:
                    title = match.group(2)
                    anchor = self._create_anchor(title)
                    headers.append((level, title, anchor))
        
        # Build TOC
        toc = ["## Table of Contents\n"]
        for level, title, anchor in headers:
            indent = "  " * (level - 1)
            toc.append(f"{indent}- [{title}](#{anchor})")
        
        # Insert TOC after first header
        first_header_idx = next(
            (i for i, line in enumerate(lines) if line.startswith('#')),
            0
        )
        
        lines[first_header_idx + 1:first_header_idx + 1] = ["\n".join(toc), ""]
        
        return "\n".join(lines)
    
    def add_line_numbers(self, code_block: str, language: str = "") -> str:
        """Add line numbers to code blocks."""
        lines = code_block.split('\n')
        numbered_lines = []
        
        for i, line in enumerate(lines, 1):
            numbered_lines.append(f"{i:4d} | {line}")
        
        return f"```{language}\n" + "\n".join(numbered_lines) + "\n```"
    
    def create_collapsible(self, summary: str, content: str) -> str:
        """Create collapsible section."""
        return f"""<details>
<summary>{summary}</summary>

{content}

</details>"""
    
    def highlight_changes(self, text: str, changes: List[Dict[str, Any]]) -> str:
        """Highlight changes in text."""
        for change in changes:
            if change['type'] == 'addition':
                text = text.replace(
                    change['text'],
                    f"<mark style='background-color: #90EE90'>{change['text']}</mark>"
                )
            elif change['type'] == 'deletion':
                text = text.replace(
                    change['text'],
                    f"<mark style='background-color: #FFB6C1'>{change['text']}</mark>"
                )
        
        return text
    
    def _create_anchor(self, title: str) -> str:
        """Create anchor from title."""
        # Remove special characters and convert to lowercase
        anchor = re.sub(r'[^\w\s-]', '', title.lower())
        anchor = re.sub(r'[-\s]+', '-', anchor)
        return anchor
```

### Export Formatter (`export_formatter.py`)

```python
import json
from typing import Dict, Any, List
from datetime import datetime

class ExportFormatter:
    """Format data for various export formats."""
    
    def to_pdf_report(self, 
                     data: Dict[str, Any],
                     template: str = "default") -> bytes:
        """Generate PDF report from data."""
        # This would use a PDF generation library
        # Placeholder implementation
        content = self._generate_report_content(data)
        return content.encode('utf-8')
    
    def to_excel(self,
                sheets: Dict[str, List[List[Any]]],
                formatting: Optional[Dict[str, Any]] = None) -> bytes:
        """Generate Excel file with multiple sheets."""
        # This would use openpyxl or similar
        # Placeholder implementation
        return b"Excel content"
    
    def to_json_report(self,
                      data: Dict[str, Any],
                      include_metadata: bool = True) -> str:
        """Generate structured JSON report."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "version": "1.0",
            "data": data
        }
        
        if include_metadata:
            report["metadata"] = {
                "total_items": self._count_items(data),
                "categories": self._extract_categories(data),
                "summary": self._generate_summary(data)
            }
        
        return json.dumps(report, indent=2, ensure_ascii=False)
    
    def to_xml(self,
              data: Dict[str, Any],
              root_element: str = "report") -> str:
        """Generate XML representation."""
        from xml.etree.ElementTree import Element, SubElement, tostring
        
        root = Element(root_element)
        self._dict_to_xml(data, root)
        
        return tostring(root, encoding='unicode')
    
    def _dict_to_xml(self, data: Dict[str, Any], parent: Element):
        """Convert dictionary to XML elements."""
        for key, value in data.items():
            if isinstance(value, dict):
                elem = SubElement(parent, key)
                self._dict_to_xml(value, elem)
            elif isinstance(value, list):
                for item in value:
                    elem = SubElement(parent, key)
                    if isinstance(item, dict):
                        self._dict_to_xml(item, elem)
                    else:
                        elem.text = str(item)
            else:
                elem = SubElement(parent, key)
                elem.text = str(value)
```

### Code Formatter (`code_formatter.py`)

```python
from typing import Optional, Dict, Any
import re

class CodeFormatter:
    """Format and beautify code snippets."""
    
    def __init__(self):
        self.language_configs = {
            'python': {
                'indent': '    ',
                'line_comment': '#',
                'block_comment': ('"""', '"""')
            },
            'javascript': {
                'indent': '  ',
                'line_comment': '//',
                'block_comment': ('/*', '*/')
            }
        }
    
    def add_syntax_highlighting(self, 
                              code: str,
                              language: str,
                              theme: str = "monokai") -> str:
        """Add syntax highlighting using pygments."""
        try:
            from pygments import highlight
            from pygments.lexers import get_lexer_by_name
            from pygments.formatters import HtmlFormatter
            
            lexer = get_lexer_by_name(language)
            formatter = HtmlFormatter(style=theme)
            
            return highlight(code, lexer, formatter)
        except ImportError:
            # Fallback to basic highlighting
            return f"```{language}\n{code}\n```"
    
    def format_diff(self, 
                   old_code: str,
                   new_code: str,
                   context_lines: int = 3) -> str:
        """Format code diff with context."""
        import difflib
        
        old_lines = old_code.splitlines(keepends=True)
        new_lines = new_code.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile='original',
            tofile='modified',
            n=context_lines
        )
        
        return ''.join(diff)
    
    def minify_code(self, code: str, language: str) -> str:
        """Minify code by removing unnecessary whitespace."""
        if language == 'javascript':
            # Remove comments
            code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
            code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
            
            # Remove extra whitespace
            code = re.sub(r'\s+', ' ', code)
            code = re.sub(r'\s*([{}();,:])\s*', r'\1', code)
            
        elif language == 'css':
            # Remove comments
            code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
            
            # Remove extra whitespace
            code = re.sub(r'\s+', ' ', code)
            code = re.sub(r'\s*([{}:;,])\s*', r'\1', code)
        
        return code.strip()
```

## Usage Guidelines

### For Language Models

When implementing formatters:

1. **Use appropriate formatter**:

```python
from forge_cli.formatters import CitationFormatter, TableFormatter

# Format citations
formatter = CitationFormatter()
apa_citation = formatter.format_apa(citation)

# Format table
table_formatter = TableFormatter()
markdown_table = table_formatter.format_markdown(
    headers=["Name", "Score"],
    rows=[["Alice", "95"], ["Bob", "87"]]
)
```

2. **Chain formatters**:

```python
# Process through multiple formatters
data = get_raw_data()
formatted = markdown_formatter.add_toc(data)
formatted = markdown_formatter.add_line_numbers(formatted)
final = export_formatter.to_pdf_report(formatted)
```

3. **Configure formatters**:

```python
# Custom table style
style = TableStyle(
    border="═",
    corner="╔",
    separator="║"
)
formatter = TableFormatter(style=style)
```

## Development Guidelines

### Adding New Formatters

1. **Create formatter class**:

```python
class NewFormatter:
    """Description of formatter purpose."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    def format(self, data: Any) -> str:
        """Main formatting method."""
        # Implementation
        pass
```

2. **Add to **init**.py**:

```python
from .new_formatter import NewFormatter

__all__ = [..., 'NewFormatter']
```

3. **Provide multiple output options**:

```python
def format_as_text(self, data: Any) -> str:
    """Plain text output."""
    pass

def format_as_html(self, data: Any) -> str:
    """HTML output."""
    pass

def format_as_json(self, data: Any) -> str:
    """JSON output."""
    pass
```

### Testing Formatters

```python
import pytest
from forge_cli.formatters import TableFormatter

def test_table_formatter_markdown():
    formatter = TableFormatter()
    
    result = formatter.format_markdown(
        headers=["A", "B"],
        rows=[["1", "2"], ["3", "4"]]
    )
    
    expected = """| A | B |
| :--- | :--- |
| 1 | 2 |
| 3 | 4 |"""
    
    assert result == expected

def test_citation_formatter_styles():
    formatter = CitationFormatter()
    citation = FileCitationAnnotation(
        file_id="123",
        file_name="test.pdf",
        quote="Sample quote",
        page_number=42
    )
    
    apa = formatter.format_apa(citation)
    assert "test.pdf" in apa
    assert "42" in apa
```

## Best Practices

1. **Preserve data integrity**: Never lose information during formatting
2. **Handle edge cases**: Empty data, special characters, etc.
3. **Provide options**: Allow customization of output
4. **Optimize performance**: Efficient algorithms for large data
5. **Maintain consistency**: Similar APIs across formatters
6. **Document formats**: Clear examples of output formats

## Integration with Display Module

Formatters complement display strategies:

```python
# Display uses formatter for specific content
class RichDisplay(BaseDisplay):
    def __init__(self):
        self.table_formatter = TableFormatter()
        self.citation_formatter = CitationFormatter()
    
    def display_citations(self, citations: List[Any]):
        # Use formatter for consistent output
        formatted = []
        for i, citation in enumerate(citations, 1):
            formatted.append(
                self.citation_formatter.format_inline(citation, i)
            )
        
        # Display formatted citations
        self.show_panel("\n".join(formatted))
```

## Future Enhancements

1. **Template Engine**: Jinja2-based templating
2. **Graph Formatters**: Mermaid, GraphViz generation
3. **Diagram Formatters**: ASCII art diagrams
4. **Report Templates**: Pre-built report formats
5. **Interactive Formats**: HTML with JavaScript
6. **Localization**: Multi-language formatting

The formatters module provides specialized transformation logic that goes beyond simple display, enabling rich data representation and export capabilities throughout the Forge CLI system.
