"""Adapters for migrating from dict-based API to typed response system."""

from typing import Any, Union

from forge_cli.response._types import (
    FileSearchTool,
    InputMessage,
    Request,
    Response,
    ResponseStreamEvent,
    WebSearchTool,
)


class ResponseAdapter:
    """Adapter for converting between dict-based API and typed Response objects."""

    @staticmethod
    def from_dict(response_dict: dict[str, Any]) -> Response:
        """Convert API response dict to typed Response object."""
        return Response(**response_dict)

    @staticmethod
    def to_dict(response: Response) -> dict[str, Any]:
        """Convert typed Response to dict for backward compatibility."""
        return response.model_dump(by_alias=True, exclude_none=True)

    @staticmethod
    def create_request(
        input_messages: str | list[dict[str, Any]] | list[InputMessage],
        model: str = "qwen-max-latest",
        tools: list[Union[dict[str, Any], "Tool"]] | None = None,
        **kwargs,
    ) -> Request:
        """Create a typed Request object from various input formats."""
        # Convert string to message list
        if isinstance(input_messages, str):
            input_messages = [{"role": "user", "content": input_messages}]

        # Use Request's built-in conversion methods
        request = Request(input=input_messages, model=model, tools=tools or [], **kwargs)

        return request

    @staticmethod
    def request_to_openai_format(request: Request) -> dict[str, Any]:
        """Convert Request to OpenAI-compatible format."""
        return request.as_openai_chat_request()


class StreamEventAdapter:
    """Adapter for processing stream events with typed objects."""

    @staticmethod
    def parse_event(event_data: dict[str, Any]) -> ResponseStreamEvent:
        """Parse raw event data into typed event object."""
        event_type = event_data.get("type", "")

        # Map event types to specific event classes
        event_map = {
            "response.created": "ResponseCreatedEvent",
            "response.completed": "ResponseCompletedEvent",
            "response.output_text.delta": "ResponseTextDeltaEvent",
            "response.file_search_call.searching": "ResponseFileSearchCallSearchingEvent",
            "response.file_search_call.completed": "ResponseFileSearchCallCompletedEvent",
            "response.web_search_call.searching": "ResponseWebSearchCallSearchingEvent",
            "response.web_search_call.completed": "ResponseWebSearchCallCompletedEvent",
        }

        # Import the specific event class dynamically
        if event_type in event_map:
            from forge_cli.response import _types

            event_class = getattr(_types, event_map[event_type])
            return event_class(**event_data)

        # Fallback to generic event
        return ResponseStreamEvent(**event_data)


class ToolAdapter:
    """Adapter for converting between dict and typed tool definitions."""

    @staticmethod
    def create_file_search_tool(vector_store_ids: list[str], max_search_results: int = 20) -> FileSearchTool:
        """Create a typed FileSearchTool."""
        return FileSearchTool(type="file_search", vector_store_ids=vector_store_ids, max_num_results=max_search_results)

    @staticmethod
    def create_web_search_tool() -> WebSearchTool:
        """Create a typed WebSearchTool."""
        return WebSearchTool(type="web_search")

    @staticmethod
    def tools_to_openai_format(tools: list[Union["Tool", dict[str, Any]]]) -> list[dict[str, Any]]:
        """Convert tool list to OpenAI format."""
        openai_tools = []
        for tool in tools:
            if hasattr(tool, "model_dump"):
                # Typed tool
                openai_tools.append(tool.model_dump(by_alias=True, exclude_none=True))
            else:
                # Dict tool
                openai_tools.append(tool)
        return openai_tools


class MigrationHelper:
    """Helper utilities for migrating from dict-based to typed API."""

    @staticmethod
    def is_typed_response(event_data: Any) -> bool:
        """Check if event_data is a typed Response or dict."""
        return event_data is not None and hasattr(event_data, "id") and hasattr(event_data, "output")

    @staticmethod
    def safe_get_text(event_data: Any) -> str:
        """Extract text from either dict or Response."""
        if event_data is None:
            return ""

        # Typed Response - but output_text property might fail with dict items
        if MigrationHelper.is_typed_response(event_data):
            try:
                return event_data.output_text or ""
            except (AttributeError, TypeError):
                # Fall back to manual extraction if output items aren't properly typed
                pass

        # Dict format
        if isinstance(event_data, dict):
            # Try direct text access
            if "text" in event_data:
                text_data = event_data["text"]
                if isinstance(text_data, str):
                    return text_data
                elif isinstance(text_data, dict) and "text" in text_data:
                    return text_data["text"]

            # Try output access for completed responses
            output = event_data.get("output", [])
            for item in output:
                if isinstance(item, dict) and item.get("type") == "message":
                    content = item.get("content", [])
                    for content_item in content:
                        if isinstance(content_item, dict) and content_item.get("type") == "output_text":
                            return content_item.get("text", "")

        return ""

    @staticmethod
    def safe_get_status(event_data: Any) -> str | None:
        """Extract status from either dict or Response."""
        if event_data is None:
            return None

        if hasattr(event_data, "status"):
            return event_data.status
        elif isinstance(event_data, dict):
            return event_data.get("status")

        return None

    @staticmethod
    def safe_get_usage(event_data: Any) -> dict[str, int] | None:
        """Extract usage info from either dict or Response."""
        if event_data is None:
            return None

        if hasattr(event_data, "usage") and event_data.usage:
            # Typed Response
            usage = event_data.usage
            return {
                "total_tokens": usage.total_tokens,
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
            }
        elif isinstance(event_data, dict):
            return event_data.get("usage")

        return None

    @staticmethod
    def safe_get_tool_calls(event_data: Any) -> list[Any]:
        """Extract tool calls from either dict or Response."""
        if event_data is None:
            return []

        tool_calls = []

        if hasattr(event_data, "output"):
            # Typed Response
            for item in event_data.output:
                if hasattr(item, "type") and "tool_call" in str(item.type):
                    tool_calls.append(item)
        elif isinstance(event_data, dict):
            # Dict format
            output = event_data.get("output", [])
            for item in output:
                if isinstance(item, dict) and "tool_call" in item.get("type", ""):
                    tool_calls.append(item)

        return tool_calls

    @staticmethod
    def is_typed_item(item: Any) -> bool:
        """Check if an item is a typed object (not dict)."""
        return hasattr(item, "type") and not isinstance(item, dict)

    @staticmethod
    def safe_get_output_items(data: Any) -> list:
        """Safely extract output items from response data."""
        if MigrationHelper.is_typed_response(data):
            try:
                return list(data.output) if hasattr(data, "output") else []
            except (AttributeError, TypeError):
                return []
        elif isinstance(data, dict):
            return data.get("output", [])
        return []
