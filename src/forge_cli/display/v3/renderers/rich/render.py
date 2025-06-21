"""Rich renderer for v3 display - renders complete Response snapshots with beautiful terminal UI."""

import time
from typing import TYPE_CHECKING, Any, Optional

from pydantic import BaseModel, Field, field_validator
from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from forge_cli.response._types.response import Response
from forge_cli.response.type_guards import (
    is_code_interpreter_call,
    is_file_reader_call,
    is_file_search_call,
    is_function_call,
    is_list_documents_call,
    is_message_item,
    is_page_reader_call,
    is_reasoning_item,
    is_web_search_call,
)

from forge_cli.display.citation_styling import long2circled
from forge_cli.style.markdowns import convert_to_blockquote
from ...base import BaseRenderer
from ...style import ICONS, STATUS_ICONS, pack_queries, sliding_display
from ...builder import TextBuilder

# Import from our new modular structure
from .tools import (
    FileReaderToolRender,
    WebSearchToolRender,
    FileSearchToolRender,
    PageReaderToolRender,
    CodeInterpreterToolRender,
    FunctionCallToolRender,
    ListDocumentsToolRender,
)
from .reason import render_reasoning_item
from .message_content import render_message_content
from .citations import render_citations
from .usage import UsageRenderer
from .welcome import render_welcome

if TYPE_CHECKING:
    from ....config import AppConfig


class RichDisplayConfig(BaseModel):
    """Configuration for Rich renderer display options."""

    show_reasoning: bool = Field(True, description="Whether to show reasoning/thinking content")
    show_citations: bool = Field(True, description="Whether to show citation details")
    show_tool_details: bool = Field(True, description="Whether to show detailed tool information")
    show_usage: bool = Field(True, description="Whether to show token usage statistics")
    show_metadata: bool = Field(False, description="Whether to show response metadata")
    max_text_preview: int = Field(100, description="Maximum characters for text previews")
    refresh_rate: int = Field(10, description="Live display refresh rate per second")

    @field_validator("refresh_rate")
    @classmethod
    def validate_refresh_rate(cls, v):
        if v < 1 or v > 30:
            raise ValueError("Refresh rate must be between 1 and 30")
        return v


class RichRenderer(BaseRenderer):
    """Rich terminal UI renderer for v3 display system.

    Renders complete Response snapshots with beautiful, interactive terminal UI.
    Follows the v3 design principle of one simple render_response() method.
    """

    def __init__(
        self,
        console: Optional["Console"] = None,
        config: RichDisplayConfig | None = None,
        in_chat_mode: bool = False,
        **config_overrides,
    ):
        """Initialize Rich renderer.

        Args:
            console: Rich console instance (creates new if not provided)
            config: Display configuration
            in_chat_mode: Whether we're in chat mode (affects display behavior)
        """
        super().__init__()
        self._console = console or Console()

        # Merge provided config or create new one using overrides
        if config is None:
            self._config = RichDisplayConfig(**config_overrides)
        else:
            # If overrides supplied, update the provided config Pydantic model
            if config_overrides:
                self._config = config.model_copy(update=config_overrides)
            else:
                self._config = config

        self._in_chat_mode = in_chat_mode

        # Live display management
        self._live: Live | None = None
        self._live_started = False

        # State tracking for display optimization
        self._last_response_id: str | None = None
        self._start_time = time.time()
        self._render_count = 0

    def render_response(self, response: Response) -> None:
        """Render a complete response snapshot.

        This is the core v3 method - everything is available in the response object.
        """
        self._ensure_not_finalized()
        self._render_count += 1

        # Initialize live display if needed
        if not self._live_started:
            self._start_live_display()

        # Create rich content from response
        content = self._create_response_content(response)

        # Save current content for potential final print
        self._current_content = content

        # Update live display
        if self._live and self._live_started:
            self._live.update(content)
        else:
            # Fallback to direct console output
            self._console.print(content)

        self._last_response_id = response.id

    def finalize(self) -> None:
        """Complete rendering and cleanup resources."""
        if self._live and self._live_started:
            # Stop live display (transient=True clears screen), then print final content once
            self._live.stop()
            if getattr(self, "_current_content", None) is not None:
                self._console.print(self._current_content)
            self._live = None
            self._live_started = False

        # Call parent finalize
        super().finalize()

    def _start_live_display(self) -> None:
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

    def _create_response_content(self, response: Response):
        """Create rich content from complete response snapshot using Group."""
        renderables = []

        # Iterate through output items maintaining order
        for item in response.output:
            if is_message_item(item):
                for content in item.content:
                    rendered_content = render_message_content(content)
                    if rendered_content:
                        renderables.append(rendered_content)
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
                tool_renderer = self._get_tool_renderer(item)
                if tool_renderer:
                    # Get complete tool content from single render() method
                    tool_content = tool_renderer.render()
                    if tool_content:
                        if isinstance(tool_content, list):
                            # If it's a list, add each item as a separate renderable
                            for item_content in tool_content:
                                if item_content:  # Skip empty items
                                    if isinstance(item_content, str):
                                        renderables.append(Markdown(item_content))
                                    else:
                                        renderables.append(item_content)
                        else:
                            # Single item
                            if isinstance(tool_content, str):
                                renderables.append(Markdown(tool_content))
                            else:
                                renderables.append(tool_content)
            elif is_reasoning_item(item):
                rendered_reasoning = render_reasoning_item(item)
                if rendered_reasoning:
                    renderables.append(rendered_reasoning)

        # References section - using type-based API
        citations = self._extract_all_citations(response)
        if citations:
            citations_content = render_citations(citations)
            if citations_content:
                if isinstance(citations_content, str):
                    renderables.append(Markdown(citations_content))
                else:
                    renderables.append(citations_content)

        # Create Group to combine all renderables
        if renderables:
            group_content = Group(*renderables)
        else:
            group_content = Text("No content available")

        # Create the title format with usage information using specialized renderer
        panel_title = ""
        if response.usage:
            usage_renderer = UsageRenderer.from_usage_object(response.usage)
            panel_title = usage_renderer.render()

        # Determine panel style based on response status
        border_style, title_style = self._get_panel_style(response)

        return Panel(
            group_content,
            title=panel_title,
            border_style=border_style,
            title_align="left",
            padding=(1, 2),
        )

    def _get_tool_renderer(self, tool_item: Any):
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

    def _extract_all_citations(self, response: Response) -> list[Any]:
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

    def _get_panel_style(self, response: Response) -> tuple[str, str]:
        """Determine panel border and title style based on response state."""
        if response.status == "completed":
            return "green", "bold green"
        elif response.status == "failed":
            return "red", "bold red"
        elif response.status == "in_progress":
            return "yellow", "bold yellow"
        else:
            return "blue", "bold blue"

    def render_error(self, error: str) -> None:
        """Render error message."""
        error_panel = Panel(
            Text(f"{ICONS['error']}Error: {error}", style="red bold"), 
            title="Error", 
            border_style="red"
        )

        if self._live and self._live_started:
            self._live.update(error_panel)
        else:
            self._console.print(error_panel)

    def render_welcome(self, config: "AppConfig") -> None:
        """Show welcome message for chat mode."""
        render_welcome(self._console, config)

    def show_status_rich(self, content: Any) -> None:
        """Show Rich content (tables, panels, etc) directly."""
        self._console.print(content) 