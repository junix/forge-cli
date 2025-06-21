"""Core methods for the RichRenderer class."""

from typing import Any

from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

from forge_cli.response._types.response import Response
from forge_cli.response.type_guards import (
    is_message_item,
    is_reasoning_item,
)

from ...style import ICONS, STATUS_ICONS

from .reason import render_reasoning_item
from .output import render_message_content, render_citations
from .tools import FileReaderToolRender
from .tool_methods import get_tool_result_summary, get_trace_block


def render_response_method(self, response: Response) -> None:
    """Render a complete response snapshot.

    This is the core v3 method - everything is available in the response object.
    """
    self._ensure_not_finalized()
    self._render_count += 1

    # Initialize live display if needed
    if not self._live_started:
        start_live_display(self)

    # Create rich content from response
    content = create_response_content(self, response)

    # Save current content for potential final print
    self._current_content = content

    # Update live display
    if self._live and self._live_started:
        self._live.update(content)
    else:
        # Fallback to direct console output
        self._console.print(content)

    self._last_response_id = response.id


def finalize_method(self) -> None:
    """Complete rendering and cleanup resources."""
    if self._live and self._live_started:
        # Stop live display (transient=True clears screen), then print final content once
        self._live.stop()
        if getattr(self, "_current_content", None) is not None:
            self._console.print(self._current_content)
        self._live = None
        self._live_started = False

    # Call parent finalize
    super(type(self), self).finalize()


def start_live_display(self) -> None:
    """Initialize and start the live display."""
    if not self._live:
        self._live = Live(
            Panel("Starting..."),
            console=self._console,
            refresh_per_second=self._config.refresh_rate,
            transient=True,
        )

    if not self._live_started:
        self._live.start()
        self._live_started = True


def create_response_content(self, response: Response):
    """Create rich content from complete response snapshot."""
    md_parts: list[str] = []

    # Iterate through output items maintaining order
    for item in response.output:
        if is_message_item(item):
            for content in item.content:
                rendered_content = render_message_content(content)
                if rendered_content:
                    md_parts.append(rendered_content)
        elif item.type in [
            "file_search_call",
            "web_search_call", 
            "list_documents_call",
            "file_reader_call",
            "page_reader_call",
            "code_interpreter_call",
            "function_call",
        ]:
            # Get tool-specific icon and format the tool call
            tool_icon = get_tool_icon(item.type)
            short_name = {
                "web_search_call": "Web",
                "file_search_call": "Search", 
                "list_documents_call": "List",
                "file_reader_call": "Reader",
                "page_reader_call": "Page",
                "code_interpreter_call": "Interpreter",
                "function_call": "Tool",
            }
            tool_name = short_name.get(item.type, item.type.replace("_call", "").replace("_", " ").title())

            # Get status icon
            status_icon = STATUS_ICONS.get(item.status, STATUS_ICONS["default"])

            # Create concise result summary based on tool type
            result_summary = get_tool_result_summary(item)

            # Format: Tool Icon + Bold Name + Status Icon + Status + Result
            tool_line = f"{tool_icon} _{tool_name}_ • {status_icon}_{item.status}_"

            if result_summary:
                tool_line += f" {ICONS['bullet']} {result_summary}"

            # Check if this tool is traceable and has execution trace
            trace_block = get_trace_block(item)
            if trace_block:
                # For traceable tools, show tool line + trace block
                md_parts.append(tool_line)
                md_parts.append("\n".join(trace_block))
            else:
                # For non-traceable tools, show just the tool line
                md_parts.append(tool_line)
        elif is_reasoning_item(item):
            rendered_reasoning = render_reasoning_item(item)
            if rendered_reasoning:
                md_parts.append(rendered_reasoning)

    # References section - using type-based API
    citations = extract_all_citations(response)
    if citations:
        citations_content = render_citations(citations)
        if citations_content:
            md_parts.append(citations_content)

    # Create markdown content
    markdown_content = Markdown("\n\n".join(md_parts))

    # Create the title format with usage information
    title_parts = []

    # Usage information with icons from style.py
    if response.usage:
        title_parts.append("[yellow]" + ICONS["input_tokens"] + "[/yellow]")
        title_parts.append(f"[green]{response.usage.input_tokens}[/green]")
        title_parts.append("[yellow]" + ICONS["output_tokens"] + "[/yellow]") 
        title_parts.append(f"[green]{response.usage.output_tokens}[/green]")

    panel_title = " ".join(title_parts)

    # Determine panel style based on response status
    border_style, title_style = get_panel_style(response)

    return Panel(
        markdown_content,
        title=panel_title,
        border_style=border_style,
        title_align="left",
        padding=(1, 2),
    )


def extract_all_citations(response: Response) -> list[Any]:
    """Extract all citations from response annotations using type-based API."""
    citations = []

    for item in response.output:
        if item.type == "message":
            for content in item.content:
                if content.type == "output_text" and content.annotations:
                    for annotation in content.annotations:
                        # Only include citation types, not file_path
                        if annotation.type in ["file_citation", "url_citation", "file_path"]:
                            citations.append(annotation)

    return citations


def get_panel_style(response: Response) -> tuple[str, str]:
    """Determine panel border and title style based on response state."""
    if response.status == "completed":
        return "green", "bold green"
    elif response.status == "failed":
        return "red", "bold red"
    elif response.status == "in_progress":
        return "yellow", "bold yellow"
    else:
        return "blue", "bold blue"


def get_tool_icon(tool_type: str) -> str:
    """Get icon for tool type."""
    return ICONS.get(tool_type, ICONS["processing"]) 