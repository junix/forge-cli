"""Plaintext renderer for the v3 display system."""

import time
from typing import TYPE_CHECKING, Any, Optional

from pydantic import BaseModel, Field, field_validator
from rich.console import Console
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

from ..base import BaseRenderer
from ....common.logger import logger
from ..style import ICONS, STATUS_ICONS

if TYPE_CHECKING:
    from ....config import AppConfig


class PlaintextDisplayConfig(BaseModel):
    """Configuration for plaintext renderer display options."""

    show_reasoning: bool = Field(True, description="Whether to show reasoning/thinking content")
    show_citations: bool = Field(True, description="Whether to show citation details")
    show_tool_details: bool = Field(True, description="Whether to show detailed tool information")
    show_usage: bool = Field(True, description="Whether to show token usage statistics")
    show_metadata: bool = Field(False, description="Whether to show response metadata")
    show_status_header: bool = Field(True, description="Whether to show status header")
    max_text_preview: int = Field(100, description="Maximum characters for text previews")
    refresh_rate: int = Field(10, description="Live display refresh rate per second")
    indent_size: int = Field(2, description="Number of spaces for indentation")
    separator_char: str = Field("─", description="Character for separators")
    separator_length: int = Field(60, description="Length of separator lines")

    @field_validator("refresh_rate")
    @classmethod
    def validate_refresh_rate(cls, v):
        if v < 1 or v > 30:
            raise ValueError("Refresh rate must be between 1 and 30")
        return v

    @field_validator("indent_size")
    @classmethod
    def validate_indent_size(cls, v):
        if v < 0 or v > 8:
            raise ValueError("Indent size must be between 0 and 8")
        return v


