"""Example of SDK integration with new type system.

This demonstrates how to gradually adopt the new response types
in the SDK while maintaining backward compatibility.
"""

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from forge_cli.response._types import (
    Request,
    Response,
    ResponseStreamEvent,
)
from forge_cli.response.adapters import (
    ResponseAdapter,
    StreamEventAdapter,
    ToolAdapter,
)


class TypedForgeSDK:
    """Enhanced SDK using the new type system."""

    def __init__(self, base_url: str = "http://localhost:9999"):
        self.base_url = base_url
        # Placeholder for actual HTTP client
        self.session = None

    async def create_response(self, request: Request, stream: bool = False) -> Response:
        """Create a response using typed Request object."""
        # Convert to OpenAI format for API call
        api_payload = request.as_openai_chat_request()

        # Make API call (placeholder)
        # response_data = await self._api_call("/v1/chat/completions", api_payload)
        response_data = {
            "id": "resp_123",
            "object": "chat.completion",
            "created": 1234567890,
            "model": request.model,
            "choices": [{"message": {"role": "assistant", "content": "This is a test response"}}],
        }

        # Convert to typed Response
        return ResponseAdapter.from_dict(response_data)

    async def stream_response(self, request: Request) -> AsyncIterator[tuple[str, ResponseStreamEvent]]:
        """Stream response with typed events."""
        # Convert request
        api_payload = request.as_openai_chat_request()
        api_payload["stream"] = True

        # Simulate streaming (in real implementation, this would be SSE)
        mock_events = [
            {"type": "response.created", "response": {"id": "resp_123"}},
            {"type": "response.output_text.delta", "text": "Hello "},
            {"type": "response.output_text.delta", "text": "world!"},
            {"type": "response.completed", "response": {"id": "resp_123"}},
        ]

        for event_data in mock_events:
            event = StreamEventAdapter.parse_event(event_data)
            yield (event_data["type"], event)
            await asyncio.sleep(0.1)  # Simulate network delay


# Example usage functions


async def example_basic_usage():
    """Basic usage with typed request."""
    sdk = TypedForgeSDK()

    # Create a typed request
    request = ResponseAdapter.create_request(
        input_messages="What is the capital of France?",
        model="qwen-max-latest",
        temperature=0.7,
    )

    # Get response
    response = await sdk.create_response(request)
    print(f"Response: {response}")


async def example_with_tools():
    """Example using typed tools."""
    sdk = TypedForgeSDK()

    # Create typed tools
    file_search = ToolAdapter.create_file_search_tool(vector_store_ids=["vs_123", "vs_456"], max_search_results=10)
    web_search = ToolAdapter.create_web_search_tool()

    # Create request with tools
    request = ResponseAdapter.create_request(
        input_messages="Find information about climate change",
        model="qwen-max-latest",
        tools=[file_search, web_search],
    )

    # Stream response
    async for event_type, event in sdk.stream_response(request):
        print(f"Event: {event_type}")
        # Type-safe access to event properties
        if hasattr(event, "text"):
            print(f"Text: {event.text}")


async def example_migration_path():
    """Show gradual migration from dict to typed API."""
    sdk = TypedForgeSDK()

    # Old style (dict-based)
    old_messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
        {"role": "user", "content": "How are you?"},
    ]

    # Convert to typed request
    request = ResponseAdapter.create_request(
        input_messages=old_messages,
        model="qwen-max-latest",
    )

    # Process with typed API
    response = await sdk.create_response(request)

    # Convert back to dict if needed for compatibility
    response_dict = ResponseAdapter.to_dict(response)
    print(f"Compatible dict: {response_dict}")


# Backward compatibility wrapper
class BackwardCompatibleSDK(TypedForgeSDK):
    """SDK that accepts both dict and typed inputs."""

    async def create_response_compat(
        self, input_messages: Any, model: str = "qwen-max-latest", **kwargs
    ) -> dict[str, Any]:
        """Backward compatible method accepting dict inputs."""
        # Create typed request
        request = ResponseAdapter.create_request(input_messages=input_messages, model=model, **kwargs)

        # Get typed response
        response = await self.create_response(request)

        # Return as dict for compatibility
        return ResponseAdapter.to_dict(response)


if __name__ == "__main__":
    # Run examples
    asyncio.run(example_basic_usage())
    asyncio.run(example_with_tools())
    asyncio.run(example_migration_path())
