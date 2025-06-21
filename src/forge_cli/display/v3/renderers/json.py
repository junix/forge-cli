"""JSON renderer for the v3 display system."""

import json
import sys
from datetime import datetime
from typing import TYPE_CHECKING, Any, TextIO

from pydantic import BaseModel, Field, field_validator
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.syntax import Syntax

from ..base import BaseRenderer
from ....common.logger import logger
from ....display.citation_styling import long2circled
from ....response._types import Response
from ....response.type_guards import (
    is_code_interpreter_call,
    is_computer_tool_call,
    is_file_citation,
    is_file_path,
    is_file_reader_call,
    is_file_search_call,
    is_function_call,
    is_list_documents_call,
    is_output_refusal,
    is_output_text,
    is_page_reader_call,
    is_reasoning_item,
    is_url_citation,
    is_web_search_call,
)

if TYPE_CHECKING:
    from ....config import AppConfig


class JsonDisplayConfig(BaseModel):
    """Configuration for JSON renderer output options."""

    pretty_print: bool = Field(True, description="Whether to format JSON with indentation")
    indent: int = Field(2, description="Number of spaces for JSON indentation")
    include_metadata: bool = Field(False, description="Whether to include response metadata")
    include_usage: bool = Field(True, description="Whether to include token usage statistics")
    include_timing: bool = Field(False, description="Whether to include timing information")
    output_file: str | None = Field(None, description="File path to write JSON output (None for stdout)")
    append_mode: bool = Field(False, description="Whether to append to output file or overwrite")
    show_panel: bool = Field(True, description="Whether to show JSON in a panel with title")
    panel_title: str = Field("JSON Response", description="Title for the panel")
    syntax_theme: str = Field("monokai", description="Syntax highlighting theme")
    line_numbers: bool = Field(True, description="Whether to show line numbers")

    @field_validator("indent")
    @classmethod
    def validate_indent(cls, v):
        if v < 0 or v > 8:
            raise ValueError("Indent must be between 0 and 8")
        return v


