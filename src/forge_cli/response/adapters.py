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
        return FileSearchTool(
            file_search={
                "vector_store_ids": vector_store_ids,
                "max_search_results": max_search_results,
            }
        )

    @staticmethod
    def create_web_search_tool() -> WebSearchTool:
        """Create a typed WebSearchTool."""
        return WebSearchTool()

    @staticmethod
    def tools_to_openai_format(tools: list[Union["Tool", dict[str, Any]]]) -> list[dict[str, Any]]:
        """Convert tool list to OpenAI format."""
        openai_tools = []
        for tool in tools:
            openai_tools.append(tool)
        return openai_tools
