import json

import aiohttp
from loguru import logger

from forge_cli.response._types import Response

from .config import BASE_URL


def validate_input_messages(
    input_messages: str | list[dict[str, str]],
) -> list[dict[str, str]]:
    """
    Validate and normalize input messages for the response API.

    Args:
        input_messages: Input messages as a string or list of message objects

    Returns:
        Normalized list of message objects with required ID field

    Raises:
        ValueError: If input messages are invalid
    """
    # Validate input messages
    if not input_messages:
        raise ValueError("Input messages cannot be empty")

    # Convert string input to a message if needed
    if isinstance(input_messages, str):
        input_messages = [{"role": "user", "id": "message_1", "content": input_messages}]

    # Ensure all messages have role, content, and an ID
    for i, msg in enumerate(input_messages):
        if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
            raise ValueError("Each message must be a dict with 'role' and 'content' keys")

        # Add ID if not present
        if "id" not in msg:
            msg["id"] = f"message_{i + 1}"

    return input_messages


async def create_stream_callback(stream: bool = True, debug: bool = False):
    """
    Create a callback function for streaming response updates.

    Args:
        stream: Whether to print streaming updates
        debug: Whether to print detailed debug information

    Returns:
        A callback function that can be passed to async_create_response
    """

    async def stream_callback(event):
        if stream:
            event_type = event["type"]
            data = event["data"] or {}

            # Print debug information if requested
            if debug:
                info = {"event_type": event_type, **data}
                logger.debug(f"Stream callback:\n{json.dumps(info, indent=2, ensure_ascii=False)}")

            # Handle text streaming for user display
            if event_type == "response.output_text.delta" and data and "text" in data:
                text_content = data["text"]
                # Handle various text content formats
                if isinstance(text_content, dict) and "text" in text_content:
                    fragment = text_content["text"]
                    print(fragment, end="", flush=True)
                elif isinstance(text_content, str):
                    print(text_content, end="", flush=True)
            elif event_type == "response.output_text.done":
                print()  # Add a newline at the end

            # Handle error events
            if event_type == "response.error":
                logger.error(f"\nError: {data.get('message', 'Unknown error occurred')}")

    return stream_callback


async def async_create_response(
    input_messages: str | list[dict[str, str]],
    model: str = "qwen-max",
    effort: str = "low",
    store: bool = True,
    temperature: float = 0.7,
    max_output_tokens: int = 1000,
    tools: list[dict[str, str | int | float | bool | list | dict]] = None,
    callback=None,
    debug: bool = False,
) -> Response | None:
    """
    Asynchronously create a response using the Knowledge Forge API with SSE streaming.

    Args:
        input_messages: String or list of message objects with role and content
        model: The model to use for generating the response
        effort: The effort level for the response ("low", "medium", "high")
        store: Whether to store the response in the database
        temperature: The temperature for response generation
        max_output_tokens: The maximum number of tokens to generate
        tools: Optional list of tools to use for the response
        callback: Optional callback function to process SSE events
        debug: Whether to enable debug logging

    Returns:
        Response object with methods for citation management, tool call analysis,
        text extraction, and content compression. Returns None on error.

    Example:
        >>> response = await async_create_response("What is machine learning?")
        >>> if response:
        ...     print(response.output_text)  # Get formatted text
        ...     citations = response.install_citation_id()  # Add citation IDs
        ...     print(f"Citations: {len(citations)}")
    """
    url = f"{BASE_URL}/v1/responses"

    # Validate and normalize input messages
    normalized_messages = validate_input_messages(input_messages)

    # Prepare request payload
    payload = {
        "model": model,
        "effort": effort,
        "store": store,
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
        "input": normalized_messages,
    }

    if tools:
        payload["tools"] = tools

    # Initialize variables to store response data
    final_response = None
    current_event_type = ""

    if debug:
        logger.debug(f"Creating response with payload:\n{json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Response creation failed with status {response.status}: {error_text}")
                    return None

                # Process the SSE stream
                async for line in response.content:
                    line = line.decode("utf-8").strip()

                    if not line:
                        continue

                    # Process event type
                    if line.startswith("event:"):
                        current_event_type = line[6:].strip()

                        # If this is the "done" event, we're finished
                        if current_event_type == "done":
                            break

                        # Call the callback if provided
                        if callback:
                            await callback({"type": current_event_type, "data": None})

                        continue

                    # Process data
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                        if not data_str:
                            continue

                        # Parse JSON data
                        if data_str.startswith("{") or data_str.startswith("["):
                            try:
                                data = json.loads(data_str)

                                # Call the callback if provided
                                if callback:
                                    await callback({"type": current_event_type, "data": data})

                                # Store the final response
                                if current_event_type == "response.completed":
                                    final_response = data
                            except json.JSONDecodeError:
                                logger.error(f"Failed to parse JSON data: {data_str}")

    except Exception as e:
        logger.error(f"Error creating response: {str(e)}")
        return None

    # Convert to Response object if we have data
    if final_response:
        try:
            return Response.model_validate(final_response)
        except Exception as e:
            logger.error(f"Failed to parse response data: {e}")
            return None
    return None


async def async_fetch_response(response_id: str) -> Response | None:
    """
    Asynchronously fetch a response by its ID.

    Args:
        response_id: The ID of the response to fetch

    Returns:
        Response object containing the response data or None if not found/error
    """
    url = f"{BASE_URL}/v1/responses/{response_id}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 404:
                    logger.warning(f"Response with ID {response_id} not found")
                    return None
                elif response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Fetch response failed with status {response.status}: {error_text}")
                    return None

                result = await response.json()
                # Convert to Response object
                try:
                    return Response.model_validate(result)
                except Exception as e:
                    logger.error(f"Failed to parse response data: {e}")
                    return None
    except Exception as e:
        logger.error(f"Error fetching response: {str(e)}")
        return None
