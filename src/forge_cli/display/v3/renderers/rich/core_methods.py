"""Core methods for the RichRenderer class - fully self-contained tool renderers."""

from typing import Any

from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

from forge_cli.response._types.response import Response
from forge_cli.response.type_guards import (
    is_message_item,
    is_reasoning_item,
)

from .reason import render_reasoning_item
from .output import render_message_content, render_citations
from .tools import (
    FileReaderToolRender,
    WebSearchToolRender,
    FileSearchToolRender,
    PageReaderToolRender,
    CodeInterpreterToolRender,
    FunctionCallToolRender,
    ListDocumentsToolRender,
)
from .usage import UsageRenderer


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
            # Use fully self-contained tool renderers!
            tool_renderer = get_tool_renderer(item)
            if tool_renderer:
                # Get complete tool content (tool line + trace if available)
                tool_parts = tool_renderer.render_complete_tool_with_trace()
                md_parts.extend(tool_parts)
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

    # Create the title format with usage information using specialized renderer
    panel_title = ""
    if response.usage:
        usage_renderer = UsageRenderer.from_usage_object(response.usage)
        panel_title = usage_renderer.render()

    # Determine panel style based on response status
    border_style, title_style = get_panel_style(response)

    return Panel(
        markdown_content,
        title=panel_title,
        border_style=border_style,
        title_align="left",
        padding=(1, 2),
    )


def get_tool_renderer(tool_item: Any):
    """Get the appropriate specialized renderer for a tool item."""
    tool_type = tool_item.type
    
    # Map tool types to their specialized renderers
    renderer_map = {
        "file_reader_call": FileReaderToolRender,
        "web_search_call": WebSearchToolRender,
        "file_search_call": FileSearchToolRender,
        "page_reader_call": PageReaderToolRender,
        "code_interpreter_call": CodeInterpreterToolRender,
        "function_call": FunctionCallToolRender,
        "list_documents_call": ListDocumentsToolRender,
    }
    
    renderer_class = renderer_map.get(tool_type)
    if renderer_class:
        return renderer_class.from_tool_item(tool_item)
    
    return None


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