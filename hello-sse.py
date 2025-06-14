#!/usr/bin/env python3
import argparse
import json
import logging
import os

import requests
from rich.align import Align
from rich.console import Console

# Set up a simple logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Use environment variable for server URL if available, otherwise default to localhost
BASE_URL = os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999")

# Add this mapping at the top of your script
EVENT_TYPE_MAP = {
    "EventType.RESPONSE_CREATED": "response.created",
    "EventType.RESPONSE_IN_PROGRESS": "response.in_progress",
    "EventType.RESPONSE_OUTPUT_ITEM_ADDED": "response.output_item.added",
    "EventType.RESPONSE_OUTPUT_TEXT_DELTA": "response.output_text.delta",
    "EventType.RESPONSE_OUTPUT_TEXT_DONE": "response.output_text.done",
    "EventType.RESPONSE_COMPLETED": "response.completed",
    # Add more as needed
}

console = Console()


def process_event_type(line):
    """Process the event type from an SSE line.

    Args:
        line (str): The SSE line starting with 'event:'

    Returns:
        str: The event type
        bool: True if the event is 'done', False otherwise
    """
    raw_event_type = line[6:].strip()
    event_type = EVENT_TYPE_MAP.get(raw_event_type, raw_event_type)
    console.print(Align.center(f"Event type: {event_type}"), style="red")

    # If we get the 'done' event, signal to stop processing
    if event_type == "response.output_text.done" or event_type == "done":
        console.print(Align.center("SSE stream completed."), style="red")
        return event_type, True

    return event_type, False


def parse_event_data(data_str, event_type, event_index):
    """Parse the JSON data from an SSE event.

    Args:
        data_str (str): The data string from the SSE event
        event_type (str): The type of the event
        event_index (int): The current event index

    Returns:
        dict: The parsed JSON data
        int: The incremented event index
    """
    try:
        data = json.loads(data_str)
        # Print event separator with event index
        console.print(
            Align.center(f"\n======== Event [{event_index}] - {event_type} ========="),
            style="red",
        )
        console.print(
            Align.center(json.dumps(data, ensure_ascii=False, indent=2)),
            style="blue",
        )
        return data, event_index + 1
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing SSE data: {e}")
        logger.error(f"Raw data: {data_str}")
        return None, event_index


def process_response_created(data):
    """Process a response.created event.

    Args:
        data (dict): The parsed JSON data from the response.created event
    """
    response_id = data.get("id")
    created_at = data.get("created_at")
    console.print(Align.center(f"Response created - ID: {response_id}"), style="yellow")
    console.print(Align.center(f"Created at: {created_at}"), style="yellow")


def process_response_in_progress(data):
    """Process a response.in_progress event.

    Args:
        data (dict): The parsed JSON data from the response.in_progress event
    """
    response_id = data.get("id")
    console.print(Align.center(f"Processing response - ID: {response_id}"), style="yellow")


def process_output_item_added(data):
    """Process a response.output_item.added event.

    Args:
        data (dict): The parsed JSON data containing the output item
    """
    message = data.get("message", {})
    role = message.get("role", "unknown")

    # Extract text content if available
    content_items = message.get("content", [])
    for item in content_items:
        if item.get("type") == "output_text":
            text = item.get("text", "")
            console.print(Align.center(f"[{role}]: {text}"), style="cyan")


def process_output_text_delta(data):
    """Process a response.output_text.delta event.

    Args:
        data (dict): The parsed JSON data containing the text delta
    """
    delta = data.get("delta", "")
    if delta:
        console.print(delta, end="", style="cyan")


def process_response_completed(data):
    """Process a response.completed event.

    Args:
        data (dict): The parsed JSON data containing the completion response

    Returns:
        str: The response ID
        dict: The final response data
    """
    response_id = data.get("id")
    console.print(Align.center(f"Response completed - ID: {response_id}"), style="green")
    console.print(Align.center(f"Model used: {data.get('model')}"), style="green")

    # Extract and print the actual text content if available
    for output_item in data.get("output", []):
        if output_item.get("type") == "message":
            for content_item in output_item.get("content", []):
                if content_item.get("type") == "output_text":
                    console.print(
                        Align.center(f"\nResponse text: {content_item.get('text', '')}"),
                        style="green",
                    )

    return response_id, data


