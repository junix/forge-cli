#!/usr/bin/env python3
import argparse
import json
import logging
import os
from typing import Any

import requests
from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.panel import Panel

# Set up a simple logger
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
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

    # If we get the 'done' event, signal to stop processing
    if event_type == "response.output_text.done" or event_type == "done":
        return event_type, True

    return event_type, False


def extract_reasoning_and_text(
    data: dict[str, Any],
) -> tuple[str | None, str | None]:
    """Extract reasoning and text output from response data.

    Args:
        data (dict): The parsed JSON data from an event

    Returns:
        Tuple[Optional[str], Optional[str]]: The reasoning text and output text if available
    """
    reasoning_text = None
    output_text = None

    # For delta updates
    if "delta" in data:
        return None, data.get("delta", "")

    # For reasoning in the 'reason' field (as shown in the example)
    if "reason" in data:
        reason_data = data.get("reason", {})
        if "summary" in reason_data:
            for summary_item in reason_data.get("summary", []):
                if summary_item.get("type") == "summary_text":
                    reasoning_text = summary_item.get("text", "")

    # Extract reasoning from output items
    if "output" in data:
        for output_item in data.get("output", []):
            if output_item.get("type") == "reasoning":
                for summary_item in output_item.get("summary", []):
                    if summary_item.get("type") == "summary_text":
                        reasoning_text = summary_item.get("text", "")

            # Extract text from message content
            if output_item.get("type") == "message":
                for content_item in output_item.get("content", []):
                    if content_item.get("type") == "output_text":
                        output_text = content_item.get("text", "")

    # Direct extraction from message field
    if "message" in data:
        message = data.get("message", {})
        content_items = message.get("content", [])
        for item in content_items:
            if item.get("type") == "output_text":
                output_text = item.get("text", "")

    # Log the extracted content for debugging
    if reasoning_text:
        logger.debug(f"Extracted reasoning text: {reasoning_text[:100]}...")
    if output_text:
        logger.debug(f"Extracted output text: {output_text[:100]}...")

    return reasoning_text, output_text


def format_as_markdown(reasoning: str | None, text: str | None) -> str:
    """Format reasoning and text as markdown.

    Args:
        reasoning (Optional[str]): The reasoning text
        text (Optional[str]): The output text

    Returns:
        str: Formatted markdown string
    """
    markdown = ""

    if reasoning:
        markdown += "## Reasoning\n\n"
        markdown += reasoning + "\n\n"

    if text:
        markdown += "## Response\n\n"
        markdown += text

    return markdown


def handle_sse_stream(response):
    """Handle the Server-Sent Events (SSE) stream with rich.live updates.

    Args:
        response (Response): The requests response object with stream=True

    Returns:
        dict: The final response data
        str: The response ID
    """
    final_response = None
    response_id = None
    current_event_type = None

    # Initialize content storage
    accumulated_reasoning = ""
    accumulated_text = ""

    # Create a simple panel for the live display
    panel = Panel("Waiting for response...")

    # Start the live display
    with Live(panel, console=console, refresh_per_second=4) as live:
        try:
            for line in response.iter_lines():
                if not line:
                    continue

                line = line.decode("utf-8")
                logger.debug(f"Raw line: {line}")

                if line.startswith("event:"):
                    event_type, is_done = process_event_type(line)
                    current_event_type = event_type
                    # Log the event type for debugging
                    logger.debug(f"Event type: {event_type}")

                    # Update the display with the current event type
                    panel = Panel(
                        f"Event: {event_type}\nReasoning: {len(accumulated_reasoning) > 0}\nText: {accumulated_text[:50]}..."
                    )
                    live.update(panel)
                    continue

                # Skip non-data lines
                if not line.startswith("data:"):
                    continue

                data_str = line[5:].strip()
                if not data_str:
                    continue

                # Only try to parse as JSON if it looks like a JSON object
                if data_str.startswith("{") or data_str.startswith("["):
                    try:
                        data = json.loads(data_str)

                        # Log the data for debugging
                        logger.debug(f"Received data type: {current_event_type}")

                        # Handle delta updates directly for text
                        if current_event_type == "response.output_text.delta":
                            delta = data.get("delta", "")
                            if delta:
                                logger.debug(f"Delta update: {delta}")
                                accumulated_text += delta
                        else:
                            # Extract reasoning and text for other event types
                            reasoning, text = extract_reasoning_and_text(data)

                            # Update accumulated content
                            if reasoning:
                                accumulated_reasoning = reasoning
                                logger.debug(f"Updated reasoning: {reasoning[:50]}...")

                            if text:
                                accumulated_text += text
                                logger.debug(f"Updated text: {text[:50]}...")

                        # Update the display with the current content
                        content_preview = accumulated_text[:100] + "..." if accumulated_text else "No text yet"
                        panel = Panel(f"Event: {current_event_type}\nText: {content_preview}")
                        live.update(panel)

                        # Store final response for response.completed event
                        if current_event_type == "response.completed":
                            response_id = data.get("id")
                            final_response = data

                            # Show the final response
                            panel = Panel(f"Response completed\n\n{accumulated_text}")
                            live.update(panel)

                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing SSE data: {e}")
                        logger.error(f"Raw data: {data_str}")
                else:
                    # For non-JSON data lines, just log them without trying to parse
                    logger.debug(f"Non-JSON data for event type '{current_event_type}': {data_str}")

                if is_done:
                    break

        except Exception as e:
            logger.error(f"Error in handle_sse_stream: {e}")
            panel = Panel(f"Error: {str(e)}")
            live.update(panel)

    # Display the final result
    if accumulated_text:
        console.print("\nFinal Response:")
        console.print(accumulated_text)

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
        final_response, _ = handle_sse_stream(response)

        return final_response

    except requests.exceptions.RequestException as e:
        return handle_request_error(e)


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
        help="Effort level for the response (default: low)",
    )
    args = parser.parse_args()

    send_hello_request(args.query, args.effort)
