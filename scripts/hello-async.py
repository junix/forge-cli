#!/usr/bin/env python3
"""
Async hello example that demonstrates using the sdk.py client library
to send requests to the Knowledge Forge API.
"""

import asyncio
import os
from typing import Any

# Import sdk functions
from sdk import (
    astream_response,
    async_create_response,
    async_fetch_response,
    validate_input_messages,
)


async def hello_async():
    """Send a simple hello request and then fetch it by ID."""
    print("=== Knowledge Forge API Async Hello Example ===")

    # Create the initial message
    user_message = "你好，Knowledge Forge!"

    # Create a validated message object
    messages = validate_input_messages(user_message)

    print(f"Sending message: '{user_message}'")

    try:
        # Method 1: Using async_create_response (regular async response)
        print("\n=== Method 1: Using async_create_response ===")
        response = await async_create_response(input_messages=messages, model="qwen-max", effort="low", store=True)

        if response:
            print("\nResponse received:")
            print_response_summary(response)

            # Fetch the response by ID to verify
            response_id = response.get("id")
            if response_id:
                print(f"\nFetching response with ID: {response_id}")
                fetched_response = await async_fetch_response(response_id)

                if fetched_response:
                    print("\nFetched response by ID:")
                    print_response_summary(fetched_response)
                else:
                    print("Failed to fetch response by ID")
        else:
            print("No response received")

        # Method 2: Using astream_response (streaming response)
        print("\n=== Method 2: Using astream_response (streaming) ===")
        print(f"Sending streaming message: '{user_message}'")

        # Variables to collect stream data
        complete_text = ""
        event_count = 0
        stream_result = None

        # Process the streaming response
        async for event_type, event_data in astream_response(
            input_messages=messages,
            model="qwen-max",
            effort="low",
        ):
            event_count += 1

            # Print event type (only for first 3 events and last event to avoid spam)
            if event_count <= 3 or event_type == "done":
                print(f"Event {event_count}: {event_type}")
            elif event_count % 10 == 0:  # Print a dot for every 10 events
                print(".", end="", flush=True)

            # Handle text deltas
            if event_type == "response.output_text.delta" and event_data and "text" in event_data:
                # Handle various text content formats
                text_content = event_data["text"]
                if isinstance(text_content, dict) and "text" in text_content:
                    complete_text += text_content["text"]
                elif isinstance(text_content, str):
                    complete_text += text_content

            # Save final response when completed
            if event_type == "final_response":
                stream_result = event_data

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
            response_id = stream_result.get("id")
            if response_id:
                print(f"\nFetching streamed response with ID: {response_id}")
                fetched_response = await async_fetch_response(response_id)

                if fetched_response:
                    print("\nFetched streamed response by ID:")
                    print_response_summary(fetched_response)
                else:
                    print("Failed to fetch streamed response by ID")

    except Exception as e:
        print(f"Error: {e}")


def print_response_summary(response: dict[str, Any]):
    """Print a summary of a response object."""
    print(f"Response ID: {response.get('id')}")
    print(f"Model: {response.get('model')}")
    print(f"Created at: {response.get('created_at')}")

    # Extract and print text content
    text_content = extract_text_from_response(response)
    if text_content:
        print(f"Content: '{text_content}'")
    else:
        print("No text content found in response")


def extract_text_from_response(response: dict[str, Any]) -> str | None:
    """Extract text content from a response object."""
    try:
        # First, look for output messages
        for output_item in response.get("output", []):
            if output_item.get("type") == "message":
                for content_item in output_item.get("content", []):
                    if content_item.get("type") == "output_text":
                        return content_item.get("text", "")

        # If not found in output messages, try the first output text
        for item in response.get("output", []):
            if isinstance(item, dict) and item.get("role") == "assistant":
                content = item.get("content", "")
                if isinstance(content, str):
                    return content
                elif isinstance(content, list):
                    for part in content:
                        if part.get("type") == "text":
                            return part.get("text", "")

        return None
    except Exception as e:
        print(f"Error extracting text from response: {e}")
        return None


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