def handle_sse_stream(response):
    """Handle the Server-Sent Events (SSE) stream.

    Args:
        response (Response): The requests response object with stream=True

    Returns:
        dict: The final response data
        str: The response ID
    """
    final_response = None
    response_id = None
    event_index = 0
    current_event_type = None

    console.print(Align.center("[bold]SSE stream started. Receiving events:[/bold]"))

    for line in response.iter_lines():
        if not line:
            continue

        line = line.decode("utf-8")
        # logger.debug(f"Raw SSE line: {line}")

        if line.startswith("event:"):
            event_type, is_done = process_event_type(line)
            current_event_type = event_type
            continue

        # Skip non-data lines
        if not line.startswith("data:"):
            continue

        data_str = line[5:].strip()
        if not data_str:
            continue

        # Only try to parse as JSON if it looks like a JSON object
        if data_str.startswith("{") or data_str.startswith("["):
            data, event_index = parse_event_data(data_str, current_event_type, event_index)
            if not data:
                continue

            # Process the event based on its raw string value
            if current_event_type == "response.created":
                process_response_created(data)
            elif current_event_type == "response.in_progress":
                process_response_in_progress(data)
            elif current_event_type == "response.output_item.added":
                process_output_item_added(data)
            elif current_event_type == "response.output_text.delta":
                process_output_text_delta(data)
            elif current_event_type == "response.completed":
                response_id, final_response = process_response_completed(data)
            else:
                # For any other event type, just log the raw string value
                console.print(
                    Align.center(f"Received event of type: {current_event_type}"),
                    style="yellow",
                )
        else:
            # For non-JSON data lines, just log them without trying to parse
            logger.debug(f"Non-JSON data for event type '{current_event_type}': {data_str}")

        if is_done:
            break

    console.print(Align.center("\n======== SSE stream finished ========="), style="red")
    return final_response, response_id


def handle_request_error(e):
    """Handle request exceptions.

    Args:
        e (RequestException): The exception that occurred

    Returns:
        None
    """
    logger.error(f"Error sending request: {e}")
    if hasattr(e, "response") and e.response is not None:
        try:
            error_data = e.response.json()
            logger.error(f"Server error details: {json.dumps(error_data, indent=2)}")
        except json.JSONDecodeError:
            logger.error(f"Server error response (non-JSON): {e.response.text[:500]}")
    return None


def send_hello_request(query=None, effort="low"):
    """Send a simple 'hello' request to the Knowledge Forge API using SSE."""

    # Create a request that matches the OpenAI format
    request_json = {
        "model": "qwen3-235b-a22b",  # Using a valid OpenAI model
        "effort": effort,  # Move effort to top level
        "store": True,
        "input": [{"role": "user", "content": query or "你好，Knowledge Forge!"}],
    }

    try:
        # Send the request to the API
        url = f"{BASE_URL}/v1/responses"
        console.print(Align.center(f"Sending request to: {url}"))
        console.print(Align.center(f"Request data: {json.dumps(request_json, ensure_ascii=False, indent=2)}"))

        # Use stream=True for SSE
        response = requests.post(url, json=request_json, stream=True)
        response.raise_for_status()

        # Process the SSE stream
        final_response, response_id = handle_sse_stream(response)

        # If we have a response ID, try to fetch it again using the API
        # if response_id:
        #     fetch_response_by_id(response_id)

        return final_response

    except requests.exceptions.RequestException as e:
        return handle_request_error(e)


def fetch_response_by_id(response_id):
    """Fetch a response by its ID using the Knowledge Forge API."""
    try:
        # Construct the URL to get the response by ID
        url = f"{BASE_URL}/v1/responses/{response_id}"
        print(f"\nFetching response by ID from: {url}")

        # Send GET request to retrieve the response
        response = requests.get(url)
        response.raise_for_status()

        # Parse and display the fetched response
        fetched_response = response.json()
        print("\nFetched response by ID:")
        print(json.dumps(fetched_response, ensure_ascii=False, indent=2))

        # Verify if the fetched response matches the original
        print(f"\nVerified response ID: {fetched_response.get('id')}")

        return fetched_response

    except requests.exceptions.RequestException as e:
        print(f"Error fetching response by ID: {e}")
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"Server error details: {json.dumps(error_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Server error response (non-JSON): {e.response.text[:500]}")
        return None


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Send a query to Knowledge Forge API")
    parser.add_argument("--query", "-q", type=str, help="Query to send to the API")
    parser.add_argument(
        "--effort",
        "-e",
        type=str,
        choices=["low", "medium", "high", "dev"],
        default="low",
        help="Effort level for the request (default: low)",
    )
    args = parser.parse_args()

    send_hello_request(args.query, args.effort)
