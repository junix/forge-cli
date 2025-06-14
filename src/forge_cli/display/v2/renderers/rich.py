"""Rich renderer - interactive terminal UI with live updates."""

import time
from typing import Dict, Union, List, Optional

try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from ..base import BaseRenderer
from ..events import EventType


class RichRenderer(BaseRenderer):
    """Rich terminal UI renderer with live updates."""

    def __init__(self, console: Optional["Console"] = None, show_reasoning: bool = True, in_chat_mode: bool = False):
        """Initialize Rich renderer.

        Args:
            console: Rich console instance (creates new if not provided)
            show_reasoning: Whether to show reasoning/thinking content
            in_chat_mode: Whether we're in chat mode (affects display behavior)
        """
        if not RICH_AVAILABLE:
            raise ImportError("rich library required for RichRenderer")

        super().__init__()
        self._console = console or Console()
        self._show_reasoning = show_reasoning
        self._in_chat_mode = in_chat_mode

        # Live display will be created when needed
        self._live = None

        # State tracking
        self._query = ""
        self._response_text = ""
        self._reasoning_text = ""
        self._reasoning_active = False
        self._citations: list[dict[str, Any]] = []
        self._active_tools: dict[str, dict[str, Any]] = {}
        self._errors: list[str] = []
        self._start_time = time.time()
        self._live_started = False
        self._event_count = 0
        self._current_event_type = ""
        self._usage = {}

        # Track previous snapshot lengths for delta detection
        self._last_response_length = 0
        self._last_reasoning_length = 0

        # Progress tracking
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=self._console,
            transient=True,
        )

    def render_stream_event(self, event_type: str, data: Dict[str, Union[str, int, float, bool, List, Dict]]) -> None:
        """Render a stream event with Rich UI."""
        # In chat mode, we allow reuse of the renderer after finalization
        if not self._in_chat_mode:
            self._ensure_not_finalized()

        # Update event tracking
        self._event_count += 1
        self._current_event_type = event_type

        # Start live display on first event (unless already started by show_request_info)
        if not self._live_started and self._live:
            self._live.start()
            self._live_started = True

        # Process event
        event_enum = EventType.from_string(event_type)

        if event_enum:
            match event_enum:
                case EventType.STREAM_START:
                    self._handle_stream_start(data)
                case EventType.STREAM_END:
                    self._handle_stream_end(data)
                case EventType.STREAM_ERROR:
                    self._handle_stream_error(data)
                case EventType.TEXT_DELTA:
                    self._handle_text_delta(data)
                case EventType.REASONING_START:
                    self._handle_reasoning_start(data)
                case EventType.REASONING_DELTA:
                    self._handle_reasoning_delta(data)
                case EventType.REASONING_COMPLETE:
                    self._handle_reasoning_complete(data)
                case EventType.TOOL_START:
                    self._handle_tool_start(data)
                case EventType.TOOL_COMPLETE:
                    self._handle_tool_complete(data)
                case EventType.TOOL_ERROR:
                    self._handle_tool_error(data)
                case EventType.CITATION_FOUND:
                    self._handle_citation_found(data)
                case _:
                    pass

        # Update display
        self._update_display()

    def _handle_stream_start(self, data: dict[str, Any]) -> None:
        """Handle stream start event."""
        self._query = data.get("query", "")
        self._start_time = time.time()

        # Create live display if needed
        if not self._live:
            self._live = Live(Panel(""), refresh_per_second=10, console=self._console, transient=False)
            # In chat mode, we need to start it immediately since render_request_info isn't called
            if self._in_chat_mode and not self._live_started:
                self._live.start()
                self._live_started = True

    def _handle_stream_end(self, data: dict[str, Any]) -> None:
        """Handle stream end event."""
        duration = time.time() - self._start_time
        self._usage = data.get("usage", {})

    def _handle_stream_error(self, data: dict[str, Any]) -> None:
        """Handle stream error event."""
        error = data.get("error", "Unknown error")
        self._errors.append(error)

        # Show error panel
        if self._live and self._live_started:
            error_panel = Panel(Text(f"❌ {error}", style="red"), title="Error", border_style="red")
            self._live.update(error_panel)

    def _handle_text_delta(self, data: dict[str, Any]) -> None:
        """Handle text delta event - actually a snapshot."""
        text = data.get("text", "")
        # Since this is a snapshot, replace the entire text
        self._response_text = text

        # Update metadata if provided
        metadata = data.get("metadata", {})
        if metadata:
            if "event_count" in metadata:
                self._event_count = metadata["event_count"]
            if "event_type" in metadata:
                self._current_event_type = metadata["event_type"]
            if "usage" in metadata:
                self._usage = metadata["usage"]

    def _handle_reasoning_start(self, data: dict[str, Any]) -> None:
        """Handle reasoning start event."""
        if self._show_reasoning:
            self._reasoning_active = True
            self._layout["reasoning"].visible = True

    def _handle_reasoning_delta(self, data: dict[str, Any]) -> None:
        """Handle reasoning delta event - actually a snapshot."""
        if self._show_reasoning:
            text = data.get("text", "")
            # Since this is a snapshot, replace the entire text
            self._reasoning_text = text

    def _handle_reasoning_complete(self, data: dict[str, Any]) -> None:
        """Handle reasoning complete event."""
        self._reasoning_active = False

    def _handle_tool_start(self, data: dict[str, Any]) -> None:
        """Handle tool start event."""
        tool_id = data.get("tool_id", f"tool_{time.time()}")
        tool_type = data.get("tool_type", "unknown")

        self._active_tools[tool_id] = {
            "type": tool_type,
            "status": "running",
            "started_at": time.time(),
            "progress_id": None,
        }

        # Add progress task
        task_id = self._progress.add_task(
            f"{tool_type}...",
            total=None,  # Indeterminate progress
        )
        self._active_tools[tool_id]["progress_id"] = task_id

    def _handle_tool_complete(self, data: dict[str, Any]) -> None:
        """Handle tool complete event."""
        tool_id = data.get("tool_id")
        if tool_id and tool_id in self._active_tools:
            tool = self._active_tools[tool_id]
            tool["status"] = "completed"
            tool["results_count"] = data.get("results_count", 0)

            # Complete progress task
            if tool["progress_id"] is not None:
                self._progress.update(
                    tool["progress_id"],
                    completed=100,
                    description=f"✅ {tool['type']} ({tool['results_count']} results)",
                )

    def _handle_tool_error(self, data: dict[str, Any]) -> None:
        """Handle tool error event."""
        tool_id = data.get("tool_id")
        if tool_id and tool_id in self._active_tools:
            tool = self._active_tools[tool_id]
            tool["status"] = "error"
            tool["error"] = data.get("error", "Unknown error")

            # Update progress task
            if tool["progress_id"] is not None:
                self._progress.update(tool["progress_id"], description=f"❌ {tool['type']} failed")

    def _handle_citation_found(self, data: dict[str, Any]) -> None:
        """Handle citation found event."""
        citation = {
            "number": data.get("citation_num", len(self._citations) + 1),
            "text": data.get("citation_text", ""),
            "source": data.get("source", ""),
            "file_name": data.get("file_name", ""),
            "page_number": data.get("page_number", ""),
            "url": data.get("url", ""),
        }
        self._citations.append(citation)

    def _format_status_info(self, metadata: dict[str, Any] | None = None) -> Text:
        """Format status information with usage statistics - matches v1 exactly."""
        status_info = Text()

        # Event count
        status_info.append(f"{self._event_count:05d}", style="cyan bold")
        status_info.append(" / ", style="white")

        # Event type
        if self._current_event_type:
            status_info.append(self._current_event_type, style="green")
            status_info.append(" / ", style="white")

        # Usage stats
        if self._usage:
            status_info.append("  ↑ ", style="blue")
            status_info.append(str(self._usage.get("input_tokens", 0)), style="blue bold")
            status_info.append("  ↓ ", style="magenta")
            status_info.append(str(self._usage.get("output_tokens", 0)), style="magenta bold")
            status_info.append("  ∑ ", style="yellow")
            status_info.append(str(self._usage.get("total_tokens", 0)), style="yellow bold")

        return status_info

    def _update_display(self) -> None:
        """Update display - simple panel mode for v1 compatibility."""
        if not self._live or not self._live_started:
            return

        # For v1 compatibility, use simple panels with status info in title
        status_info = self._format_status_info()

        # Combine content appropriately
        if self._response_text:
            try:
                panel = Panel(
                    Markdown(self._response_text),
                    title=status_info if status_info else "🔄 Streaming response...",
                    border_style="green",
                )
            except Exception:
                # Fallback to plain text if Markdown fails
                panel = Panel(
                    Text(self._response_text),
                    title=status_info if status_info else "🔄 Streaming response...",
                    border_style="green",
                )
            self._live.update(panel)
        else:
            # Show waiting panel
            panel = Panel(
                Text("Waiting for response...", style="dim italic"),
                title=status_info if status_info else "🔄 Streaming response...",
                border_style="blue",
            )
            self._live.update(panel)

    def finalize(self) -> None:
        """Complete rendering and stop live display."""
        if not self._finalized:
            if self._live_started and self._live:
                # Stop live display
                self._live.stop()
                self._live = None

                # Print final response outside of Live context for persistence
                if self._response_text:
                    if self._in_chat_mode:
                        # In chat mode, don't re-print content to avoid duplication
                        # The live display already showed the content during streaming
                        self._console.print()  # Just add blank line for spacing

                        # Reset state for next message in chat mode
                        self._response_text = ""
                        self._reasoning_text = ""
                        self._reasoning_complete = False
                        self._event_count = 0  # Reset event count for next message
                        self._finalized = False  # Allow renderer to be used again
                        self._live_started = False  # Allow live display to restart
                        self._live = None  # Reset live display reference
                    else:
                        # Non-chat mode - print separator and completion message
                        self._console.print()
                        # Just print a separator line like v1
                        self._console.print("=" * 80, style="blue")

                        # Print completion info like v1
                        completion_text = Text()
                        completion_text.append("\n✅ Response completed successfully!\n", style="green bold")
                        self._console.print(completion_text)

                # Print citations summary if any
                if self._citations and not self._in_chat_mode:
                    self._console.print()
                    self._print_citations_summary()

            # Only mark as finalized if not in chat mode
            if not self._in_chat_mode:
                self._finalized = True

    def _print_citations_summary(self) -> None:
        """Print a summary of citations after live display ends."""
        citations_table = Table(title="Citations", show_header=True, header_style="bold")
        citations_table.add_column("Citation", style="cyan", width=10)
        citations_table.add_column("Document", style="blue")
        citations_table.add_column("Page", width=8)
        citations_table.add_column("Quote", style="dim")

        for citation in self._citations:
            cite_num = f"[{citation['number']}]"
            doc = citation.get("file_name") or citation.get("source", "")
            page = str(citation.get("page_number", "")) if citation.get("page_number") else "-"
            quote = citation.get("text", "")

            # Truncate quote if too long
            if len(quote) > 50:
                quote = quote[:47] + "..."

            citations_table.add_row(cite_num, doc, page, quote)

        self._console.print(citations_table)

    def render_request_info(self, info: dict[str, Any]) -> None:
        """Render request information like v1 show_request_info."""
        request_text = Text()
        request_text.append("\n📄 Request Information:\n", style="cyan bold")

        if info.get("question"):
            request_text.append("  💬 Question: ", style="green")
            request_text.append(f"{info['question']}\n")

        if info.get("vec_ids"):
            request_text.append("  🔍 Vector Store IDs: ", style="green")
            request_text.append(f"{', '.join(info['vec_ids'])}\n")

        if info.get("model"):
            request_text.append("  🤖 Model: ", style="green")
            request_text.append(f"{info['model']}\n")

        if info.get("effort"):
            request_text.append("  ⚙️ Effort Level: ", style="green")
            request_text.append(f"{info['effort']}\n")

        if info.get("tools"):
            request_text.append("  🛠️ Enabled Tools: ", style="green")
            request_text.append(f"{', '.join(info['tools'])}\n")

        self._console.print(request_text)
        self._console.print(Text("\n🔄 Streaming response (please wait):", style="yellow bold"))
        self._console.print("=" * 80, style="blue")

        # Start live display - use simple panel like v1
        if not self._live:
            self._live = Live(Panel(""), refresh_per_second=10, console=self._console, transient=False)
            self._live.start()
            self._live_started = True

    def render_status(self, message: str) -> None:
        """Render a status message like v1 show_status."""
        if self._live and self._live_started:
            panel = Panel(Text(message, style="yellow"), title="Status", border_style="yellow")
            self._live.update(panel)
        else:
            # Print directly if live not started
            self._console.print(Panel(Text(message, style="yellow"), title="Status", border_style="yellow"))

    def render_status_rich(self, rich_content: Any) -> None:
        """Render rich content like v1 show_status_rich."""
        if self._live and self._live_started:
            self._live.update(rich_content)
        else:
            self._console.print(rich_content)

    def render_error(self, error: str) -> None:
        """Render error like v1 show_error."""
        if self._live and self._live_started:
            error_panel = Panel(Text(f"Error: {error}", style="red bold"), title="Error", border_style="red")
            self._live.update(error_panel)
        else:
            self._console.print(Text(f"\n❌ Error: {error}", style="red bold"))

    def render_finalize(self, response: dict[str, Any], state: Any) -> None:
        """Finalize rendering like v1 finalize method."""
        # In chat mode, just stop the live display without re-displaying content
        if self._in_chat_mode and self._live:
            # Stop live display - the content is already visible
            self._live.stop()
            self._live = None
            # Add a small spacing for better readability
            self._console.print()
            return

        # Non-chat mode finalization
        if self._live and self._live_started:
            self._live.stop()
            self._live = None

            # Print separator line like v1
            self._console.print()
            self._console.print("=" * 80, style="blue")

            # Print completion info like v1
            completion_text = Text()
            completion_text.append("\n✅ Response completed successfully!\n", style="green bold")

            if response:
                if response.get("id"):
                    completion_text.append("  🆔 Response ID: ", style="yellow")
                    completion_text.append(f"{response['id']}\n")

                if response.get("model"):
                    completion_text.append("  🤖 Model used: ", style="yellow")
                    completion_text.append(f"{response['model']}\n")

            self._console.print(completion_text)

            # Print citations summary if any
            if self._citations:
                self._console.print()
                self._print_citations_summary()

    # Chat mode specific methods
    def render_welcome(self, config: Any) -> None:
        """Show welcome message for chat mode - matches v1."""
        # Create a beautiful welcome panel
        welcome_text = Text()

        # ASCII art logo - using raw string to avoid escape sequence issues
        ascii_art = r"""
 _  __                    _          _              _____
| |/ /_ __   _____      _| | ___  __| | __ _  ___  |  ___|__  _ __ __ _  ___
| ' /| '_ \ / _ \ \ /\ / / |/ _ \/ _` |/ _` |/ _ \ | |_ / _ \| '__/ _` |/ _ \
| . \| | | | (_) \ V  V /| |  __/ (_| | (_| |  __/ |  _| (_) | | | (_| |  __/
|_|\_\_| |_|\___/ \_/\_/ |_|\___|\__,_|\__, |\___| |_|  \___/|_|  \__, |\___|
                                       |___/                      |___/
"""
        welcome_text.append(ascii_art, style="cyan")
        welcome_text.append("\nWelcome to ", style="bold")
        welcome_text.append("Knowledge Forge Chat", style="bold cyan")
        welcome_text.append("!\n\n", style="bold")

        if hasattr(config, "model"):
            welcome_text.append("Model: ", style="yellow")
            welcome_text.append(f"{config.model}\n", style="white")

        if hasattr(config, "enabled_tools") and config.enabled_tools:
            welcome_text.append("Tools: ", style="yellow")
            welcome_text.append(f"{', '.join(config.enabled_tools)}\n", style="white")

        welcome_text.append("\nType ", style="dim")
        welcome_text.append("/help", style="bold green")
        welcome_text.append(" for available commands", style="dim")

        panel = Panel(
            welcome_text,
            title="[bold cyan]Knowledge Forge Chat[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        )
        self._console.print(panel)
