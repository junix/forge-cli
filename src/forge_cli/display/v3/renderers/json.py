"""JSON renderer for v3 display - outputs Response snapshots as formatted JSON with rich live updates."""

import json
import sys
from typing import Any, Optional, TextIO

from pydantic import BaseModel, Field, validator
from rich.console import Console
from rich.live import Live
from rich.syntax import Syntax
from rich.panel import Panel

from forge_cli.response._types.response import Response

from ..base import BaseRenderer


class JsonDisplayConfig(BaseModel):
    """Configuration for JSON renderer output options."""

    pretty_print: bool = Field(True, description="Whether to format JSON with indentation")
    indent: int = Field(2, description="Number of spaces for JSON indentation")
    include_metadata: bool = Field(False, description="Whether to include response metadata")
    include_usage: bool = Field(True, description="Whether to include token usage statistics")
    include_timing: bool = Field(False, description="Whether to include timing information")
    output_file: Optional[str] = Field(None, description="File path to write JSON output (None for stdout)")
    append_mode: bool = Field(False, description="Whether to append to output file or overwrite")
    show_panel: bool = Field(True, description="Whether to show JSON in a panel with title")
    panel_title: str = Field("JSON Response", description="Title for the panel")
    syntax_theme: str = Field("monokai", description="Syntax highlighting theme")
    line_numbers: bool = Field(True, description="Whether to show line numbers")

    @validator("indent")
    def validate_indent(cls, v):
        if v < 0 or v > 8:
            raise ValueError("Indent must be between 0 and 8")
        return v


class JsonRenderer(BaseRenderer):
    """JSON renderer for v3 display system.

    Renders complete Response snapshots as formatted JSON output using Rich live updates.
    Follows the v3 design principle of one simple render_response() method.
    """

    def __init__(self, config: JsonDisplayConfig | None = None, output_stream: Optional[TextIO] = None):
        """Initialize JSON renderer.

        Args:
            config: Display configuration
            output_stream: Output stream (defaults to stdout)
        """
        super().__init__()
        self._config = config or JsonDisplayConfig()
        self._output_stream = output_stream or sys.stdout
        self._file_handle: Optional[TextIO] = None
        self._response_count = 0

        # Rich components
        self._console = Console(file=self._output_stream)
        self._live: Optional[Live] = None
        self._current_json = ""

        # Open output file if specified
        if self._config.output_file:
            try:
                mode = "a" if self._config.append_mode else "w"
                self._file_handle = open(self._config.output_file, mode, encoding="utf-8")
                self._console = Console(file=self._file_handle)
            except Exception as e:
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
                "created_at": getattr(response, "created_at", None),
                "completed_at": getattr(response, "completed_at", None),
            }

        return result

    def _serialize_output_item(self, item: Any) -> dict[str, Any]:
        """Serialize an output item to dictionary format."""
        if not hasattr(item, "type"):
            return {"raw_data": str(item)}

        item_dict = {"type": item.type}

        # Handle different item types
        if item.type == "message":
            if hasattr(item, "content") and item.content:
                item_dict["content"] = []
                for content in item.content:
                    content_dict = self._serialize_content_item(content)
                    item_dict["content"].append(content_dict)

        elif hasattr(item, "status"):
            # Tool-related items
            item_dict["status"] = item.status

            if hasattr(item, "queries") and item.queries:
                item_dict["queries"] = item.queries

            if hasattr(item, "results") and item.results:
                item_dict["results"] = item.results

        elif item.type == "reasoning":
            if hasattr(item, "summary") and item.summary:
                item_dict["summary"] = []
                for summary in item.summary:
                    if hasattr(summary, "text"):
                        item_dict["summary"].append({"text": summary.text})

        # Add any other attributes that might be useful
        for attr in ["role", "status", "queries", "results", "summary"]:
            if hasattr(item, attr) and attr not in item_dict:
                value = getattr(item, attr)
                if value is not None:
                    item_dict[attr] = value

        return item_dict

    def _serialize_content_item(self, content: Any) -> dict[str, Any]:
        """Serialize a content item to dictionary format."""
        if not hasattr(content, "type"):
            return {"raw_data": str(content)}

        content_dict = {"type": content.type}

        if content.type == "output_text":
            content_dict["text"] = getattr(content, "text", "")

            # Add annotations if present
            if hasattr(content, "annotations") and content.annotations:
                content_dict["annotations"] = []
                for annotation in content.annotations:
                    ann_dict = self._serialize_annotation(annotation)
                    content_dict["annotations"].append(ann_dict)

        elif content.type == "output_refusal":
            content_dict["refusal"] = getattr(content, "refusal", "")

        return content_dict

    def _serialize_annotation(self, annotation: Any) -> dict[str, Any]:
        """Serialize an annotation to dictionary format."""
        if not hasattr(annotation, "type"):
            return {"raw_data": str(annotation)}

        ann_dict = {"type": annotation.type}

        # Handle different annotation types
        if annotation.type == "file_citation":
            for attr in ["file_id", "file_name", "page_number", "text"]:
                if hasattr(annotation, attr):
                    value = getattr(annotation, attr)
                    if value is not None:
                        ann_dict[attr] = value

        elif annotation.type == "url_citation":
            for attr in ["url", "text"]:
                if hasattr(annotation, attr):
                    value = getattr(annotation, attr)
                    if value is not None:
                        ann_dict[attr] = value

        return ann_dict

    def _json_serializer(self, obj: Any) -> Any:
        """Custom JSON serializer for objects that aren't natively JSON serializable."""
        # Handle pydantic models
        if hasattr(obj, "dict"):
            return obj.dict()

        # Handle other objects by converting to string
        return str(obj)

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime

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

    def render_welcome(self, config: Any) -> None:
        """Render welcome message as JSON."""
        welcome_data = {
            "type": "welcome",
            "message": "Knowledge Forge Chat v3 - JSON Renderer",
            "timestamp": self._get_current_timestamp(),
        }

        if hasattr(config, "model"):
            welcome_data["model"] = config.model

        if hasattr(config, "enabled_tools"):
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
