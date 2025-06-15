"""Plaintext renderer for v3 display - uses Rich Live and Text with custom colors."""

import time
from typing import Any, Optional

from pydantic import BaseModel, Field, validator
from rich.console import Console
from rich.live import Live
from rich.text import Text

from forge_cli.response._types.response import Response

from ..base import BaseRenderer


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

    @validator("refresh_rate")
    def validate_refresh_rate(cls, v):
        if v < 1 or v > 30:
            raise ValueError("Refresh rate must be between 1 and 30")
        return v

    @validator("indent_size")
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
            if item.type == "message":
                # Handle message content
                for content in item.content:
                    if content.type == "output_text":
                        # Add the text content with white color
                        self._add_formatted_text(text, content.text, style=self._styles["content"])
                        # Add inline annotations if available
                        if content.annotations and self._config.show_citations:
                            self._add_inline_annotations(text, content.annotations)
                    elif content.type == "output_refusal":
                        text.append("⚠️  Response Refused: ", style=self._styles["warning"])
                        text.append(f"{content.refusal}\n", style=self._styles["error"])

            elif item.type == "reasoning" and self._config.show_reasoning:
                # Handle reasoning content with dark green italic style
                if hasattr(item, "summary") and item.summary:
                    # text.append("🤔 ", style=self._styles["reasoning_header"])
                    # text.append("AI Thinking Process", style=self._styles["reasoning_header"])
                    text.append("\n", style="")

                    for summary in item.summary:
                        if hasattr(summary, "text") and summary.text:
                            # Add reasoning text with dark green italic style
                            reasoning_lines = summary.text.split("\n")
                            for line in reasoning_lines:
                                if line.strip():
                                    indent = "" * self._config.indent_size
                                    text.append(f"{indent}{line.strip()}\n", style=self._styles["reasoning"])
                                else:
                                    text.append("\n")
                    text.append("\n")

            elif (
                item.type in ["file_search_call", "web_search_call", "document_finder_call", "file_reader_call"]
                and self._config.show_tool_details
            ):
                # Handle tool calls with colorful display
                self._add_tool_item(text, item)

        # Add citations section at the end if enabled
        if self._config.show_citations:
            citations = self._extract_all_citations(response)
            if citations:
                self._add_separator(text, "SOURCES")
                self._add_citation_list(text, citations)

        # Add usage statistics if enabled
        if self._config.show_usage and response.usage:
            self._add_usage_content(text, response)

        return text

    def _add_status_header(self, text: Text, response: Response) -> None:
        """Add status header information."""
        # Main title
        text.append("🔥 Knowledge Forge Response", style=self._styles["header"])
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
        tool_type = tool_item.type

        if tool_type == "file_search_call":
            # Show query and result count
            parts = []
            if hasattr(tool_item, "query") and tool_item.query:
                parts.append(f' {query}')
            elif hasattr(tool_item, "queries") and tool_item.queries:
                query = " ".join(" {query}" for query in tool_item.queries)
                parts.append(f' {query}')
            if hasattr(tool_item, "results") and tool_item.results:
                parts.append(f"found {len(tool_item.results)} results")

            return " • ".join(parts) if parts else ""

        elif tool_type == "web_search_call":
            # Show search query and results
            if hasattr(tool_item, "queries") and tool_item.queries:
                query = " ".join(" {query}" for query in tool_item.queries)
                parts.append(f'󰜏 {query}')
            if hasattr(tool_item, "results") and tool_item.results:
                parts.append(f"found {len(tool_item.results)} results")

            return " • ".join(parts) if parts else ""

        elif tool_type == "document_finder_call":
            # Show query and document count
            parts = []
            if hasattr(tool_item, "query") and tool_item.query:
                parts.append(f'󰈞 {tool_item.query}')
            if hasattr(tool_item, "results") and tool_item.results:
                doc_count = len(tool_item.results)
                parts.append(f"found {doc_count} document{'s' if doc_count != 1 else ''}")

            return " • ".join(parts) if parts else ""

        elif tool_type == "file_reader_call":
            # Show file name and status
            parts = []
            if hasattr(tool_item, "file_name") and tool_item.file_name:
                parts.append(f'󰑇 {tool_item.file_name}')
            elif hasattr(tool_item, "file_id") and tool_item.file_id:
                parts.append(f"󰻾 {tool_item.file_id}")
            return " • ".join(parts) if parts else ""

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
                text.append("🔸 ", style=self._styles["header"])
                text.append(line[2:], style=self._styles["header"])
                text.append("\n")
            elif line.startswith("## "):
                text.append("  ▸ ", style=self._styles["info"])
                text.append(line[3:], style="bold white")
                text.append("\n")
            elif line.startswith("### "):
                text.append("    • ", style=self._styles["citation_ref"])
                text.append(line[4:], style="bold dim white")
                text.append("\n")
            # Handle bullet points
            elif line.startswith("- ") or line.startswith("* "):
                indent = " " * self._config.indent_size
                text.append(f"{indent}• ", style=self._styles["citation_ref"])
                text.append(line[2:], style=style)
                text.append("\n")
            # Handle numbered lists
            elif line and line[0].isdigit() and ". " in line:
                indent = " " * self._config.indent_size
                parts = line.split(". ", 1)
                text.append(f"{indent}{parts[0]}. ", style=self._styles["citation_ref"])
                if len(parts) > 1:
                    text.append(parts[1], style=style)
                text.append("\n")
            # Regular text with bold/italic handling
            else:
                formatted_line = self._apply_inline_formatting(line, base_style=style)
                text.append(formatted_line)
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
        text.append(f"{tool_icon} ", style=self._styles["tool_icon"])

        # Tool name with vibrant color
        tool_name = tool_item.type.replace("_call", "").replace("_", " ").title()
        text.append(f"{tool_name}", style=self._styles["tool_name"])
        text.append(" • ", style=self._styles["separator"])

        # Status with appropriate color and icon using the pattern
        icon, style = self.status_icon(tool_item.status)
        text.append(icon, style=style)
        # text.append(tool_item.status, style=style)

        # Tool-specific details with cyan color
        details = self._get_tool_details(tool_item)
        if details:
            text.append(" • ", style=self._styles["separator"])
            text.append(details, style=self._styles["tool_details"])

        text.append("\n\n")

    def _add_citation_list(self, text: Text, citations: list[dict[str, Any]]) -> None:
        """Add citation list with proper formatting."""
        for i, citation in enumerate(citations, 1):
            # Citation reference number
            text.append(f"[{i}] ", style=self._styles["citation_ref"])

            # Source information based on citation type
            if citation.get("type") == "file_citation":
                source = citation.get("file_name") or citation.get("file_id", "Unknown File")
                text.append(f"{source}", style=self._styles["citation_source"])
                
                # Page/index number if available
                if citation.get("page_number") is not None:
                    text.append(f" (index {citation['page_number']})", style="dim")
                    
            elif citation.get("type") == "url_citation":
                # Show title with URL
                title = citation.get("title", "Web Page")
                url = citation.get("url", "")
                if url:
                    # Extract domain for compact display
                    try:
                        from urllib.parse import urlparse
                        domain = urlparse(url).netloc
                        if domain.startswith("www."):
                            domain = domain[4:]
                        text.append(f"{title}", style=self._styles["citation_source"])
                        text.append(f" ({domain})", style="dim")
                    except:
                        text.append(f"{title}", style=self._styles["citation_source"])
                else:
                    text.append(f"{title}", style=self._styles["citation_source"])
            else:
                # Fallback for unknown types
                source = citation.get("file_name", citation.get("url", "Unknown"))
                text.append(f"{source}", style=self._styles["citation_source"])

            text.append("\n")

            # Quote/snippet if available
            if citation.get("text"):
                quote = citation["text"]
                if len(quote) > self._config.max_text_preview:
                    quote = quote[: self._config.max_text_preview - 3] + "..."

                indent = " " * (self._config.indent_size + 2)
                text.append(f'{indent}"{quote}"\n', style=self._styles["citation_text"])

            text.append("\n")

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
        text.append(" ⇓ ", style=self._styles["usage_label"])
        text.append(f"{usage.input_tokens or 0}", style=self._styles["usage"])
        text.append(" ⇑ ", style=self._styles["usage_label"])
        text.append(f"{usage.output_tokens or 0}", style=self._styles["usage"])
        text.append("\n")

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
                                    "text": getattr(annotation, "snippet", ""),  # Use snippet instead of text
                                }

                                if annotation.type == "file_citation":
                                    citation_data.update(
                                        {
                                            "file_id": getattr(annotation, "file_id", ""),
                                            "file_name": getattr(annotation, "filename", ""),  # Use filename instead of file_name
                                            "page_number": getattr(annotation, "index", None),  # Use index instead of page_number
                                        }
                                    )
                                elif annotation.type == "url_citation":
                                    citation_data.update(
                                        {
                                            "url": getattr(annotation, "url", ""),
                                            "title": getattr(annotation, "title", ""),
                                        }
                                    )

                                citations.append(citation_data)

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
        return {
            "completed": "✅",
            "failed": "❌",
            "in_progress": "⏳",
            "incomplete": "⚠️",
        }.get(status, "ℹ️")

    def _get_tool_icon(self, tool_type: str) -> str:
        """Get icon for tool type."""
        return {
            "file_search_call": "📄",
            "web_search_call": "🌐",
            "document_finder_call": "🔍",
            "file_reader_call": "📖",
            "code_interpreter_call": "💻",
            "function_call": "🔧",
        }.get(tool_type, "🛠️")

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

    def render_welcome(self, config: Any) -> None:
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

        if hasattr(config, "model"):
            welcome_text.append("🤖 Model: ", style=self._styles["info"])
            welcome_text.append(f"{config.model}\n", style=self._styles["model"])

        if hasattr(config, "enabled_tools") and config.enabled_tools:
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
