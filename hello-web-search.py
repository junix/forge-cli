#!/usr/bin/env python3
import argparse
import json
import os

import requests
from loguru import logger
from rich.align import Align
from rich.console import Console

# Remove default logger and use loguru

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


def handle_sse_stream(response, debug=False):
    """Handle the Server-Sent Events (SSE) stream.

    Args:
        response (Response): The requests response object with stream=True
        debug (bool): Whether to show debug information

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

        # Debug output for raw SSE lines
        if debug:
            logger.debug(f"Raw SSE line: {line}")

        # Handle event type lines
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

            # Debug output for parsed event data
            if debug:
                logger.debug(
                    f"Parsed event data for {current_event_type}: {json.dumps(data, indent=2, ensure_ascii=False)}"
                )

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

        # Handle event type lines
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


def send_hello_request(
    question="你好，Knowledge Forge!",
    search_context_size=None,
    country="CN",
    city="Shanghai",
    region=None,
    timezone=None,
    effort="low",
    debug=False,
):
    """Send a request to the Knowledge Forge API using SSE with web search tool.

    Args:
        question (str): The question to ask
        search_context_size (str, optional): Size of context for search ("low", "medium", "high")
        country (str, optional): Two-letter ISO country code
        city (str, optional): User's city
        region (str, optional): User's region
        timezone (str, optional): IANA timezone
        effort (str): Effort level for the response ("low", "medium", "high")
    """

    # Create a request that matches the OpenAI format
    request_json = {
        "model": "qwen3-235b-a22b",  # Using a valid OpenAI model
        "effort": effort,  # Move effort to top level
        "store": True,
        "input": [{"role": "user", "content": question}],
    }

    # Add web search tool
    web_search_tool = {"type": "web_search"}

    # Add optional search context size if provided
    if search_context_size:
        web_search_tool["search_context_size"] = search_context_size

    # Add optional user location if any location field is provided
    if any([country, city, region, timezone]):
        user_location = {"type": "approximate"}
        if country:
            user_location["country"] = country
        if city:
            user_location["city"] = city
        if region:
            user_location["region"] = region
        if timezone:
            user_location["timezone"] = timezone

        web_search_tool["user_location"] = user_location

    request_json["tools"] = [web_search_tool]
    logger.info(f"Using web search tool with configuration: {web_search_tool}")

    try:
        # Send the request to the API
        url = f"{BASE_URL}/v1/responses"
        console.print(Align.center(f"Sending request to: {url}"))
        console.print(Align.center(f"Request data: {json.dumps(request_json, ensure_ascii=False, indent=2)}"))

        # Use stream=True for SSE
        response = requests.post(url, json=request_json, stream=True)
        response.raise_for_status()

        # Process the SSE stream
        final_response, response_id = handle_sse_stream(response, debug=debug)

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
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Send requests to Knowledge Forge API with web search capabilities")
    parser.add_argument(
        "--search-context",
        choices=["low", "medium", "high"],
        default=None,
        help="Search context size (low, medium, high)",
    )
    parser.add_argument(
        "--country",
        type=str,
        default="CN",
        help="Two-letter ISO country code (e.g., US, CN)",
    )
    parser.add_argument("--city", type=str, default="Shanghai", help="User's city (e.g., San Francisco)")
    parser.add_argument("--region", type=str, default=None, help="User's region (e.g., California)")
    parser.add_argument("--timezone", type=str, default=None, help="IANA timezone (e.g., Asia/Shanghai)")
    parser.add_argument(
        "--question",
        "-q",
        type=str,
        default="What was a positive news story from today?",
        help="Question to ask using the web search tool",
    )
    parser.add_argument(
        "--effort",
        "-e",
        type=str,
        choices=["low", "medium", "high", "dev"],
        default="low",
        help="Effort level for the response (default: low)",
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Enable debug output with detailed event information",
    )
    args = parser.parse_args()

    send_hello_request(
        question=args.question,
        search_context_size=args.search_context,
        country=args.country,
        city=args.city,
        region=args.region,
        timezone=args.timezone,
        effort=args.effort,
        debug=args.debug,
    )
