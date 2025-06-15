"""Rich renderer for v3 display - renders complete Response snapshots with beautiful terminal UI."""

import time
from typing import Any, Optional

from pydantic import BaseModel, Field, validator
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
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

    @validator("refresh_rate")
    def validate_refresh_rate(cls, v):  # noqa: N805
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
        """Create rich content from complete response snapshot."""
        md_parts: list[str] = []

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
                # Get tool-specific icon and format the tool call in a single beautiful line
                tool_icon = self._get_tool_icon(item.type)
                tool_name = item.type.replace("_call", "").replace("_", " ").title()

                # Create concise result summary based on tool type
                result_summary = self._get_tool_result_summary(item)

                # Format: Icon + Bold Name → Status • Result
                # Example: 🌐 **Web Search** → _completed_ • "weather today" found 5 results
                tool_line = f"{tool_icon} **{tool_name}** → _{item.status}_"

                if result_summary:
                    tool_line += f" • {result_summary}"

                md_parts.append(tool_line)
            elif item.type == "reasoning":
                if hasattr(item, "summary") and item.summary:
                    # Combine all reasoning lines into a single continuous Markdown
                    # blockquote so that Rich renders it as one cohesive block instead
                    # of multiple quote paragraphs.
                    quoted_lines: list[str] = []
                    for summary in item.summary:
                        if hasattr(summary, "text") and summary.text:
                            for line in summary.text.strip().splitlines():
                                # Prefix each line with '> '. If the line is empty we
                                # still add a lone '>' to preserve paragraph spacing
                                # inside the same quote block.
                                if line.strip():
                                    quoted_lines.append(f"> {line}")
                                else:
                                    quoted_lines.append(">")
                    if quoted_lines:
                        md_parts.append("\n".join(quoted_lines))

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

        # Create markdown content
        markdown_content = Markdown("\n\n".join(md_parts))

        # Create the new title format: full_id / status / ↑ input ↓ output
        title_parts = []

        # Full message ID
        title_parts.append(response.id)

        # Status
        if response.status:
            title_parts.append(response.status)

        # Usage information with arrows
        if response.usage:
            usage_part = f"↑ {response.usage.input_tokens or 0} ↓ {response.usage.output_tokens or 0}"
            title_parts.append(usage_part)

        panel_title = " / ".join(title_parts)

        # Determine panel style based on response status
        border_style, title_style = self._get_panel_style(response)

        return Panel(
            markdown_content,
            title=f"[{title_style}]{panel_title}[/{title_style}]",
            border_style=border_style,
            padding=(1, 2),
        )




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

    def _get_tool_result_summary(self, tool_item: Any) -> str:
        """Create a concise, beautiful summary of tool results."""
        tool_type = tool_item.type

        if tool_type == "file_search_call":
            # Show query/queries and result count
            query_str = ""
            if hasattr(tool_item, "query") and tool_item.query:
                query = tool_item.query[:40] + "..." if len(tool_item.query) > 40 else tool_item.query
                query_str = f'"{query}"'
            elif hasattr(tool_item, "queries") and tool_item.queries:
                if len(tool_item.queries) == 1:
                    query = tool_item.queries[0][:40] + "..." if len(tool_item.queries[0]) > 40 else tool_item.queries[0]
                    query_str = f'"{query}"'
                else:
                    query_str = f"{len(tool_item.queries)} queries"

            if hasattr(tool_item, "results") and tool_item.results:
                if query_str:
                    return f"{query_str} → found {len(tool_item.results)} results"
                else:
                    return f"found {len(tool_item.results)} results"
            elif query_str:
                return f"searching {query_str}"
            return "initializing search"

        elif tool_type == "web_search_call":
            # Show the search query and result count
            if hasattr(tool_item, "queries") and tool_item.queries:
                query = tool_item.queries[0][:50] + "..." if len(tool_item.queries[0]) > 50 else tool_item.queries[0]

                if hasattr(tool_item, "results") and tool_item.results:
                    return f'"{query}" → {len(tool_item.results)} results'
                else:
                    return f'searching "{query}"'
            return "initializing web search"

        elif tool_type == "document_finder_call":
            # Show query and results
            query_str = ""
            if hasattr(tool_item, "query") and tool_item.query:
                query = tool_item.query[:40] + "..." if len(tool_item.query) > 40 else tool_item.query
                query_str = f'"{query}"'
            elif hasattr(tool_item, "queries") and tool_item.queries:
                if len(tool_item.queries) == 1:
                    query = tool_item.queries[0][:40] + "..." if len(tool_item.queries[0]) > 40 else tool_item.queries[0]
                    query_str = f'"{query}"'
                else:
                    query_str = f"{len(tool_item.queries)} queries"
            
            if hasattr(tool_item, "results") and tool_item.results:
                doc_count = len(tool_item.results)
                if query_str:
                    return f"{query_str} → found {doc_count} document{'s' if doc_count != 1 else ''}"
                else:
                    return f"found {doc_count} document{'s' if doc_count != 1 else ''}"
            elif query_str:
                return f"searching {query_str}"
            return "initializing search"

        elif tool_type == "file_reader_call":
            # Show file being read with more context
            file_info = ""
            
            # Try to get file name first (most useful)
            if hasattr(tool_item, "file_name") and tool_item.file_name:
                name = tool_item.file_name[:35] + "..." if len(tool_item.file_name) > 35 else tool_item.file_name
                file_info = f'"{name}"'
            elif hasattr(tool_item, "file_id") and tool_item.file_id:
                file_info = f"file:{tool_item.file_id[:12]}..."
            
            # Check if there's content or results
            if hasattr(tool_item, "content") and tool_item.content:
                content_preview = tool_item.content[:50].replace('\n', ' ') + "..." if len(tool_item.content) > 50 else tool_item.content.replace('\n', ' ')
                if file_info:
                    return f"{file_info} → loaded ({len(tool_item.content)} chars)"
                else:
                    return f"loaded {len(tool_item.content)} characters"
            elif hasattr(tool_item, "results") and tool_item.results:
                if file_info:
                    return f"{file_info} → loaded successfully"
                else:
                    return "file loaded"
            elif file_info:
                return f"reading {file_info}"
            return "loading file"

        elif tool_type == "code_interpreter_call":
            # Show what code is doing
            if hasattr(tool_item, "code") and tool_item.code:
                # Extract first meaningful line of code
                lines = [line.strip() for line in tool_item.code.split("\n") if line.strip() and not line.strip().startswith("#")]
                if lines:
                    code_preview = lines[0][:40] + "..." if len(lines[0]) > 40 else lines[0]
                    return f"executing `{code_preview}`"
            return "running code"

        elif tool_type == "function_call":
            # Show function name and args preview
            if hasattr(tool_item, "function"):
                func_name = tool_item.function
                if hasattr(tool_item, "arguments"):
                    return f"calling {func_name}(...)"
                return f"calling {func_name}"
            return "executing function"

        # Default fallback
        if hasattr(tool_item, "results") and tool_item.results:
            return f"{len(tool_item.results)} results"
        return ""

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
