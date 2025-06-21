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

from ...citation_styling import long2circled
from forge_cli.style.markdowns import convert_to_blockquote
from ..base import BaseRenderer
from ..style import ICONS, STATUS_ICONS, pack_queries, sliding_display
from ..builder import Build


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
                        # Convert long-style citation markers to circled digits
                        converted_text = long2circled(content.text)
                        md_parts.append(converted_text)
                        # inline citation numbers if present
                        if content.annotations:
                            # inline citation numbers handled; detailed reference list appended later
                            pass
                    elif content.type == "output_refusal":
                        md_parts.append(f"> ⚠️ Response refused: {content.refusal}")
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
                tool_icon = self._get_tool_icon(item.type)
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
                result_summary = self._get_tool_result_summary(item)

                # Format: Tool Icon + Bold Name + Status Icon + Status + Result
                # Example: 󱁴 **File Search** ✓ _completed_ → "query" found 5 results
                tool_line = f"{tool_icon} _{tool_name}_ • {status_icon}_{item.status}_"

                if result_summary:
                    tool_line += f" {ICONS['bullet']} {result_summary}"

                # Check if this tool is traceable and has execution trace
                trace_block = self._get_trace_block(item)
                if trace_block:
                    # For traceable tools, show tool line + trace block
                    md_parts.append(tool_line)
                    md_parts.append("\n".join(trace_block))
                else:
                    # For non-traceable tools, show just the tool line
                    md_parts.append(tool_line)
            elif is_reasoning_item(item):
                # Use the text property to get consolidated reasoning text
                reasoning_text = item.text
                if reasoning_text:
                    # Use Builder pattern for clean text processing
                    processed_text = Build(reasoning_text).with_block_quote().build()
                    md_parts.append(processed_text)

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
        # title_parts.append(response.id)

        # Status
        # if response.status:
        #     title_parts.append(response.status)

        # Usage information with icons from style.py
        if response.usage:
            title_parts.append("[yellow]" + ICONS["input_tokens"] + "[/yellow]")
            title_parts.append(f"[green]{response.usage.input_tokens}[/green]")
            title_parts.append("[yellow]" + ICONS["output_tokens"] + "[/yellow]")
            title_parts.append(f"[green]{response.usage.output_tokens}[/green]")

        panel_title = " ".join(title_parts)

        # Determine panel style based on response status
        border_style, title_style = self._get_panel_style(response)

        return Panel(
            markdown_content,
            title=panel_title,
            border_style=border_style,
            title_align="left",
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

    def _get_trace_preview(self, tool_item: Any, max_length: int = 35) -> str | None:
        """Extract the last trace message from a traceable tool for display.

        Args:
            tool_item: The tool item to extract trace from
            max_length: Maximum length of the trace message to display

        Returns:
            Formatted trace message or None if no trace available
        """
        execution_trace = getattr(tool_item, "execution_trace", None)
        if not execution_trace:
            return None

        # Show last trace line as a preview
        trace_lines = execution_trace.strip().split("\n")
        if not trace_lines:
            return None

        last_line = trace_lines[-1]
        # Extract just the message part (remove timestamp and step name)
        if "] " in last_line:
            message = last_line.split("] ")[-1][:max_length]
            if len(message) > max_length - 3:
                message = message[: max_length - 3] + "..."
            return f"{ICONS['check']}{message}"
        return None

    def _get_trace_block(self, tool_item: Any) -> list[str] | None:
        """Extract the last few trace lines from a traceable tool for sliding display.

        Args:
            tool_item: The tool item to extract trace from

        Returns:
            List of formatted trace lines or None if no trace available
        """
        execution_trace = getattr(tool_item, "execution_trace", None)
        if not execution_trace:
            return None

        # Use Builder pattern for clean sliding display processing
        return Build(execution_trace).with_slide(max_lines=3, format_type="text").build()

    def _get_tool_result_summary(self, tool_item: Any) -> str:
        """Create a concise, beautiful summary of tool results."""
        if is_file_search_call(tool_item):
            # Show query/queries with search icon and result count
            query_parts = []
            # File search calls have queries (list), not a single query
            if tool_item.queries:
                # Use pack_queries for beautiful multi-query display
                shortened_queries = [q[:30] + "..." if len(q) > 30 else q for q in tool_item.queries]
                packed = pack_queries(*[f"{q}" for q in shortened_queries])
                query_parts.append(packed)

            if query_parts:
                return f" {ICONS['bullet']} ".join(query_parts)
            elif tool_item.status == "searching":
                return f"{ICONS['searching']} init"
            return "preparing file search"

        elif is_web_search_call(tool_item):
            # Show web search with globe icon
            parts = []
            if tool_item.queries:
                # Use pack_queries for beautiful display
                shortened_queries = [q[:30] + "..." if len(q) > 30 else q for q in tool_item.queries]
                packed = pack_queries(*[f"{q}" for q in shortened_queries])
                parts.append(packed)

            if parts:
                return f" {ICONS['bullet']} ".join(parts)
            return f"{ICONS['searching']} init"

        elif is_list_documents_call(tool_item):
            # Show document listing with magnifying glass
            parts = []
            if tool_item.queries:
                # Use pack_queries for consistent display
                shortened_queries = [q[:25] + "..." if len(q) > 25 else q for q in tool_item.queries]
                packed = pack_queries(*[f"{q}" for q in shortened_queries])
                parts.append(packed)

            if parts:
                return f" {ICONS['bullet']} ".join(parts)
            return f"{ICONS['searching']} init"

        elif is_file_reader_call(tool_item):
            # Show file reading with book icon and detailed info
            parts = []

            # File identification
            file_name = getattr(tool_item, "file_name", None)
            if file_name:
                # Show file extension
                ext = file_name.split(".")[-1].lower() if "." in file_name else "file"
                name_short = file_name[:30] + "..." if len(file_name) > 30 else file_name
                parts.append(f'{ICONS["file_reader_call"]}"{name_short}" [{ext.upper()}]')
            elif tool_item.doc_ids and len(tool_item.doc_ids) > 0:
                parts.append(f"{ICONS['file_reader_call']}file:{tool_item.doc_ids[0][:12]}...")

            # Show progress if available (inherited from TraceableToolCall)
            progress = getattr(tool_item, "progress", None)
            if progress is not None:
                progress_percent = int(progress * 100)
                parts.append(f"{ICONS['processing']}{progress_percent}%")

            # Note: execution trace is now handled separately in trace block

            if parts:
                return f" {ICONS['bullet']} ".join(parts)
            return f"{ICONS['processing']}loading file..."

        elif is_page_reader_call(tool_item):
            # Show page reading with page icon and detailed info
            parts = []

            # Document identification
            document_id = tool_item.document_id
            start_page = tool_item.start_page
            end_page = tool_item.end_page

            if document_id:
                # Show document with page range
                doc_short = document_id
                if start_page is not None:
                    if end_page is not None and end_page != start_page:
                        page_info = f"p.{start_page}-{end_page}"
                    else:
                        page_info = f"p.{start_page}"
                    parts.append(f"{ICONS['page_reader_call']} 󰈙 {doc_short} 󰕅 [{page_info}]")
                else:
                    parts.append(f"{ICONS['page_reader_call']} 󰈙 {doc_short}")

            # Show progress if available (inherited from TraceableToolCall)
            progress = getattr(tool_item, "progress", None)
            if progress is not None:
                progress_percent = int(progress * 100)
                parts.append(f"{ICONS['processing']}{progress_percent}%")

            # Note: execution trace is now handled separately in trace block

            if parts:
                return f" {ICONS['bullet']} ".join(parts)
            return f"{ICONS['processing']}loading pages..."

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
                lines = [line.strip() for line in code.split("\n") if line.strip() and not line.strip().startswith("#")]
                if lines:
                    code_preview = lines[0][:35] + "..." if len(lines[0]) > 35 else lines[0]
                    parts.append(f"{ICONS['code']}{lang}: `{code_preview}`")

                    # Show line count for longer code
                    total_lines = len([line for line in code.split("\n") if line.strip()])
                    if total_lines > 5:
                        parts.append(f"{ICONS['code']}{total_lines} lines")

            # Show output if available
            output = getattr(tool_item, "output", None)
            if output:
                output_preview = str(output)[:30] + "..." if len(str(output)) > 30 else str(output)
                parts.append(f"{ICONS['output_tokens']}output: {output_preview}")

            if parts:
                return f" {ICONS['bullet']} ".join(parts)
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
                    except Exception:
                        parts.append(f"{ICONS['code']}(with arguments)")

            # Show result preview if available
            output = getattr(tool_item, "output", None)
            if output:
                output_str = str(output)[:40] + "..." if len(str(output)) > 40 else str(output)
                parts.append(f"{ICONS['check']}{output_str}")

            if parts:
                return f" {ICONS['bullet']} ".join(parts)
            return f"{ICONS['processing']}calling function..."

        # Default fallback
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
        ascii_art = r"""
  ____            _            _      _____             _
 / ___|___  _ __ | |_ _____  _| |_   | ____|_ __   __ _(_)_ __   ___
| |   / _ \| '_ \| __/ _ \ \/ / __|  |  _| | '_ \ / _` | | '_ \ / _ \
| |__| (_) | | | | ||  __/>  <| |_   | |___| | | | (_| | | | | |  __/
 \____\___/|_| |_|\__\___/_/\_\\__|  |_____|_| |_|\__, |_|_| |_|\___|
                                                  |___/

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

    def show_status_rich(self, content: Any) -> None:
        """Show Rich content (tables, panels, etc) directly."""
        self._console.print(content)
