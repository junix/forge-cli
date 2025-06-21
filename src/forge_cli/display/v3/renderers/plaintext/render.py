"""Refactored plaintext renderer using modular components for v3 display system."""

import time
from typing import TYPE_CHECKING, Any, Optional

from rich.console import Console, Group
from rich.live import Live
from rich.text import Text

from forge_cli.response._types.response import Response
from forge_cli.response.type_guards import (
    is_code_interpreter_call,
    is_computer_tool_call,
    is_file_reader_call,
    is_file_search_call,
    is_function_call,
    is_list_documents_call,
    is_message_item,
    is_page_reader_call,
    is_reasoning_item,
    is_web_search_call,
)

from ...base import BaseRenderer
from .....common.logger import logger
from .config import PlaintextDisplayConfig
from .styles import PlaintextStyles
from .message_content import PlaintextMessageContentRenderer
from .citations import PlaintextCitationsRenderer
from .usage import PlaintextUsageRenderer
from .reasoning import PlaintextReasoningRenderer
from .welcome import PlaintextWelcomeRenderer
from .tools import (
    PlaintextFileReaderToolRender,
    PlaintextWebSearchToolRender,
    PlaintextFileSearchToolRender,
    PlaintextPageReaderToolRender,
    PlaintextCodeInterpreterToolRender,
    PlaintextFunctionCallToolRender,
    PlaintextListDocumentsToolRender,
)

if TYPE_CHECKING:
    from ....config import AppConfig


