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
from forge_cli.response.type_guards import (
    is_file_search_call,
    is_web_search_call,
    is_document_finder_call,
    is_file_reader_call,
    is_code_interpreter_call,
    is_function_call,
    is_message_item,
    is_reasoning_item,
)

from ..base import BaseRenderer
from ..style import ICONS, STATUS_ICONS, pack_queries


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
            if getattr(self, "_current_content", None) is not None:
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
            if is_message_item(item):
                for content in item.content:
                    if content.type == "output_text":
                        md_parts.append(content.text)
                        # inline citation numbers if present
                        if content.annotations:
                            # inline citation numbers handled; detailed reference list appended later
                            pass
                    elif content.type == "output_refusal":
                        md_parts.append(f"> ⚠️ Response refused: {content.refusal}")
            elif item.type in [
                "file_search_call",
                "web_search_call",
                "document_finder_call",
                "file_reader_call",
                "code_interpreter_call",
                "function_call",
            ]:
                # Get tool-specific icon and format the tool call in a single beautiful line
                tool_icon = self._get_tool_icon(item.type)
                tool_name = item.type.replace("_call", "").replace("_", " ").title()

                # Get status icon
                status_icon = STATUS_ICONS.get(item.status, STATUS_ICONS["default"])

                # Create concise result summary based on tool type
                result_summary = self._get_tool_result_summary(item)

                # Format: Tool Icon + Bold Name + Status Icon + Status + Result
                # Example: 󱁴 **File Search** ✓ _completed_ → "query" found 5 results
                tool_line = f"{tool_icon}**{tool_name}** {status_icon}_{item.status}_"

                if result_summary:
                    tool_line += f" {ICONS['arrow']} {result_summary}"

                md_parts.append(tool_line)
            elif is_reasoning_item(item):
                if item.summary:
                    # Combine all reasoning lines into a single continuous Markdown
                    # blockquote so that Rich renders it as one cohesive block instead
                    # of multiple quote paragraphs.
                    quoted_lines: list[str] = []
                    for summary in item.summary:
                        if summary.text:
                            # summary = f"{ICONS['thinking']} thinking\n\n" + summary.text.strip()
                            summary_text = summary.text.strip()
                            for line in summary_text.splitlines():
                                # Prefix each line with '> '. If the line is empty we
                                # still add a lone '>' to preserve paragraph spacing
                                # inside the same quote block.
                                if line.strip():
                                    quoted_lines.append(f"> {line}")
                                else:
                                    quoted_lines.append(">")
                    if quoted_lines:
                        md_parts.append("\n".join(quoted_lines))

        # References section - using type-based API
        citations = self._extract_all_citations(response)
        if citations:
            ref_lines = ["### References"]
            for idx, citation in enumerate(citations, 1):
                if citation.type == "file_citation":
                    # Use typed properties from AnnotationFileCitation
                    source = citation.filename or citation.file_id or "unknown_file"
                    # Note: AnnotationFileCitation uses 'index' not 'page_number'
                    page = f" p.{citation.index}" if citation.index is not None else ""
                    ref_lines.append(f"{idx}. {source} 󰭤 {page}")
                elif citation.type == "url_citation":
                    # Use typed properties from AnnotationURLCitation
                    url = citation.url
                    if not citation.title:
                        title = url
                    else:
                        title = citation.title
                    ref_lines.append(f"{idx}. [{title}]({url})")
                elif citation.type == "file_path":
                    # Use typed properties from AnnotationFilePath
                    source = citation.file_id or "unknown_file"
                    ref_lines.append(f"{ICONS['bullet']}[{idx}] {source}")
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

        # Usage information with icons from style.py
        if response.usage:
            usage_part = f"{ICONS['input_tokens']}{response.usage.input_tokens or 0} {ICONS['output_tokens']}{response.usage.output_tokens or 0}"
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

    def _format_inline_annotations(self, annotations: list[Any]) -> Text | None:
        """Format annotations as inline references."""
        if not annotations:
            return None

        ann_text = Text()
        ann_text.append(f"{ICONS['citation']}References: ", style="dim")

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
        return ICONS.get(tool_type, ICONS["processing"])

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
        if is_file_search_call(tool_item):
            # Show query/queries with search icon and result count
            query_parts = []
            # File search calls have queries (list), not a single query
            if tool_item.queries:
                # Use pack_queries for beautiful multi-query display
                shortened_queries = [q[:30] + "..." if len(q) > 30 else q for q in tool_item.queries]
                packed = pack_queries(*[f'"{q}"' for q in shortened_queries])
                query_parts.append(packed)

            # Add results information
            if getattr(tool_item, "results", None):
                result_count = len(tool_item.results)
                # Note: vector_store_ids might be added dynamically
                vector_store_ids = getattr(tool_item, "vector_store_ids", None)
                if vector_store_ids:
                    stores = len(vector_store_ids)
                    query_parts.append(
                        f"{ICONS['check']}{result_count} results from {stores} store{'s' if stores > 1 else ''}"
                    )
                else:
                    query_parts.append(f"{ICONS['check']}{result_count} result{'s' if result_count != 1 else ''}")

            if query_parts:
                return f" {ICONS['arrow']} ".join(query_parts)
            elif tool_item.status == "searching":
                return f"{ICONS['searching']}initializing search..."
            return "preparing file search"

        elif is_web_search_call(tool_item):
            # Show web search with globe icon
            parts = []
            if tool_item.queries:
                # Use pack_queries for beautiful display
                shortened_queries = [q[:30] + "..." if len(q) > 30 else q for q in tool_item.queries]
                packed = pack_queries(*[f'"{q}"' for q in shortened_queries])
                parts.append(packed)

                if getattr(tool_item, "results", None):
                    result_count = len(tool_item.results)
                    # Show top domains if available
                    domains = []
                    for r in tool_item.results[:3]:
                        if r.url:
                            try:
                                from urllib.parse import urlparse

                                domain = urlparse(r.url).netloc
                                if domain and domain not in domains:
                                    domains.append(domain.replace("www.", ""))
                            except:
                                pass

                    if domains:
                        parts.append(f"{ICONS['check']}{result_count} results ({', '.join(domains[:2])}...)")
                    else:
                        parts.append(f"{ICONS['check']}{result_count} results")

            if parts:
                return f" {ICONS['arrow']} ".join(parts)
            return f"{ICONS['searching']}initializing web search..."

        elif is_document_finder_call(tool_item):
            # Show document search with magnifying glass
            parts = []
            if tool_item.queries:
                # Use pack_queries for consistent display
                shortened_queries = [q[:25] + "..." if len(q) > 25 else q for q in tool_item.queries]
                packed = pack_queries(*[f'"{q}"' for q in shortened_queries])
                parts.append(packed)

            if getattr(tool_item, "results", None):
                doc_count = len(tool_item.results)
                # Show document types if available
                doc_types = set()
                for r in tool_item.results:
                    if getattr(r, "file_name", None):
                        ext = r.file_name.split(".")[-1].lower() if "." in r.file_name else None
                        if ext:
                            doc_types.add(ext)

                if doc_types:
                    types_str = ", ".join(list(doc_types)[:3])
                    parts.append(f"{ICONS['check']}{doc_count} document{'s' if doc_count != 1 else ''} ({types_str})")
                else:
                    parts.append(f"{ICONS['check']}{doc_count} document{'s' if doc_count != 1 else ''}")

            if parts:
                return f" {ICONS['arrow']} ".join(parts)
            return f"{ICONS['searching']}initializing document search..."

        elif is_file_reader_call(tool_item):
            # Show file reading with book icon and detailed info
            parts = []

            # File identification
            file_name = getattr(tool_item, "file_name", None)
            if file_name:
                # Show file extension
                ext = file_name.split(".")[-1].lower() if "." in file_name else "file"
                name_short = file_name[:30] + "..." if len(file_name) > 30 else file_name
                parts.append(f'{ICONS["file_reader"]}"{name_short}" [{ext.upper()}]')
            elif tool_item.doc_ids and len(tool_item.doc_ids) > 0:
                parts.append(f"{ICONS['file_reader']}file:{tool_item.doc_ids[0][:12]}...")

            # Content information
            content = getattr(tool_item, "content", None)
            if content:
                content_len = len(content)
                # Format size nicely
                if content_len > 1024 * 1024:
                    size_str = f"{content_len / (1024 * 1024):.1f}MB"
                elif content_len > 1024:
                    size_str = f"{content_len / 1024:.1f}KB"
                else:
                    size_str = f"{content_len} chars"

                # Show preview of content type
                content_preview = content[:100].strip()
                if content_preview.startswith("{") or content_preview.startswith("["):
                    parts.append(f"{ICONS['check']}loaded {size_str} (JSON)")
                elif content_preview.startswith("<?xml"):
                    parts.append(f"{ICONS['check']}loaded {size_str} (XML)")
                elif content_preview.startswith("<!DOCTYPE") or content_preview.startswith("<html"):
                    parts.append(f"{ICONS['check']}loaded {size_str} (HTML)")
                else:
                    parts.append(f"{ICONS['check']}loaded {size_str}")
            elif getattr(tool_item, "results", None):
                parts.append(f"{ICONS['completed']}loaded successfully")

            if parts:
                return f" {ICONS['arrow']} ".join(parts)
            return f"{ICONS['processing']}loading file..."

        elif is_code_interpreter_call(tool_item):
            # Show code execution with computer icon
            parts = []
            code = getattr(tool_item, "code", None)
            if code:
                # Detect language from code
                code_lower = code.lower()
                if "import" in code_lower or "def " in code_lower:
                    lang = "Python"
                elif "const " in code_lower or "function " in code_lower:
                    lang = "JavaScript"
                elif "#include" in code_lower:
                    lang = "C/C++"
                else:
                    lang = "Code"

                # Extract first meaningful line
                lines = [
                    line.strip()
                    for line in code.split("\n")
                    if line.strip() and not line.strip().startswith("#")
                ]
                if lines:
                    code_preview = lines[0][:35] + "..." if len(lines[0]) > 35 else lines[0]
                    parts.append(f"{ICONS['code']}{lang}: `{code_preview}`")

                    # Show line count for longer code
                    total_lines = len([l for l in code.split("\n") if l.strip()])
                    if total_lines > 5:
                        parts.append(f"{ICONS['code']}{total_lines} lines")

            # Show output if available
            output = getattr(tool_item, "output", None)
            if output:
                output_preview = (
                    str(output)[:30] + "..." if len(str(output)) > 30 else str(output)
                )
                parts.append(f"{ICONS['output_tokens']}output: {output_preview}")

            if parts:
                return f" {ICONS['arrow']} ".join(parts)
            return f"{ICONS['processing']}executing code..."

        elif is_function_call(tool_item):
            # Show function call with wrench icon
            parts = []
            if tool_item.function:
                parts.append(f"{ICONS['function_call']}{tool_item.function}")

                # Show argument preview if available
                if tool_item.arguments:
                    try:
                        import json

                        args = (
                            json.loads(tool_item.arguments)
                            if isinstance(tool_item.arguments, str)
                            else tool_item.arguments
                        )
                        if isinstance(args, dict):
                            arg_preview = ", ".join(f"{k}={v}" for k, v in list(args.items())[:2])
                            if len(args) > 2:
                                arg_preview += f", +{len(args) - 2} more"
                            parts.append(f"{ICONS['code']}({arg_preview})")
                    except:
                        parts.append(f"{ICONS['code']}(with arguments)")

            # Show result preview if available
            output = getattr(tool_item, "output", None)
            if output:
                output_str = (
                    str(output)[:40] + "..." if len(str(output)) > 40 else str(output)
                )
                parts.append(f"{ICONS['check']}{output_str}")

            if parts:
                return f" {ICONS['arrow']} ".join(parts)
            return f"{ICONS['processing']}calling function..."

        # Default fallback
        if getattr(tool_item, "results", None):
            return f"{ICONS['check']}{len(tool_item.results)} results"
        return ""

    # Additional methods for chat mode and error handling
    def render_error(self, error: str) -> None:
        """Render error message."""
        error_panel = Panel(
            Text(f"{ICONS['error']}Error: {error}", style="red bold"), title="Error", border_style="red"
        )

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

        if getattr(config, "model", None):
            welcome_text.append("Model: ", style="yellow")
            welcome_text.append(f"{config.model}\n", style="white")

        if getattr(config, "enabled_tools", None):
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
