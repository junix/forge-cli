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
    "document_finder_call": "  ",  # matches rich.py:304
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
        return f"  {queries[0]}"
    if len(queries) == 2:
        return f"   {queries[0]}  {queries[1]}"
    return f"   {queries[0]}  {queries[1]}  {queries[2]} • {len(queries) - 3} more"
