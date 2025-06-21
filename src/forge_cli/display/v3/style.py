"""Style definitions for the v3 display system.

This module contains visual style definitions including icons for different tools
and other styling constants used across the v3 display renderers.
"""

# Icons for different tools and components
ICONS = {
    # Tool icons (matching existing codebase usage)
    "file_search_call": " 󱁴 ",  # matches rich.py:302
    "web_search_call": " 󰖟 ",  # matches rich.py:303
    "code_analyzer_call": "🔧",  # matches rich.py:307
    "file_reader_call": " 󰈈 ",  # matches rich.py:305
    "page_reader_call": " 󰗚 ",  # page reader icon
    "list_documents_call": "  ",  # matches rich.py:304
    "code_interpreter_call": " 󱄕 ",  # matches rich.py:306
    "function_call": "  ",  # matches rich.py:307
    # Status icons (matching existing usage)
    "thinking": "  ",  # matches rich.py reasoning section
    "processing": " ⚡ ",
    "completed": "  ",
    "error": "  ",
    "warning": "  ",
    "in_progress": " 󰑮 ",
    "searching": "  ",
    "failed": "  ",
    "incomplete": "  ",
    "query": "  ",
    # Content type icons
    "message": " 󰍥 ",
    "citation": "  ",  # matches rich.py:268
    "code": " 󰌠 ",
    "reasoning": "  ",
    # Token usage icons (using existing directional arrows)
    "input_tokens": " ↑ ",  # matches rich.py:231
    "output_tokens": " ↓ ",  # matches rich.py:231
    "total": " ∑ ",
    # General UI icons
    "bullet": " • ",
    "arrow": " → ",  # matches rich.py tool summaries
    "check": " ✓ ",
    "cross": " ✗ ",
    "separator": "  ",  # matches rich.py title format
}

# Status icons dictionary for easy lookup
STATUS_ICONS = {
    "completed": "  ",
    "failed": "  ",
    "in_progress": " 󰑮 ",
    "incomplete": "  ",
    "searching": "  ",
    "interpreting": " 󱄕 ",
    "default": "  ",
}


def pack_queries(*queries) -> str:
    if len(queries) == 0:
        return ""
    if len(queries) == 1:
        return f"  {queries[0]}"
    if len(queries) == 2:
        return f"   {queries[0]}  {queries[1]}"

    fmt = f"   {queries[0]}  {queries[1]}  {queries[2]}"
    remain_count = len(queries) - 3
    if remain_count > 0:
        fmt += f" • {remain_count} more"
    return fmt


def sliding_display(
    content: str, 
    max_lines: int = 3, 
    format_type: str = "text", 
    strip_empty: bool = True
) -> list[str] | None:
    """Create a sliding display of the last N lines from content.
    
    This function extracts the last few lines from multi-line content, creating
    a sliding window effect when used with Rich's Live component. As new content
    is added, only the most recent lines are shown, giving a smooth scrolling appearance.
    
    Args:
        content: The multi-line text content to process
        max_lines: Maximum number of lines to show (default: 3)
        format_type: Output format - "text", "code", "markdown" (default: "text")
        strip_empty: Whether to remove empty lines before processing (default: True)
        
    Returns:
        List of formatted lines ready for display, or None if no content
        
    Example:
        >>> trace = "Step 1: Starting\\nStep 2: Processing\\nStep 3: Almost done\\nStep 4: Complete"
        >>> sliding_display(trace, max_lines=2, format_type="code")
        ['```text', 'Step 3: Almost done', 'Step 4: Complete', '```']
        
        >>> sliding_display("", max_lines=3)
        None
    """
    if not content:
        return None
    
    # Split content into lines
    lines = content.split("\n")
    
    # Remove empty lines if requested
    if strip_empty:
        lines = [line for line in lines if line.strip()]
        # After stripping empty lines, check if anything remains
        if not lines:
            return None
    
    # Handle edge cases for max_lines
    if max_lines <= 0:
        sliding_lines = []
    else:
        # Take the last N lines (sliding window)
        sliding_lines = lines[-max_lines:] if len(lines) > max_lines else lines
    
    # Format according to requested type
    if format_type == "code" or format_type == "text":
        formatted_lines = ["```text"]
        formatted_lines.extend(sliding_lines)
        formatted_lines.append("```")
        return formatted_lines
    elif format_type == "markdown":
        # Return as markdown lines
        return sliding_lines
    elif format_type == "raw":
        # Return raw lines without any formatting
        return sliding_lines
    else:
        # Default to text format
        formatted_lines = ["```text"]
        formatted_lines.extend(sliding_lines)
        formatted_lines.append("```")
        return formatted_lines



