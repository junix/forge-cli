"""Rich renderer - interactive terminal UI with live updates."""

import time
from typing import Any, Optional

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

    def __init__(self, console: Optional["Console"] = None, show_reasoning: bool = True):
        """Initialize Rich renderer.

        Args:
            console: Rich console instance (creates new if not provided)
            show_reasoning: Whether to show reasoning/thinking content
        """
        if not RICH_AVAILABLE:
            raise ImportError("rich library required for RichRenderer")

        super().__init__()
        self._console = console or Console()
        self._show_reasoning = show_reasoning

        # Create layout
        self._layout = self._create_layout()
        self._live = Live(self._layout, console=self._console, refresh_per_second=10, vertical_overflow="visible")

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

        # Progress tracking
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=self._console,
            transient=True,
        )

    def _create_layout(self) -> Layout:
        """Create the Rich layout structure."""
        layout = Layout()

        # Main vertical split
        layout.split_column(Layout(name="header", size=3), Layout(name="body"), Layout(name="footer", size=1))

        # Body split into main content and sidebar
        layout["body"].split_row(Layout(name="main", ratio=3), Layout(name="sidebar", ratio=1))

        # Main content areas
        layout["main"].split_column(Layout(name="reasoning", size=6, visible=False), Layout(name="response"))

        # Sidebar areas
        layout["sidebar"].split_column(Layout(name="tools", size=10), Layout(name="citations"))

        return layout

    def render_stream_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Render a stream event with Rich UI."""
        self._ensure_not_finalized()

        # Start live display on first event
        if not self._live_started:
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

        # Update header
        header_text = Text(f"🔍 {self._query}", style="bold cyan")
        self._layout["header"].update(Panel(header_text, title="Knowledge Forge"))

        # Update footer
        model = data.get("model", "")
        effort = data.get("effort", "")
        footer_text = f"Model: {model} | Effort: {effort}"
        self._layout["footer"].update(Text(footer_text, style="dim"))

    def _handle_stream_end(self, data: dict[str, Any]) -> None:
        """Handle stream end event."""
        duration = time.time() - self._start_time
        usage = data.get("usage", {})

        # Update footer with completion info
        tokens = usage.get("total_tokens", 0)
        footer_text = f"✅ Completed in {duration:.1f}s | Tokens: {tokens}"
        self._layout["footer"].update(Text(footer_text, style="green"))

    def _handle_stream_error(self, data: dict[str, Any]) -> None:
        """Handle stream error event."""
        error = data.get("error", "Unknown error")
        self._errors.append(error)

        # Show error panel
        error_panel = Panel(Text(f"❌ {error}", style="red"), title="Error", border_style="red")
        self._layout["response"].update(error_panel)

    def _handle_text_delta(self, data: dict[str, Any]) -> None:
        """Handle text delta event."""
        text = data.get("text", "")
        self._response_text += text

    def _handle_reasoning_start(self, data: dict[str, Any]) -> None:
        """Handle reasoning start event."""
        if self._show_reasoning:
            self._reasoning_active = True
            self._layout["reasoning"].visible = True

    def _handle_reasoning_delta(self, data: dict[str, Any]) -> None:
        """Handle reasoning delta event."""
        if self._show_reasoning:
            text = data.get("text", "")
            self._reasoning_text += text

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

    def _update_display(self) -> None:
        """Update all display components."""
        # Update reasoning panel
        if self._show_reasoning and self._reasoning_text:
            reasoning_content = Panel(
                Markdown(self._reasoning_text),
                title="🤔 Thinking",
                border_style="yellow" if self._reasoning_active else "dim",
            )
            self._layout["reasoning"].update(reasoning_content)

        # Update response panel
        if self._response_text:
            response_content = Panel(Markdown(self._response_text), title="💬 Response", border_style="green")
            self._layout["response"].update(response_content)
        else:
            # Show waiting message
            waiting = Panel(Text("Waiting for response...", style="dim italic"), title="💬 Response")
            self._layout["response"].update(waiting)

        # Update tools panel
        if self._active_tools:
            tools_table = Table(title="🔧 Tools", show_header=True, header_style="bold")
            tools_table.add_column("Tool", style="cyan")
            tools_table.add_column("Status", style="green")
            tools_table.add_column("Results")

            for tool_id, tool_info in self._active_tools.items():
                status = tool_info["status"]

                if status == "running":
                    status_text = Text("⏳ Running", style="yellow")
                    results_text = "-"
                elif status == "completed":
                    status_text = Text("✅ Done", style="green")
                    results_text = str(tool_info.get("results_count", 0))
                else:
                    status_text = Text("❌ Error", style="red")
                    results_text = "-"

                tools_table.add_row(tool_info["type"], status_text, results_text)

            self._layout["tools"].update(Panel(tools_table))
        else:
            self._layout["tools"].update(Panel(Text("No tools active", style="dim")))

        # Update citations panel
        if self._citations:
            citations_table = Table(title="📚 Citations", show_header=True, header_style="bold")
            citations_table.add_column("#", width=3)
            citations_table.add_column("Source", style="blue", no_wrap=True)
            citations_table.add_column("Page", width=6)

            for citation in self._citations[-10:]:  # Show last 10
                page = str(citation.get("page_number", "")) if citation.get("page_number") else "-"
                source = citation.get("file_name") or citation.get("source", "Unknown")

                # Truncate source if too long
                if len(source) > 25:
                    source = source[:22] + "..."

                citations_table.add_row(f"[{citation['number']}]", source, page)

            self._layout["citations"].update(Panel(citations_table))
        else:
            self._layout["citations"].update(Panel(Text("No citations yet", style="dim")))

    def finalize(self) -> None:
        """Complete rendering and stop live display."""
        if not self._finalized:
            if self._live_started:
                # Final update
                self._update_display()

                # Show completion in footer
                duration = time.time() - self._start_time
                footer_text = f"✨ Response ready ({duration:.1f}s)"
                self._layout["footer"].update(Text(footer_text, style="bold green"))

                # Keep display for a moment
                time.sleep(0.5)

                # Stop live display
                self._live.stop()

                # Print final response outside of Live context for persistence
                if self._response_text:
                    self._console.print()
                    self._console.print(
                        Panel(Markdown(self._response_text), title="Final Response", border_style="green")
                    )

                # Print citations summary if any
                if self._citations:
                    self._console.print()
                    self._print_citations_summary()

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