class PlaintextRenderer(BaseRenderer):
    """Refactored plaintext renderer using modular components.

    Creates beautiful, colorful plaintext output without panels or markdown.
    Uses Rich's Group to combine different renderable objects.
    
    Now uses modular components following the same pattern as Rich renderer:
    - Separate renderers for each component type
    - Consistent interfaces and builder patterns
    - Better maintainability and testability
    """

    def __init__(
        self,
        console: Optional["Console"] = None,
        config: PlaintextDisplayConfig | None = None,
        in_chat_mode: bool = False,
    ):
        """Initialize plaintext renderer.

        Args:
            console: Rich console instance (creates new if not provided)
            config: Display configuration
            in_chat_mode: Whether we're in chat mode (affects display behavior)
        """
        super().__init__()
        self._console = console or Console()
        self._config = config or PlaintextDisplayConfig()
        self._in_chat_mode = in_chat_mode

        # Initialize centralized style manager
        self._styles = PlaintextStyles()

        # Live display management
        self._live: Live | None = None
        self._live_started = False

        # State tracking
        self._last_response_id: str | None = None
        self._start_time = time.time()
        self._render_count = 0

    def render_response(self, response: Response) -> None:
        """Render a complete response snapshot using modular components.

        This is the core v3 method - everything is available in the response object.
        """
        self._ensure_not_finalized()
        self._render_count += 1

        # Initialize live display if needed
        if not self._live_started:
            self._start_live_display()

        # Create content using modular renderers and Group
        content = self._create_response_group_modular(response)

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
            # Stop live display
            self._live.stop()
            self._live = None
            self._live_started = False

            # Add final spacing for readability
            if self._in_chat_mode:
                self._console.print()

        super().finalize()

    def _start_live_display(self) -> None:
        """Initialize and start the live display."""
        if not self._live:
            initial_text = Text("Starting Knowledge Forge...", style=self._styles.get_style("info"))
            self._live = Live(
                initial_text,
                console=self._console,
                refresh_per_second=self._config.refresh_rate,
                transient=False,
            )

        if not self._live_started:
            self._live.start()
            self._live_started = True

    def _create_response_group_modular(self, response: Response) -> Group:
        """Create Rich Group from complete response snapshot using modular renderers."""
        renderables = []

        # Process output items in their original order to preserve event sequence
        for item in response.output:
            if is_message_item(item):
                # Use message content renderer for each content item
                for content in item.content:
                    message_renderable = PlaintextMessageContentRenderer.from_content(
                        content, self._styles
                    )
                    if message_renderable:
                        renderables.append(message_renderable)

            elif is_reasoning_item(item) and self._config.show_reasoning:
                # Use reasoning renderer for single item
                reasoning_renderable = PlaintextReasoningRenderer.from_single_item(
                    item, self._styles, self._config
                ).render()
                if reasoning_renderable:
                    if isinstance(reasoning_renderable, list):
                        renderables.extend(reasoning_renderable)
                    else:
                        renderables.append(reasoning_renderable)

            elif self._is_tool_item(item) and self._config.show_tool_details:
                # Use specialized tool renderers
                tool_renderer = self._get_tool_renderer(item)
                if tool_renderer:
                    tool_renderable = tool_renderer.render()
                    if tool_renderable:
                        renderables.append(tool_renderable)

        # Add citations section using citations renderer
        citations_renderable = PlaintextCitationsRenderer.from_response(
            response, self._styles, self._config
        ).render()
        if citations_renderable:
            renderables.append(citations_renderable)

        # Add usage statistics using usage renderer
        usage_renderable = PlaintextUsageRenderer.from_response(
            response, self._render_count, self._styles, self._config
        ).render()
        if usage_renderable:
            renderables.append(usage_renderable)

        # Return Group containing all renderables
        return Group(*renderables)

    def _get_tool_renderer(self, tool_item: Any):
        """Get the appropriate specialized renderer for a tool item.
        
        Args:
            tool_item: Tool item to render
            
        Returns:
            Appropriate tool renderer instance or None
        """
        tool_type = tool_item.type
        
        # Map tool types to their specialized renderers
        renderer_map = {
            "file_search_call": PlaintextFileSearchToolRender,
            "web_search_call": PlaintextWebSearchToolRender,
            "file_reader_call": PlaintextFileReaderToolRender,
            "page_reader_call": PlaintextPageReaderToolRender,
            "list_documents_call": PlaintextListDocumentsToolRender,
            "code_interpreter_call": PlaintextCodeInterpreterToolRender,
            "function_call": PlaintextFunctionCallToolRender,
        }
        
        renderer_class = renderer_map.get(tool_type)
        if renderer_class:
            return renderer_class.from_tool_item(tool_item, self._styles, self._config)
        
        return None

    def _is_tool_item(self, item: Any) -> bool:
        """Check if item is a tool item.
        
        Args:
            item: Item to check
            
        Returns:
            True if item is a tool item
        """
        return item.type in [
            "file_search_call",
            "web_search_call",
            "list_documents_call",
            "file_reader_call",
            "page_reader_call",
            "code_interpreter_call",
            "function_call",
        ]

    # Additional methods for compatibility with Display interface
    def render_error(self, error: str) -> None:
        """Render error message."""
        error_text = Text()
        error_text.append("❌ ERROR: ", style=self._styles.get_style("error"))
        error_text.append(error, style="bold red")

        if self._live and self._live_started:
            self._live.update(error_text)
        else:
            self._console.print(error_text)

    def render_welcome(self, config: "AppConfig") -> None:
        """Show welcome message for chat mode using welcome renderer."""
        welcome_renderer = PlaintextWelcomeRenderer.from_app_config(
            config, self._styles, self._config, self._console
        )
        welcome_renderer.render_to_console()

    def render_request_info(self, info: dict) -> None:
        """Show request information."""
        info_text = Text()
        info_text.append("🔍 Query: ", style=self._styles.get_style("info"))
        info_text.append(f"{info.get('question', 'N/A')}\n", style=self._styles.get_style("content"))

        if info.get("model"):
            info_text.append("🤖 Model: ", style=self._styles.get_style("info"))
            info_text.append(f"{info['model']}\n", style=self._styles.get_style("model"))

        if info.get("tools"):
            info_text.append("🛠️  Tools: ", style=self._styles.get_style("info"))
            info_text.append(f"{', '.join(info['tools'])}\n", style=self._styles.get_style("content"))

        self._console.print(info_text)

    def render_status(self, message: str) -> None:
        """Show status message."""
        status_text = Text()
        status_text.append("ℹ️  Status: ", style=self._styles.get_style("info"))
        status_text.append(message, style=self._styles.get_style("content"))
        self._console.print(status_text)

    def show_status_rich(self, content: Any) -> None:
        """Show Rich content (tables, panels, etc) directly."""
        # For plaintext renderer, we'll display Rich objects directly
        # since we're using Rich console anyway
        self._console.print(content) 