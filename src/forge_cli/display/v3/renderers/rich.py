"""Rich renderer for v3 display - renders complete Response snapshots with beautiful terminal UI."""

import time
from typing import Any, Optional

from pydantic import BaseModel, Field, validator
from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from forge_cli.response._types.response import Response

from ..base import BaseRenderer


class RichDisplayConfig(BaseModel):
    """Configuration for Rich renderer display options."""

    show_reasoning: bool = Field(True, description="Whether to show reasoning/thinking content")
    show_citations: bool = Field(True, description="Whether to show citation details")
    show_tool_details: bool = Field(True, description="Whether to show detailed tool information")
    show_usage: bool = Field(True, description="Whether to show token usage statistics")
    show_metadata: bool = Field(False, description="Whether to show response metadata")
    max_text_preview: int = Field(100, description="Maximum characters for text previews")
    refresh_rate: int = Field(10, description="Live display refresh rate per second")
    flat_markdown: bool = Field(True, description="Render flat packed markdown without panels")

    @validator("refresh_rate")
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
            # If overrides supplied, update the provided config dataclass
            if config_overrides:
                self._config = config.copy(update=config_overrides)
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
            if hasattr(self, "_current_content") and self._current_content is not None:
                self._console.print(self._current_content)
            self._live = None
            self._live_started = False

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
        """Create rich content from complete response snapshot.

        If `self._config.flat_markdown` is True, build a single packed Markdown renderable
        that preserves the exact order of `response.output` and avoids any nested panels.
        """
        # Flat markdown path
        if self._config.flat_markdown:
            return self._create_flat_markdown_content(response)

        # Build content components
        content_parts = []

        # Add status header
        status_info = self._create_status_header(response)
        content_parts.append(status_info)

        # Add response content
        response_content = self._create_response_body(response)
        if response_content:
            content_parts.append(response_content)

        # Add tool information
        tool_content = self._create_tool_information(response)
        if tool_content:
            content_parts.append(tool_content)

        # Add reasoning if available and enabled
        if self._config.show_reasoning:
            reasoning_content = self._create_reasoning_content(response)
            if reasoning_content:
                content_parts.append(reasoning_content)

        # Add citations if available and enabled
        if self._config.show_citations:
            citation_content = self._create_citation_content(response)
            if citation_content:
                content_parts.append(citation_content)

        # Add usage statistics if enabled
        if self._config.show_usage and response.usage:
            usage_content = self._create_usage_content(response)
            content_parts.append(usage_content)

        # Combine all content
        if content_parts:
            combined_content = Group(*content_parts)
        else:
            combined_content = Text("No content available", style="dim italic")

        # Determine panel style based on response status
        border_style, title_style = self._get_panel_style(response)

        return Panel(
            combined_content,
            title=f"[{title_style}]Knowledge Forge Response[/{title_style}]",
            border_style=border_style,
            padding=(1, 2),
        )

    def _create_flat_markdown_content(self, response: Response) -> Markdown:
        """Build a packed Markdown object with no nested Rich containers."""
        md_parts: list[str] = []

        # Status line
        status_fragments: list[str] = []
        status_fragments.append(f"**ID:** {response.id[:12]}…")
        if response.status:
            status_fragments.append(f"**Status:** {response.status}")
        if response.model:
            status_fragments.append(f"**Model:** {response.model}")
        md_parts.append(" | ".join(status_fragments))

        # Iterate through output items maintaining order
        for item in response.output:
            if item.type == "message":
                for content in item.content:
                    if content.type == "output_text":
                        md_parts.append(content.text)
                        # inline citation numbers if present
                        if content.annotations:
                            # inline citation numbers handled; detailed reference list appended later
                            pass
                    elif content.type == "output_refusal":
                        md_parts.append(f"> ⚠️ Response refused: {content.refusal}")
            elif item.type in ["file_search_call", "web_search_call", "document_finder_call", "file_reader_call", "code_interpreter_call", "function_call"]:
                details = []
                if hasattr(item, "queries") and item.queries:
                    details.append(f"{len(item.queries)} queries")
                if hasattr(item, "results") and item.results:
                    details.append(f"{len(item.results)} results")
                detail_str = f" — {'; '.join(details)}" if details else ""
                md_parts.append(f"- 🛠️ {item.type.replace('_', ' ').title()} ({item.status}){detail_str}")
            elif item.type == "reasoning":
                if hasattr(item, "summary") and item.summary:
                    lines = [s.text.strip() for s in item.summary if hasattr(s, "text") and s.text]
                    if lines:
                        md_parts.extend([f"> {line}" for line in lines])

        # References section
        citations = self._extract_all_citations(response)
        if citations:
            ref_lines = ["**References**"]
            for idx, citation in enumerate(citations, 1):
                if citation["type"] == "file_citation":
                    source = citation.get("file_name") or citation.get("file_id", "unknown_file")
                    page = f" p.{citation.get('page_number')}" if citation.get("page_number") else ""
                    quote = f' — "{citation.get("text", "").strip()}"' if citation.get("text") else ""
                    ref_lines.append(f"{idx}. {source}{page}{quote}")
                else:
                    url = citation.get("url", "")
                    quote = f' — "{citation.get("text", "").strip()}"' if citation.get("text") else ""
                    ref_lines.append(f"{idx}. {url}{quote}")
            md_parts.append("\n".join(ref_lines))

        # Usage stats
        if self._config.show_usage and response.usage:
            u = response.usage
            md_parts.append(f"📊 **Usage:** Input {u.input_tokens or 0} | Output {u.output_tokens or 0} | Total {u.total_tokens or 0}")

        return Markdown("\n\n".join(md_parts))

    def _create_status_header(self, response: Response) -> Text:
        """Create status header with response information."""
        status_text = Text()

        # Response ID and status
        status_text.append("ID: ", style="cyan")
        status_text.append(f"{response.id[:12]}...", style="white")

        if response.status:
            status_text.append(" | Status: ", style="cyan")
            status_style = self._get_status_style(response.status)
            status_text.append(f"{response.status}", style=status_style)

        # Model information
        if response.model:
            status_text.append(" | Model: ", style="cyan")
            status_text.append(f"{response.model}", style="green")

        # Render count for streaming feedback
        status_text.append(" | Updates: ", style="cyan")
        status_text.append(f"{self._render_count}", style="yellow")

        return status_text

    def _create_response_body(self, response: Response) -> Group | None:
        """Create the main response content from output items."""
        content_parts = []

        for item in response.output:
            if item.type == "message":
                # Handle message content
                for content in item.content:
                    if content.type == "output_text":
                        # Render text as markdown
                        try:
                            md_content = Markdown(content.text)
                            content_parts.append(md_content)
                        except Exception:
                            # Fallback to plain text
                            content_parts.append(Text(content.text))

                        # Add annotations if available
                        if content.annotations and self._config.show_citations:
                            ann_text = self._format_inline_annotations(content.annotations)
                            if ann_text:
                                content_parts.append(ann_text)

                    elif content.type == "output_refusal":
                        # Handle refusal content
                        refusal_text = Text(f"⚠️ Response refused: {content.refusal}", style="red italic")
                        content_parts.append(refusal_text)

        return Group(*content_parts) if content_parts else None

    def _create_tool_information(self, response: Response) -> Panel | None:
        """Create tool execution information panel."""
        if not self._config.show_tool_details:
            return None

        tool_parts = []

        for item in response.output:
            if hasattr(item, "status") and hasattr(item, "type"):
                if item.type in ["file_search_call", "web_search_call", "document_finder_call", "file_reader_call"]:
                    tool_info = self._format_tool_item(item)
                    if tool_info:
                        tool_parts.append(tool_info)

        if tool_parts:
            return Panel(Group(*tool_parts), title="🛠️ Tool Execution", border_style="blue", padding=(0, 1))

        return None

    def _format_tool_item(self, tool_item: Any) -> Text | None:
        """Format individual tool item information."""
        tool_text = Text()

        # Tool type and status
        tool_icon = self._get_tool_icon(tool_item.type)
        status_style = self._get_tool_status_style(tool_item.status)

        tool_text.append(f"{tool_icon} ", style="")
        tool_text.append(f"{tool_item.type.replace('_', ' ').title()}: ", style="bold")
        tool_text.append(f"{tool_item.status}", style=status_style)

        # Add specific tool information
        if hasattr(tool_item, "queries") and tool_item.queries:
            tool_text.append(f" | Queries: {len(tool_item.queries)}", style="dim")

        if hasattr(tool_item, "results") and tool_item.results:
            tool_text.append(f" | Results: {len(tool_item.results)}", style="dim")

        return tool_text

    def _create_reasoning_content(self, response: Response) -> Panel | None:
        """Create reasoning content panel if available."""
        reasoning_parts = []

        for item in response.output:
            if hasattr(item, "type") and item.type == "reasoning":
                # Extract reasoning content from summary items
                if hasattr(item, "summary") and item.summary:
                    # Collect all reasoning text from summary items
                    reasoning_texts = []
                    for summary in item.summary:
                        if hasattr(summary, "text") and summary.text:
                            reasoning_texts.append(summary.text)

                    if reasoning_texts:
                        reasoning_content = "\n\n".join(reasoning_texts)
                        reasoning_text = Text("🤔 AI Reasoning:\n", style="yellow bold")
                        reasoning_text.append(reasoning_content, style="italic dim")
                        reasoning_parts.append(reasoning_text)

        if reasoning_parts:
            return Panel(Group(*reasoning_parts), title="💭 Reasoning", border_style="yellow", padding=(0, 1))

        return None

    def _create_citation_content(self, response: Response) -> Panel | None:
        """Create citations panel from annotations."""
        citations = self._extract_all_citations(response)

        if not citations:
            return None

        # Create citations table
        table = Table(title="Citations", show_header=True, header_style="bold cyan")
        table.add_column("Ref", style="cyan", width=6)
        table.add_column("Source", style="blue")
        table.add_column("Page", width=8)
        table.add_column("Quote", style="dim")

        for i, citation in enumerate(citations, 1):
            ref = f"[{i}]"
            source = citation.get("file_name", citation.get("url", "Unknown"))
            page = str(citation.get("page_number", "")) if citation.get("page_number") else "-"
            quote = citation.get("text", "")

            # Truncate quote if too long
            if len(quote) > 60:
                quote = quote[:57] + "..."

            table.add_row(ref, source, page, quote)

        return Panel(table, title="📚 Sources", border_style="cyan")

    def _create_usage_content(self, response: Response) -> Text:
        """Create usage statistics display."""
        usage = response.usage
        usage_text = Text()

        usage_text.append("📊 Usage: ", style="cyan bold")
        usage_text.append(f"Input: {usage.input_tokens or 0} | ", style="green")
        usage_text.append(f"Output: {usage.output_tokens or 0} | ", style="yellow")
        usage_text.append(f"Total: {usage.total_tokens or 0}", style="bold")

        return usage_text

    def _extract_all_citations(self, response: Response) -> list[dict[str, Any]]:
        """Extract all citations from response annotations."""
        citations = []

        for item in response.output:
            if item.type == "message":
                for content in item.content:
                    if content.type == "output_text" and content.annotations:
                        for annotation in content.annotations:
                            if annotation.type in ["file_citation", "url_citation"]:
                                citation_data = {
                                    "type": annotation.type,
                                    "text": getattr(annotation, "text", ""),
                                }

                                if annotation.type == "file_citation":
                                    citation_data.update(
                                        {
                                            "file_id": getattr(annotation, "file_id", ""),
                                            "file_name": getattr(annotation, "file_name", ""),
                                            "page_number": getattr(annotation, "page_number", None),
                                        }
                                    )
                                elif annotation.type == "url_citation":
                                    citation_data["url"] = getattr(annotation, "url", "")

                                citations.append(citation_data)

        return citations

    def _format_inline_annotations(self, annotations: list[Any]) -> Text | None:
        """Format annotations as inline references."""
        if not annotations:
            return None

        ann_text = Text()
        ann_text.append("📎 References: ", style="dim")

        for i, annotation in enumerate(annotations):
            if i > 0:
                ann_text.append(", ", style="dim")

            ann_text.append(f"[{i + 1}]", style="cyan")

        return ann_text

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

    def _get_status_style(self, status: str) -> str:
        """Get style for status text."""
        status_styles = {
            "completed": "bold green",
            "failed": "bold red",
            "in_progress": "bold yellow",
            "incomplete": "bold orange3",
        }
        return status_styles.get(status, "white")

    def _get_tool_icon(self, tool_type: str) -> str:
        """Get icon for tool type."""
        icons = {
            "file_search_call": "📄",
            "web_search_call": "🌐",
            "document_finder_call": "🔍",
            "file_reader_call": "📖",
            "code_interpreter_call": "💻",
            "function_call": "🔧",
        }
        return icons.get(tool_type, "🛠️")

    def _get_tool_status_style(self, status: str) -> str:
        """Get style for tool status."""
        status_styles = {
            "completed": "bold green",
            "in_progress": "bold yellow",
            "searching": "bold blue",
            "interpreting": "bold blue",
            "failed": "bold red",
        }
        return status_styles.get(status, "white")

    # Additional methods for chat mode and error handling
    def render_error(self, error: str) -> None:
        """Render error message."""
        error_panel = Panel(Text(f"❌ Error: {error}", style="red bold"), title="Error", border_style="red")

        if self._live and self._live_started:
            self._live.update(error_panel)
        else:
            self._console.print(error_panel)

    def render_welcome(self, config: Any) -> None:
        """Show welcome message for chat mode."""
        welcome_text = Text()

        # ASCII art logo
        ascii_art = """
╔═══════════════════════════════════════╗
║        Knowledge Forge v3             ║
║        Rich Display Renderer          ║
╚═══════════════════════════════════════╝
"""
        welcome_text.append(ascii_art, style="cyan")
        welcome_text.append("\nWelcome to ", style="bold")
        welcome_text.append("Knowledge Forge Chat", style="bold cyan")
        welcome_text.append("! (v3 Rich Renderer)\n\n", style="bold")

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
            title="[bold cyan]Knowledge Forge Chat v3[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        )
        self._console.print(panel)
