"""Rich renderer for v3 display - renders complete Response snapshots with beautiful terminal UI."""

import time
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator
from rich.console import Console
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
from .tools import FileReaderToolRender
from .reason import render_reasoning_item
from .output import render_message_content, render_citations
from .welcome import render_welcome


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
        """Render a complete response snapshot."""
        from .core_methods import render_response_method
        render_response_method(self, response)

    def finalize(self) -> None:
        """Complete rendering and cleanup resources."""
        from .core_methods import finalize_method
        finalize_method(self)

    def _start_live_display(self) -> None:
        """Initialize and start the live display."""
        from .core_methods import start_live_display
        start_live_display(self)

    def _create_response_content(self, response: Response):
        """Create rich content from complete response snapshot."""
        from .core_methods import create_response_content
        return create_response_content(self, response)

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

    def render_welcome(self, config: Any) -> None:
        """Show welcome message for chat mode."""
        render_welcome(self._console, config)

    def show_status_rich(self, content: Any) -> None:
        """Show Rich content (tables, panels, etc) directly."""
        self._console.print(content) 