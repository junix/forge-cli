#!/usr/bin/env python3
"""
Async hello example that demonstrates using the typed API
to send requests to the Knowledge Forge API.

This example shows the migration from dict-based to typed Response API.
"""

import asyncio
import os
from typing import Optional, Union, Any

# Import typed SDK functions and types
from sdk import (
    astream_typed_response,
    async_create_typed_response,
    async_fetch_response,
    create_typed_request,
)
from forge_cli.response._types import Response
from forge_cli.response.adapters import MigrationHelper


async def hello_async():
    """Send a simple hello request and then fetch it by ID."""
    print("=== Knowledge Forge API Typed Hello Example ===")

    # Create the initial message
    user_message = "你好，Knowledge Forge!"

    # Create a typed request object
    request = create_typed_request(input_messages=user_message, model="qwen-max-latest", effort="low", store=True)

    print(f"Sending message: '{user_message}'")

    try:
        # Method 1: Using async_create_typed_response (regular async response)
        print("\n=== Method 1: Using async_create_typed_response ===")
        response = await async_create_typed_response(request)

        if response:
            print("\nResponse received:")
            print_response_summary(response)

            # Fetch the response by ID to verify
            if response.id:
                print(f"\nFetching response with ID: {response.id}")
                fetched_response = await async_fetch_response(response.id)

                if fetched_response:
                    print("\nFetched response by ID:")
                    print_response_summary(fetched_response)
                else:
                    print("Failed to fetch response by ID")
        else:
            print("No response received")

        # Method 2: Using astream_typed_response (streaming response)
        print("\n=== Method 2: Using astream_typed_response (streaming) ===")
        print(f"Sending streaming message: '{user_message}'")

        # Variables to collect stream data
        complete_text = ""
        event_count = 0
        stream_result: Optional[Response] = None

        # Process the streaming response with typed API
        async for event_type, response in astream_typed_response(request):
            event_count += 1

            # Print event type (only for first 3 events and last event to avoid spam)
            if event_count <= 3 or event_type == "done":
                print(f"Event {event_count}: {event_type}")
            elif event_count % 10 == 0:  # Print a dot for every 10 events
                print(".", end="", flush=True)

            # Handle text deltas using typed Response
            if event_type == "response.output_text.delta" and response:
                # Use Response's output_text property for clean access
                if response.output_text:
                    current_text = response.output_text
                    # Accumulate only the new text (assuming snapshot-based)
                    if len(current_text) > len(complete_text):
                        complete_text = current_text

            # Save final response when completed
            if event_type == "response.completed" and response:
                stream_result = response

            # Exit on done event
            if event_type == "done":
                print("\nStreaming completed")
                break

        # Print streaming results summary
        print(f"\nReceived {event_count} streaming events")
        print(f"Final text: '{complete_text}'")

        if stream_result:
            print("\nFinal stream response:")
            print_response_summary(stream_result)

            # Fetch the response by ID to verify
            if stream_result.id:
                print(f"\nFetching streamed response with ID: {stream_result.id}")
                fetched_response = await async_fetch_response(stream_result.id)

                if fetched_response:
                    print("\nFetched streamed response by ID:")
                    print_response_summary(fetched_response)
                else:
                    print("Failed to fetch streamed response by ID")

    except Exception as e:
        print(f"Error: {e}")


def print_response_summary(response: Union[Response, dict[str, Any]]):
    """Print a summary of a response object (supports both typed and dict)."""
    # Handle typed Response
    if isinstance(response, Response):
        print(f"Response ID: {response.id}")
        print(f"Model: {response.model}")
        print(f"Created at: {response.created_at}")

        # Use Response's output_text property
        text_content = response.output_text
        if text_content:
            print(f"Content: '{text_content}'")
        else:
            print("No text content found in response")

        # Show token usage if available
        if response.usage:
            print(f"Tokens used: {response.usage.total_tokens}")

    # Handle dict response (backward compatibility)
    elif isinstance(response, dict):
        print(f"Response ID: {response.get('id')}")
        print(f"Model: {response.get('model')}")
        print(f"Created at: {response.get('created_at')}")

        # Use migration helper for safe text extraction
        text_content = MigrationHelper.safe_get_text(response)
        if text_content:
            print(f"Content: '{text_content}'")
        else:
            print("No text content found in response")

        # Show token usage if available
        usage = MigrationHelper.safe_get_usage(response)
        if usage:
            print(f"Tokens used: {usage.get('total_tokens', 0)}")


if __name__ == "__main__":
    # Set OpenAI API key if needed
    if not os.environ.get("OPENAI_API_KEY"):
        try:
            with open(os.path.expanduser("~/.openai-api-key")) as f:
                os.environ["OPENAI_API_KEY"] = f.read().strip()
            print("Loaded OpenAI API key from ~/.openai-api-key")
        except Exception:
            print("Warning: No OPENAI_API_KEY found in environment or ~/.openai-api-key")

    # Run the async example
    asyncio.run(hello_async())