class PlaintextRenderer(BaseRenderer):
    """Plaintext renderer for v3 display system using Rich Live and Text.

    Creates beautiful, colorful plaintext output without panels or markdown.
    Uses only Rich's Live display and Text components with custom styling.
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

        # Live display management
        self._live: Live | None = None
        self._live_started = False

        # State tracking
        self._last_response_id: str | None = None
        self._start_time = time.time()
        self._render_count = 0

        # Style definitions
        self._styles = {
            "header": "bold cyan",
            "status_completed": "bold green",
            "status_failed": "bold red",
            "status_in_progress": "bold yellow",
            "status_default": "bold blue",
            "model": "green",
            "id": "dim white",
            "separator": "dim blue",
            "content": "white",  # 正式文本用白色
            "tool_icon": "yellow",
            "tool_name": "bold magenta",  # 工具名称用洋红色，更活泼
            "tool_status_completed": "bold green",
            "tool_status_in_progress": "bold yellow",
            "tool_status_failed": "bold red",
            "tool_details": "cyan",  # 工具细节用青色
            "reasoning": "italic dark_green",  # 推理文本用暗绿色斜体
            "reasoning_header": "bold dark_green",
            "citation_ref": "bold cyan",
            "citation_source": "blue",
            "citation_text": "dim",
            "usage": "green",
            "usage_label": "cyan",
            "error": "bold red",
            "warning": "bold orange3",
            "info": "cyan",
            "success": "green",
        }

    def render_response(self, response: Response) -> None:
        """Render a complete response snapshot using Rich Text and Live.

        This is the core v3 method - everything is available in the response object.
        """
        self._ensure_not_finalized()
        self._render_count += 1

        # Initialize live display if needed
        if not self._live_started:
            self._start_live_display()

        # Create text content from response
        content = self._create_response_text(response)

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
            initial_text = Text("Starting Knowledge Forge...", style=self._styles["info"])
            self._live = Live(
                initial_text,
                console=self._console,
                refresh_per_second=self._config.refresh_rate,
                transient=False,
            )

        if not self._live_started:
            self._live.start()
            self._live_started = True

    def _create_response_text(self, response: Response) -> Text:
        """Create Rich Text from complete response snapshot."""
        text = Text()

        # Add status header
        # if self._config.show_status_header:

        # Process output items in their original order to preserve event sequence
        for item in response.output:
            if is_message_item(item):
                # Handle message content
                for content in item.content:
                    if content.type == "output_text":
                        # Add the text content with white color
                        self._add_formatted_text(text, content.text, style=self._styles["content"])
                        # Don't add inline annotations - they're already in the text as ⟦⟦1⟧⟧
                    elif content.type == "output_refusal":
                        text.append("⚠️  Response Refused: ", style=self._styles["warning"])
                        text.append(f"{content.refusal}\n", style=self._styles["error"])

            elif is_reasoning_item(item) and self._config.show_reasoning:
                # Handle reasoning content with dark green italic style using the text property
                reasoning_text = item.text
                if reasoning_text:
                    text.append("\n", style="")
                    
                    # Add reasoning text with dark green italic style
                    reasoning_lines = reasoning_text.split("\n")
                    for line in reasoning_lines:
                        if line.strip():
                            indent = " " * self._config.indent_size
                            text.append(f"{indent}{line.strip()}\n", style=self._styles["reasoning"])
                        else:
                            text.append("\n")
                    text.append("\n")

            elif (
                item.type
                in [
                    "file_search_call",
                    "web_search_call",
                    "list_documents_call",
                    "file_reader_call",
                    "page_reader_call",
                ]
                and self._config.show_tool_details
            ):
                # Handle tool calls with colorful display
                self._add_tool_item(text, item)

        # Add citations section at the end if enabled
        if self._config.show_citations:
            citations = self._extract_all_citations(response)
            if citations:
                # Add a simple newline before citations, no separator
                text.append("\n")
                self._add_citation_list(text, citations)

        # Add usage statistics if enabled
        if self._config.show_usage and response.usage:
            self._add_usage_content(text, response)

        return text

    def _add_status_header(self, text: Text, response: Response) -> None:
        """Add status header information."""
        # Main title
        text.append(f"{ICONS['processing']}Knowledge Forge Response", style=self._styles["header"])
        text.append("\n")

        # Response details
        text.append("ID: ", style=self._styles["info"])
        text.append(f"{response.id[:12]}...", style=self._styles["id"])

        if response.status:
            #     text.append(" │ Status: ", style=self._styles["info"])
            status_style = self._get_status_style(response.status)
            status_icon = self._get_status_icon(response.status)
            text.append(f"{status_icon} {response.status.upper()}", style=status_style)

        # if response.model:
        #     text.append(" │ Model: ", style=self._styles["info"])
        #     text.append(f"{response.model}", style=self._styles["model"])

        # Render count for streaming feedback
        text.append(" │ # ", style=self._styles["info"])
        text.append(f"{self._render_count}", style=self._styles["warning"])

        text.append("\n")

    def _add_separator(self, text: Text, label: str = None) -> None:
        """Add a separator line with optional label."""
        if label:
            # Calculate padding for centered label
            total_length = self._config.separator_length
            label_length = len(label) + 2  # +2 for spaces around label
            left_padding = (total_length - label_length) // 2
            right_padding = total_length - label_length - left_padding

            separator_line = (
                self._config.separator_char * left_padding + f" {label} " + self._config.separator_char * right_padding
            )
        else:
            separator_line = self._config.separator_char * self._config.separator_length

        text.append(separator_line, style=self._styles["separator"])
        text.append("\n")

    def _get_tool_details(self, tool_item: Any) -> str:
        """Get concise details for a tool item."""
        if is_file_search_call(tool_item):
            # Show query and result count
            parts = []
            if tool_item.queries:
                # Use pack_queries for beautiful display
                shortened_queries = [q[:30] + "..." if len(q) > 30 else q for q in tool_item.queries]
                packed = pack_queries(*[f'"{q}"' for q in shortened_queries])
                parts.append(packed)
            # Note: results are not directly accessible from tool_item

            return f" {ICONS['bullet']} ".join(parts) if parts else ""

        elif is_web_search_call(tool_item):
            # Show search query and results
            parts = []
            if tool_item.queries:
                # Use pack_queries for consistent display
                shortened_queries = [q[:30] + "..." if len(q) > 30 else q for q in tool_item.queries]
                packed = pack_queries(*[f'"{q}"' for q in shortened_queries])
                parts.append(packed)
            # Note: results are not directly accessible from tool_item

            return f" {ICONS['bullet']} ".join(parts) if parts else ""

        elif is_list_documents_call(tool_item):
            # Show queries and document count
            parts = []
            if tool_item.queries:
                # Show all queries
                # Use pack_queries for consistent display
                shortened_queries = [q[:25] + "..." if len(q) > 25 else q for q in tool_item.queries]
                packed = pack_queries(*[f'"{q}"' for q in shortened_queries])
                parts.append(packed)

            # # Show document count
            # if tool_item.count is not None:
            #     parts.append(f"found {tool_item.count} document{'s' if tool_item.count != 1 else ''}")
            # elif getattr(tool_item, "results", None):
            #     doc_count = len(tool_item.results)
            #     parts.append(f"found {doc_count} document{'s' if doc_count != 1 else ''}")

            return f" {ICONS['bullet']} ".join(parts) if parts else ""

        elif is_file_reader_call(tool_item):
            # Show file name and status
            parts = []
            # Note: file_name might be added dynamically, not in the base model
            file_name = getattr(tool_item, "file_name", None)
            if file_name:
                parts.append(f"{ICONS['file_reader_call']}{file_name}")
            elif tool_item.doc_ids and len(tool_item.doc_ids) > 0:
                # Use first doc_id as fallback
                parts.append(f"{ICONS['file_reader_call']}{tool_item.doc_ids[0]}")

            # Show progress if available (inherited from TraceableToolCall)
            progress = getattr(tool_item, "progress", None)
            if progress is not None:
                progress_percent = int(progress * 100)
                parts.append(f"{ICONS['processing']}{progress_percent}%")

            # Show execution trace preview if available (for traceable tools)
            execution_trace = getattr(tool_item, "execution_trace", None)
            if execution_trace:
                # Show last trace line as a preview
                trace_lines = execution_trace.strip().split("\n")
                if trace_lines:
                    last_line = trace_lines[-1]
                    # Extract just the message part (remove timestamp and step name)
                    if "] " in last_line:
                        message = last_line.split("] ")[-1][:30]
                        if len(message) > 27:
                            message = message[:27] + "..."
                        parts.append(f"{ICONS['check']}{message}")

            return f" {ICONS['bullet']} ".join(parts) if parts else ""

        elif is_page_reader_call(tool_item):
            # Show page reading with document info
            parts = []
            document_id = getattr(tool_item, "document_id", None)
            if document_id:
                # Shorten document ID for display
                doc_short = document_id[:8] if len(document_id) > 8 else document_id
                start_page = getattr(tool_item, "start_page", None)
                end_page = getattr(tool_item, "end_page", None)

                if start_page is not None:
                    if end_page is not None and end_page != start_page:
                        page_info = f"p.{start_page}-{end_page}"
                    else:
                        page_info = f"p.{start_page}"
                    parts.append(f"{ICONS['page_reader_call']}doc:{doc_short} [{page_info}]")
                else:
                    parts.append(f"{ICONS['page_reader_call']}doc:{doc_short}")

            # Show progress if available (inherited from TraceableToolCall)
            progress = getattr(tool_item, "progress", None)
            if progress is not None:
                progress_percent = int(progress * 100)
                parts.append(f"{ICONS['processing']}{progress_percent}%")

            # Show execution trace preview if available (for traceable tools)
            execution_trace = getattr(tool_item, "execution_trace", None)
            if execution_trace:
                # Show last trace line as a preview
                trace_lines = execution_trace.strip().split("\n")
                if trace_lines:
                    last_line = trace_lines[-1]
                    # Extract just the message part (remove timestamp and step name)
                    if "] " in last_line:
                        message = last_line.split("] ")[-1][:30]
                        if len(message) > 27:
                            message = message[:27] + "..."
                        parts.append(f"{ICONS['check']}{message}")

            return f" {ICONS['bullet']} ".join(parts) if parts else ""

        else:
            return ""

    def _add_formatted_text(self, text: Text, content: str, style: str = None) -> None:
        """Add formatted text content with simple markdown-like styling."""
        if style is None:
            style = self._styles["content"]

        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                text.append("\n")
                continue

            # Handle headers
            if line.startswith("# "):
                # Create centered header by calculating padding
                header_text = line[2:]
                console_width = getattr(self._console.size, "width", 80)  # Default to 80 if size unavailable
                header_width = len(header_text)
                padding = max(0, (console_width - header_width) // 2)
                centered_header = " " * padding + header_text
                text.append(centered_header, style=self._styles["header"])
                text.append("\n")
            elif line.startswith("## "):
                # Create centered header by calculating padding
                header_text = line[3:]
                console_width = getattr(self._console.size, "width", 80)  # Default to 80 if size unavailable
                header_width = len(header_text)
                padding = max(0, (console_width - header_width) // 2)
                centered_header = " " * padding + header_text
                text.append(centered_header, style="bold white")
                text.append("\n")
            elif line.startswith("### "):
                # Create centered header by calculating padding
                header_text = line[4:]
                console_width = getattr(self._console.size, "width", 80)  # Default to 80 if size unavailable
                header_width = len(header_text)
                padding = max(0, (console_width - header_width) // 2)
                centered_header = " " * padding + header_text
                text.append(centered_header, style="bold dim white")
                text.append("\n")
            # Handle bullet points
            # elif line.startswith("- ") or line.startswith("* "):
            #     indent = "" * self._config.indent_size
            #     text.append(f"{indent}• ", style=self._styles["citation_ref"])
            #     text.append(line[2:], style=style)
            #     text.append("\n")
            # # Handle numbered lists
            # elif line and line[0].isdigit() and ". " in line:
            #     indent = " " * self._config.indent_size
            #     parts = line.split(". ", 1)
            #     text.append(f"{indent}{parts[0]}. ", style=self._styles["citation_ref"])
            #     if len(parts) > 1:
            #         text.append(parts[1], style=style)
            #     text.append("\n")
            # Regular text with bold/italic handling
            else:
                # formatted_line = self._apply_inline_formatting(line, base_style=style)
                text.append(line)
                text.append("\n")

    def _apply_inline_formatting(self, line: str, base_style: str = None) -> Text:
        """Apply simple inline formatting like **bold** and *italic*."""
        if base_style is None:
            base_style = self._styles["content"]

        result = Text()
        i = 0

        while i < len(line):
            # Check for **bold**
            if i < len(line) - 3 and line[i : i + 2] == "**":
                end = line.find("**", i + 2)
                if end != -1:
                    result.append(line[i + 2 : end], style="bold " + base_style)
                    i = end + 2
                    continue

            # Check for *italic*
            if i < len(line) - 2 and line[i] == "*" and line[i + 1] != "*":
                end = line.find("*", i + 1)
                if end != -1:
                    result.append(line[i + 1 : end], style="italic " + base_style)
                    i = end + 1
                    continue

            # Check for `code`
            if i < len(line) - 2 and line[i] == "`":
                end = line.find("`", i + 1)
                if end != -1:
                    result.append(line[i + 1 : end], style="bold green")
                    i = end + 1
                    continue

            # Regular character
            result.append(line[i], style=base_style)
            i += 1

        return result

    def status_icon(self, status: str) -> tuple[str, str]:
        """Get icon for status."""
        return {
            "completed": ("  ", self._styles["status_completed"]),
            "in_progress": (" 󰜎 ", self._styles["status_in_progress"]),
            "failed": ("  ", self._styles["status_failed"]),
            "incomplete": ("  ", self._styles["status_default"]),
        }.get(status, ("  ", "white"))

    def _add_tool_item(self, text: Text, tool_item: Any) -> None:
        """Add a single tool execution item with colorful display."""
        # Tool icon
        tool_icon = self._get_tool_icon(tool_item.type)
        text.append(f"{tool_icon}", style=self._styles["tool_icon"])

        # Tool name with vibrant color
        tool_name = tool_item.type.replace("_call", "").replace("_", " ").title()
        text.append(f"{tool_name}", style=self._styles["tool_name"])
        text.append(f" {ICONS['bullet']} ", style=self._styles["separator"])

        # Status with appropriate color and icon using the pattern
        icon, style = self.status_icon(tool_item.status)
        text.append(icon, style=style)
        # text.append(tool_item.status, style=style)

        # Tool-specific details with cyan color
        details = self._get_tool_details(tool_item)
        if details:
            text.append(f" {ICONS['bullet']} ", style=self._styles["separator"])
            text.append(details, style=self._styles["tool_details"])

        text.append("\n\n")

    def _add_citation_list(self, text: Text, citations: list[Any]) -> None:
        """Add citation list with proper formatting using type-based API."""
        # Use compact format for file citations
        text.append("ref:\n", style=self._styles["citation_ref"])

        for i, citation in enumerate(citations, 1):
            if citation.type == "file_citation":
                # Compact format: 1. filename, P{index} - using typed properties
                source = citation.filename or citation.file_id or "Unknown"
                page = f", P{citation.index}" if citation.index is not None else ""
                text.append(f"{i}. {source}{page}\n", style=self._styles["citation_source"])

            elif citation.type == "url_citation":
                # URL format: 1. title (domain) - using typed properties
                title = citation.title if citation.title else "Web Page"
                url = citation.url
                if url:
                    try:
                        from urllib.parse import urlparse

                        domain = urlparse(url).netloc
                        if domain.startswith("www."):
                            domain = domain[4:]
                        text.append(f"{i}. {title} ({domain})\n", style=self._styles["citation_source"])
                    except Exception:
                        text.append(f"{i}. {title}\n", style=self._styles["citation_source"])
                else:
                    text.append(f"{i}. {title}\n", style=self._styles["citation_source"])
            elif citation.type == "file_path":
                # File path format - using typed properties
                source = citation.file_id or "Unknown"
                text.append(f"{i}. {source}\n", style=self._styles["citation_source"])
            else:
                # Fallback format
                source = getattr(citation, "filename", getattr(citation, "url", "Unknown"))
                text.append(f"{i}. {source}\n", style=self._styles["citation_source"])

    # Remove old methods that are no longer needed
    # The functionality has been integrated into the main flow

    def _add_inline_annotations(self, text: Text, annotations: list[Any]) -> None:
        """Add inline annotation references."""
        if not annotations:
            return

        text.append("📎 References: ", style="dim")
        for i, annotation in enumerate(annotations):
            if i > 0:
                text.append(", ", style="dim")
            text.append(f"[{i + 1}]", style=self._styles["citation_ref"])
        text.append("\n")

    def _add_usage_content(self, text: Text, response: Response) -> None:
        """Add usage statistics."""

        # self._add_status_header(text, response)

        usage = response.usage
        # self._add_separator(text, "USAGE")

        # text.append("📊 Token Usage: ", style=self._styles["usage_label"])
        # Render count for streaming feedback

        #     text.append(" │ Status: ", style=self._styles["info"])
        text.append("\n")

        icon, style = self.status_icon(response.status)
        text.append(icon, style=style)

        text.append("# ", style=self._styles["info"])
        text.append(f"{self._render_count}", style=self._styles["warning"])
        text.append(f" {ICONS['input_tokens']}", style=self._styles["usage_label"])
        text.append(f"{usage.input_tokens or 0}", style=self._styles["usage"])
        text.append(f" {ICONS['output_tokens']}", style=self._styles["usage_label"])
        text.append(f"{usage.output_tokens or 0}", style=self._styles["usage"])
        text.append("\n")

    def _extract_all_citations(self, response: Response) -> list[Any]:
        """Extract all citations from response annotations using type-based API."""

        citations = []

        for item in response.output:
            if item.type == "message":
                for content in item.content:
                    if content.type == "output_text" and content.annotations:
                        for annotation in content.annotations:
                            # Only include citation types
                            if annotation.type in ["file_citation", "url_citation", "file_path"]:
                                citations.append(annotation)

        return citations

    def _get_status_style(self, status: str) -> str:
        """Get style for status text."""
        return {
            "completed": self._styles["status_completed"],
            "failed": self._styles["status_failed"],
            "in_progress": self._styles["status_in_progress"],
            "incomplete": self._styles["warning"],
        }.get(status, self._styles["status_default"])

    def _get_status_icon(self, status: str) -> str:
        """Get icon for status."""
        return STATUS_ICONS.get(status, STATUS_ICONS["default"])

    def _get_tool_icon(self, tool_type: str) -> str:
        """Get icon for tool type."""
        return ICONS.get(tool_type, ICONS["processing"])

    def _get_tool_status_style(self, status: str) -> str:
        """Get style for tool status."""
        return {
            "completed": self._styles["tool_status_completed"],
            "in_progress": self._styles["tool_status_in_progress"],
            "searching": self._styles["tool_status_in_progress"],
            "interpreting": self._styles["tool_status_in_progress"],
            "failed": self._styles["tool_status_failed"],
        }.get(status, "white")

    def _get_tool_status_icon(self, status: str) -> str:
        """Get icon for tool status."""
        return {
            "completed": "✅",
            "in_progress": "⏳",
            "searching": "🔍",
            "interpreting": "💻",
            "failed": "❌",
        }.get(status, "ℹ️")

    # Additional methods for compatibility with Display interface
    def render_error(self, error: str) -> None:
        """Render error message."""
        error_text = Text()
        error_text.append("❌ ERROR: ", style=self._styles["error"])
        error_text.append(error, style="bold red")

        if self._live and self._live_started:
            self._live.update(error_text)
        else:
            self._console.print(error_text)

    def render_welcome(self, config: "AppConfig") -> None:
        """Show welcome message for chat mode."""
        welcome_text = Text()

        # ASCII art header
        welcome_text.append("╔═══════════════════════════════════════╗\n", style=self._styles["header"])
        welcome_text.append("║        Knowledge Forge v3             ║\n", style=self._styles["header"])
        welcome_text.append("║      Plaintext Display Renderer       ║\n", style=self._styles["header"])
        welcome_text.append("╚═══════════════════════════════════════╝\n", style=self._styles["header"])

        welcome_text.append("\n🔥 Welcome to ", style="bold")
        welcome_text.append("Knowledge Forge Chat", style=self._styles["header"])
        welcome_text.append("! (v3 Plaintext Renderer)\n\n", style="bold")

        if getattr(config, "model", None):
            welcome_text.append("🤖 Model: ", style=self._styles["info"])
            welcome_text.append(f"{config.model}\n", style=self._styles["model"])

        if getattr(config, "enabled_tools", None):
            welcome_text.append("🛠️  Tools: ", style=self._styles["info"])
            welcome_text.append(f"{', '.join(config.enabled_tools)}\n", style=self._styles["content"])

        welcome_text.append("\n💡 Type ", style="dim")
        welcome_text.append("/help", style=self._styles["success"])
        welcome_text.append(" for available commands\n", style="dim")

        self._console.print(welcome_text)

    def render_request_info(self, info: dict) -> None:
        """Show request information."""
        info_text = Text()
        info_text.append("🔍 Query: ", style=self._styles["info"])
        info_text.append(f"{info.get('question', 'N/A')}\n", style=self._styles["content"])

        if info.get("model"):
            info_text.append("🤖 Model: ", style=self._styles["info"])
            info_text.append(f"{info['model']}\n", style=self._styles["model"])

        if info.get("tools"):
            info_text.append("🛠️  Tools: ", style=self._styles["info"])
            info_text.append(f"{', '.join(info['tools'])}\n", style=self._styles["content"])

        self._console.print(info_text)

    def render_status(self, message: str) -> None:
        """Show status message."""
        status_text = Text()
        status_text.append("ℹ️  Status: ", style=self._styles["info"])
        status_text.append(message, style=self._styles["content"])
        self._console.print(status_text)

    def show_status_rich(self, content: Any) -> None:
        """Show Rich content (tables, panels, etc) directly."""
        # For plaintext renderer, we'll display Rich objects directly
        # since we're using Rich console anyway
        self._console.print(content)
