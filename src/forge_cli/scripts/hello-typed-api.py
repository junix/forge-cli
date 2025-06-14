#!/usr/bin/env python3
"""
Example demonstrating the new typed API for Knowledge Forge.

This script shows how to use the typed request/response system
with full type safety and IDE support.
"""

import asyncio
from forge_cli.sdk import (
    async_create_typed_response,
    astream_typed_response,
    create_typed_request,
    create_file_search_tool,
    create_web_search_tool,
)
from forge_cli.response._types import (
    Request,
    Response,
    ResponseTextDeltaEvent,
    ResponseFileSearchCallCompletedEvent,
    ResponseWebSearchCallCompletedEvent,
)


async def example_basic_typed_request():
    """Basic example using typed request and response."""
    print("\n=== Basic Typed Request Example ===\n")

    # Create a typed request
    request = create_typed_request(
        input_messages="What are the key principles of machine learning?",
        model="qwen-max-latest",
        temperature=0.7,
        max_output_tokens=500,
    )

    # Get typed response
    response = await async_create_typed_response(request)

    # Type-safe access to response fields
    print(f"Response ID: {response.id}")
    print(f"Model: {response.model}")

    # Extract message content
    for item in response.output or []:
        if item.type == "message" and hasattr(item, "content"):
            for content in item.content:
                if hasattr(content, "text"):
                    print(f"\nResponse: {content.text}")

    # Usage statistics
    if response.usage:
        print(f"\nTokens used: {response.usage.total_tokens}")


async def example_streaming_with_types():
    """Example using typed streaming API."""
    print("\n=== Streaming with Typed Events Example ===\n")

    # Create request with tools
    file_search = create_file_search_tool(vector_store_ids=["vs_example"], max_search_results=5)

    web_search = create_web_search_tool()

    request = create_typed_request(
        input_messages="Tell me about recent developments in AI",
        model="qwen-max-latest",
        tools=[file_search, web_search],
        effort="medium",
    )

    # Stream with typed events
    print("Streaming response...")
    async for event_type, event in astream_typed_response(request):
        # Type-safe event handling
        if isinstance(event, ResponseTextDeltaEvent):
            print(event.text, end="", flush=True)

        elif isinstance(event, ResponseFileSearchCallCompletedEvent):
            print(f"\n\n[File search completed with {len(event.results or [])} results]")

        elif isinstance(event, ResponseWebSearchCallCompletedEvent):
            print(f"\n\n[Web search completed with {len(event.results or [])} results]")

        elif event_type == "done":
            print("\n\n[Stream complete]")
            break


async def example_complex_request():
    """Example with complex typed request including multiple messages."""
    print("\n=== Complex Typed Request Example ===\n")

    # Create a request with conversation history
    request = Request(
        input=[
            {"role": "user", "content": "What is Python?"},
            {"role": "assistant", "content": "Python is a high-level programming language..."},
            {"role": "user", "content": "What are its main use cases?"},
        ],
        model="qwen-max-latest",
        system="You are a helpful programming assistant.",
        temperature=0.5,
        effort="high",
    )

    # Convert to OpenAI format for inspection
    openai_format = request.as_openai_chat_request()
    print("Request will be sent as:")
    print(f"  Model: {openai_format['model']}")
    print(f"  Messages: {len(openai_format['messages'])} messages")
    print(f"  Temperature: {openai_format['temperature']}")

    # Stream the response
    async for event_type, event in astream_typed_response(request):
        if isinstance(event, ResponseTextDeltaEvent):
            print(event.text, end="", flush=True)
        elif event_type == "done":
            break


async def example_type_safety():
    """Demonstrate type safety benefits."""
    print("\n=== Type Safety Example ===\n")

    # This would be caught by type checker:
    # request = create_typed_request(
    #     input_messages=123,  # Type error: expected str or list
    #     model=True,          # Type error: expected str
    # )

    # Correct usage with IDE support
    request = create_typed_request(
        input_messages="Explain type safety in programming",
        model="qwen-max-latest",
    )

    # The request object has full IDE support
    print(f"Request model: {request.model}")
    print(f"Request has {len(request.tools or [])} tools")

    # Type-safe tool creation
    file_tool = create_file_search_tool(
        vector_store_ids=["vs_123", "vs_456"],
        max_search_results=10,  # IDE knows this should be an int
    )

    # Add tool to request
    request.tools = [file_tool]

    print(f"Added file search tool with {len(file_tool.file_search.vector_store_ids)} vector stores")


async def main():
    """Run all examples."""
    print("Knowledge Forge Typed API Examples")
    print("=================================")

    # Run examples
    await example_basic_typed_request()
    await example_streaming_with_types()
    await example_complex_request()
    await example_type_safety()

    print("\n\nAll examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