class JsonRenderer(BaseRenderer):
    """JSON renderer for v3 display system.

    Renders complete Response snapshots as formatted JSON output using Rich live updates.
    Follows the v3 design principle of one simple render_response() method.
    """

    def __init__(self, config: JsonDisplayConfig | None = None, output_stream: TextIO | None = None):
        """Initialize JSON renderer.

        Args:
            config: Display configuration
            output_stream: Output stream (defaults to stdout)
        """
        super().__init__()
        self._config = config or JsonDisplayConfig()
        self._output_stream = output_stream or sys.stdout
        self._file_handle: TextIO | None = None
        self._response_count = 0

        # Rich components
        self._console = Console(file=self._output_stream)
        self._live: Live | None = None
        self._current_json = ""

        # Open output file if specified
        if self._config.output_file:
            try:
                mode = "a" if self._config.append_mode else "w"
                self._file_handle = open(self._config.output_file, mode, encoding="utf-8")
                self._console = Console(file=self._file_handle)
            except Exception:
                # Fallback to stdout
                self._console = Console(file=sys.stdout)

    def render_response(self, response: Response) -> None:
        """Render a complete response snapshot as JSON using Rich live updates.

        This is the core v3 method - everything is available in the response object.
        """
        self._ensure_not_finalized()
        self._response_count += 1

        try:
            # Convert response to JSON-serializable format
            json_data = self._response_to_dict(response)

            # Add renderer metadata if enabled
            if self._config.include_metadata:
                json_data["_renderer_metadata"] = {
                    "render_count": self._response_count,
                    "renderer_type": "json_v3_rich",
                    "timestamp": self._get_current_timestamp(),
                }

            # Serialize to JSON
            if self._config.pretty_print:
                json_output = json.dumps(
                    json_data, indent=self._config.indent, ensure_ascii=False, default=self._json_serializer
                )
            else:
                json_output = json.dumps(json_data, ensure_ascii=False, default=self._json_serializer)

            # Store current JSON for live updates
            self._current_json = json_output

            # Create Rich syntax highlighting
            syntax = Syntax(
                json_output,
                "json",
                theme=self._config.syntax_theme,
                line_numbers=self._config.line_numbers,
                word_wrap=True,
            )

            # Create panel if configured
            if self._config.show_panel:
                content = Panel(syntax, title=self._config.panel_title, title_align="left", border_style="blue")
            else:
                content = syntax

            # Start live display if not already started
            if self._live is None:
                self._live = Live(content, console=self._console, refresh_per_second=4)
                self._live.start()
            else:
                # Update existing live display
                self._live.update(content)

        except Exception as e:
            # Show error in Rich format
            error_json = {
                "error": "JSON rendering failed",
                "message": str(e),
                "response_id": response.id if hasattr(response, "id") else None,
            }
            error_output = json.dumps(error_json, indent=self._config.indent)

            # Create Rich syntax highlighting for error
            error_syntax = Syntax(error_output, "json", theme="github-dark", line_numbers=False)

            error_panel = Panel(error_syntax, title="❌ JSON Rendering Error", title_align="left", border_style="red")

            if self._live is None:
                self._live = Live(error_panel, console=self._console, refresh_per_second=4)
                self._live.start()
            else:
                self._live.update(error_panel)

    def finalize(self) -> None:
        """Complete rendering and cleanup resources."""
        try:
            # Stop live display (this preserves the last rendered content)
            if self._live is not None:
                self._live.stop()
                self._live = None

            # Add final metadata if configured (only in debug mode)
            if self._config.include_metadata and self._response_count > 0:
                self._console.print()  # Add spacing
                final_metadata = {
                    "_session_summary": {
                        "total_responses": self._response_count,
                        "renderer_type": "json_v3_rich",
                        "finalized_at": self._get_current_timestamp(),
                    }
                }
                metadata_json = json.dumps(
                    final_metadata, indent=self._config.indent if self._config.pretty_print else None
                )

                # Show metadata as Rich syntax (smaller, less intrusive)
                metadata_syntax = Syntax(metadata_json, "json", theme="github-dark", line_numbers=False)
                metadata_panel = Panel(
                    metadata_syntax, title="📊 Debug: Session Metadata", title_align="left", border_style="dim cyan"
                )
                self._console.print(metadata_panel)

            # Close file handle if we opened one
            if self._file_handle:
                self._file_handle.close()
                self._file_handle = None

        except Exception as e:
            # Show error in Rich format
            self._console.print(f"[red]Error during JSON renderer finalization: {e}[/red]")
        finally:
            super().finalize()

    def _response_to_dict(self, response: Response) -> dict[str, Any]:
        """Convert Response object to JSON-serializable dictionary."""
        # Start with basic response data
        result = {
            "id": response.id,
            "status": response.status,
            "model": response.model,
        }

        # Add output items
        if response.output:
            result["output"] = []
            for item in response.output:
                item_dict = self._serialize_output_item(item)
                result["output"].append(item_dict)

        # Add usage statistics if enabled
        if self._config.include_usage and response.usage:
            result["usage"] = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        # Add timing information if enabled
        if self._config.include_timing:
            result["timing"] = {
                "created_at": getattr(response, "created_at", None),  # TODO: Add to Response type
                "completed_at": getattr(response, "completed_at", None),  # TODO: Add to Response type
            }

        return result

    def _serialize_output_item(self, item: Any) -> dict[str, Any]:
        """Serialize an output item to dictionary format using type guards."""
        # Handle message items
        if is_message_item(item):
            item_dict = {"type": "message"}
            if item.content:
                item_dict["content"] = [self._serialize_content_item(content) for content in item.content]
            return item_dict

        # Handle reasoning items
        elif is_reasoning_item(item):
            item_dict = {"type": "reasoning"}
            if item.summary:
                item_dict["summary"] = [{"text": long2circled(summary.text)} for summary in item.summary if hasattr(summary, "text")]
            return item_dict

        # Handle file search tool calls
        elif is_file_search_call(item):
            item_dict = {
                "type": "file_search_call",
                "id": item.id,
                "status": item.status,
            }
            if item.queries:
                item_dict["queries"] = item.queries
            # Note: Results are accessed through response methods, not directly from item
            return item_dict

        # Handle web search tool calls
        elif is_web_search_call(item):
            item_dict = {
                "type": "web_search_call",
                "id": item.id,
                "status": item.status,
            }
            if item.queries:
                item_dict["queries"] = item.queries
            return item_dict

        # Handle list documents tool calls
        elif is_list_documents_call(item):
            item_dict = {
                "type": "list_documents_call",
                "id": item.id,
                "status": item.status,
            }
            if item.queries:
                item_dict["queries"] = item.queries
            if hasattr(item, "count"):
                item_dict["count"] = item.count
            return item_dict

        # Handle file reader tool calls
        elif is_file_reader_call(item):
            item_dict = {
                "type": "file_reader_call",
                "id": item.id,
                "status": item.status,
            }
            if item.doc_ids:
                item_dict["doc_ids"] = item.doc_ids
            if item.query:
                item_dict["query"] = item.query
            if hasattr(item, "progress") and item.progress is not None:
                item_dict["progress"] = item.progress
            return item_dict

        # Handle page reader tool calls
        elif is_page_reader_call(item):
            item_dict = {
                "type": "page_reader_call",
                "id": item.id,
                "status": item.status,
            }
            if item.document_id:
                item_dict["document_id"] = item.document_id
            if hasattr(item, "start_page") and item.start_page is not None:
                item_dict["start_page"] = item.start_page
            if hasattr(item, "end_page") and item.end_page is not None:
                item_dict["end_page"] = item.end_page
            if hasattr(item, "progress") and item.progress is not None:
                item_dict["progress"] = item.progress
            if hasattr(item, "execution_trace") and item.execution_trace is not None:
                item_dict["execution_trace"] = item.execution_trace
            return item_dict

        # Handle function tool calls
        elif is_function_call(item):
            item_dict = {
                "type": "function_call",
                "id": item.id,
                "call_id": item.call_id,
                "name": item.name,
                "arguments": item.arguments,
            }
            if item.status:
                item_dict["status"] = item.status
            return item_dict

        # Handle computer tool calls
        elif is_computer_tool_call(item):
            item_dict = {
                "type": "computer_call",
                "id": item.id,
                "call_id": item.call_id,
                "status": item.status,
            }
            if hasattr(item, "action"):
                item_dict["action"] = item.action
            return item_dict

        # Handle code interpreter tool calls
        elif is_code_interpreter_call(item):
            item_dict = {
                "type": "code_interpreter_call",
                "id": item.id,
                "status": item.status,
            }
            if item.code:
                item_dict["code"] = item.code
            if item.results:
                item_dict["results"] = item.results
            return item_dict

        # Fallback for unknown item types
        else:
            return {
                "type": "unknown",
                "raw_data": str(item),
                "item_type": type(item).__name__,
            }

    def _serialize_content_item(self, content: Any) -> dict[str, Any]:
        """Serialize a content item to dictionary format using type guards."""
        # Handle output text content
        if is_output_text(content):
            content_dict = {
                "type": "output_text",
                "text": long2circled(content.text),
            }

            # Add annotations if present
            if content.annotations:
                content_dict["annotations"] = [
                    self._serialize_annotation(annotation) for annotation in content.annotations
                ]

            return content_dict

        # Handle output refusal content
        elif is_output_refusal(content):
            return {
                "type": "output_refusal",
                "refusal": content.refusal,
            }

        # Fallback for unknown content types
        else:
            return {
                "type": "unknown_content",
                "raw_data": str(content),
                "content_type": type(content).__name__,
            }

    def _serialize_annotation(self, annotation: Any) -> dict[str, Any]:
        """Serialize an annotation to dictionary format using type guards."""
        # Handle file citation annotations
        if is_file_citation(annotation):
            ann_dict = {"type": "file_citation"}

            # Add available attributes
            if hasattr(annotation, "file_id") and annotation.file_id:
                ann_dict["file_id"] = annotation.file_id
            if hasattr(annotation, "filename") and annotation.filename:
                ann_dict["filename"] = annotation.filename
            if hasattr(annotation, "index") and annotation.index is not None:
                ann_dict["index"] = annotation.index
            if hasattr(annotation, "snippet") and annotation.snippet:
                ann_dict["snippet"] = annotation.snippet
            if hasattr(annotation, "quote") and annotation.quote:
                ann_dict["quote"] = annotation.quote

            return ann_dict

        # Handle URL citation annotations
        elif is_url_citation(annotation):
            ann_dict = {"type": "url_citation"}

            # Add available attributes
            if hasattr(annotation, "url") and annotation.url:
                ann_dict["url"] = annotation.url
            if hasattr(annotation, "title") and annotation.title:
                ann_dict["title"] = annotation.title
            if hasattr(annotation, "snippet") and annotation.snippet:
                ann_dict["snippet"] = annotation.snippet
            if hasattr(annotation, "start_index") and annotation.start_index is not None:
                ann_dict["start_index"] = annotation.start_index
            if hasattr(annotation, "end_index") and annotation.end_index is not None:
                ann_dict["end_index"] = annotation.end_index

            return ann_dict

        # Handle file path annotations
        elif is_file_path(annotation):
            ann_dict = {"type": "file_path"}

            # Add available attributes
            if hasattr(annotation, "file_id") and annotation.file_id:
                ann_dict["file_id"] = annotation.file_id
            if hasattr(annotation, "index") and annotation.index is not None:
                ann_dict["index"] = annotation.index

            return ann_dict

        # Fallback for unknown annotation types
        else:
            return {
                "type": "unknown_annotation",
                "raw_data": str(annotation),
                "annotation_type": type(annotation).__name__,
            }

    def _json_serializer(self, obj: Any) -> Any:
        """Custom JSON serializer for objects that aren't natively JSON serializable."""
        # Handle pydantic models
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        elif hasattr(obj, "dict"):
            return obj.dict()

        # Handle other objects by converting to string
        return str(obj)

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()

    # Additional methods for compatibility with Display interface
    def render_error(self, error: str) -> None:
        """Render error message as JSON."""
        error_data = {"type": "error", "message": error, "timestamp": self._get_current_timestamp()}

        try:
            json_output = json.dumps(error_data, indent=self._config.indent if self._config.pretty_print else None)
            self._output_stream.write(json_output)
            self._output_stream.write("\n")
            self._output_stream.flush()
        except Exception as e:
            logger.error(f"Failed to render error as JSON: {e}")

    def render_welcome(self, config: "AppConfig") -> None:
        """Render welcome message as JSON."""
        welcome_data = {
            "type": "welcome",
            "message": "Knowledge Forge Chat v3 - JSON Renderer",
            "timestamp": self._get_current_timestamp(),
        }

        # Use hasattr instead of getattr for better type checking
        if hasattr(config, "model") and config.model:
            welcome_data["model"] = config.model

        if hasattr(config, "enabled_tools") and config.enabled_tools:
            welcome_data["enabled_tools"] = config.enabled_tools

        try:
            json_output = json.dumps(welcome_data, indent=self._config.indent if self._config.pretty_print else None)
            self._output_stream.write(json_output)
            self._output_stream.write("\n")
            self._output_stream.flush()
        except Exception as e:
            logger.error(f"Failed to render welcome as JSON: {e}")

    def render_request_info(self, info: dict) -> None:
        """Render request information as JSON."""
        request_data = {"type": "request_info", "timestamp": self._get_current_timestamp(), **info}

        try:
            json_output = json.dumps(request_data, indent=self._config.indent if self._config.pretty_print else None)
            self._output_stream.write(json_output)
            self._output_stream.write("\n")
            self._output_stream.flush()
        except Exception as e:
            logger.error(f"Failed to render request info as JSON: {e}")

    def render_status(self, message: str) -> None:
        """Render status message as JSON."""
        status_data = {"type": "status", "message": message, "timestamp": self._get_current_timestamp()}

        try:
            json_output = json.dumps(status_data, indent=self._config.indent if self._config.pretty_print else None)
            self._output_stream.write(json_output)
            self._output_stream.write("\n")
            self._output_stream.flush()
        except Exception as e:
            logger.error(f"Failed to render status as JSON: {e}")
