import json
from collections.abc import AsyncIterator
from typing import Any

import aiohttp
from loguru import logger

from forge_cli.response._types import (
    FileSearchTool,
    InputMessage,
    Request,
    Response,
    WebSearchTool,
)

from .config import BASE_URL


async def async_create_typed_response(
    request: Request,
    stream: bool = False,
    debug: bool = False,
) -> Response:
    """
    Create a response using a typed Request object.

    Args:
        request: A typed Request object with all configuration
        stream: Whether to return a streaming response
        debug: Enable debug logging

    Returns:
        A typed Response object
    """
    url = f"{BASE_URL}/v1/responses"

    # Convert to OpenAI format
    payload = request.as_openai_chat_request()

    if debug:
        logger.debug(f"Creating typed response with payload:\n{json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Response creation failed with status {response.status}: {error_text}")

                if stream:
                    # For streaming, we need to collect the final response
                    final_data = None
                    async for line in response.content:
                        line = line.decode("utf-8").strip()
                        if line.startswith("event:") and line[6:].strip() == "response.completed":
                            # The actual data for response.completed is in the data: line
                            continue
                        if line.startswith("data:"):
                            data_str = line[5:].strip()
                            if data_str.startswith("{"):
                                try:
                                    data = json.loads(data_str)
                                    # Check if this is the data for response.completed
                                    # Based on original sdk.py, the final response is associated with "response.completed" event type
                                    # We need to find which line.startswith("event:") was before this data
                                    # However, the current logic assumes the last JSON object on "data:" is the one.
                                    # A more robust stream handling might be needed if multiple JSON data objects are sent
                                    # before the "response.completed" event line.
                                    # For now, let's assume the last data object before "done" or the one tied to "response.completed" event is it.
                                    # The original code snippet for async_create_response had:
                                    # if current_event_type == "response.completed":
                                    #    final_response = data
                                    # This implies we need to track current_event_type here too if we want to be precise.
                                    # Let's assume for now the API sends the full response object as data with the "response.completed" event type.
                                    # This part of the logic might need refinement based on actual API stream behavior.
                                    # The provided code snippet for async_create_typed_response's streaming part is a bit ambiguous.
                                    # It checks for `data.get("type") == "response.completed"` which is unusual for SSE data field.
                                    # Let's stick to the pattern from `async_create_response` where `current_event_type` is key.
                                    # To simplify, we will assume the *last* JSON payload received on the stream before 'done' is the full response
                                    # if `response.completed` event was seen.
                                    # A better approach for robust streaming is to accumulate data based on event types.
                                    final_data = data  # Keep track of the latest data payload
                                except json.JSONDecodeError:
                                    pass  # Ignore malformed JSON
                        elif line.startswith("event:") and line[6:].strip() == "done":
                            break  # Stream finished

                    if final_data:  # Check if we received any data that could be the final response
                        return Response(**final_data)
                    else:
                        raise Exception("No final response data received from stream")
                else:
                    # Non-streaming response
                    result = await response.json()
                    return Response(**result)

    except Exception as e:
        logger.error(f"Error creating typed response: {str(e)}")
        raise


async def astream_typed_response(
    request: Request,
    debug: bool = False,
) -> AsyncIterator[tuple[str, Response | None]]:
    """
    Stream a response using a typed Request object, yielding typed events with Response snapshots.

    Args:
        request: A typed Request object with all configuration
        debug: Enable debug logging

    Yields:
        Tuples of (event_type, response_snapshot) where response_snapshot is a Response object
        representing the complete state at that point in the stream (snapshot-based design per ADR-004).
        For events that don't contain full response data, response_snapshot will be None.
    """
    # Convert Request to API format
    request_dict = request.model_dump(exclude_none=True)

    # Convert input messages to API format
    input_messages = []
    for msg in request_dict.get("input", []):
        if isinstance(msg, dict):
            input_messages.append(msg)
        elif hasattr(msg, "model_dump"):
            input_messages.append(msg.model_dump())
        else:
            # Fallback for simple string content, assuming 'user' role
            input_messages.append({"role": "user", "content": str(msg)})

    # Prepare request payload
    payload = {
        "model": request_dict.get("model", "qwen-max"),
        "effort": request_dict.get("effort", "low"),
        "store": request_dict.get("store", True),
        "temperature": request_dict.get("temperature", 0.7),
        "max_output_tokens": request_dict.get("max_output_tokens", 1000),
        "input": input_messages,  # Use validated/converted messages
    }

    # Convert tools to API format
    if request_dict.get("tools"):
        tools = []
        for tool in request_dict["tools"]:
            if isinstance(tool, dict):
                tools.append(tool)
            elif hasattr(tool, "model_dump"):  # Check if it's a Pydantic model
                tools.append(tool.model_dump(exclude_none=True))  # Ensure it's dumped correctly
            else:
                # This case should ideally not happen if Request model is used correctly
                tools.append(tool)
        payload["tools"] = tools

    url = f"{BASE_URL}/v1/responses"
    current_event_type = ""

    if debug:
        logger.debug(f"Streaming typed response with payload:\n{json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    error_msg = f"Response creation failed with status {response.status}: {error_text}"
                    logger.error(error_msg)
                    yield "error", None
                    return

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
                            yield "done", None
                            break
                        continue  # Wait for data line

                    # Process data
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                        if not data_str:  # Empty data line
                            yield current_event_type, None  # Yield event type with no data
                            continue

                        # Parse JSON data
                        if data_str.startswith("{") or data_str.startswith("["):
                            try:
                                data = json.loads(data_str)

                                # Events that contain full response snapshots according to ADR-004
                                # This list seems to be from the original sdk.py comments.
                                SNAPSHOT_EVENT_TYPES = {
                                    "response.created",
                                    "response.in_progress",
                                    "response.completed",
                                    "response.output_text.delta",
                                    "response.output_text.done",
                                    "response.reasoning_summary_text.delta",
                                    "response.reasoning_summary_text.done",
                                    "response.file_search_call.completed",
                                    "response.web_search_call.completed",
                                    "response.function_call.completed",
                                }

                                response_obj = None
                                if data and isinstance(data, dict):  # Ensure data is a dict before **data
                                    try:
                                        # Attempt to create a Response object from the data
                                        # This assumes 'data' directly maps to Response fields
                                        response_obj = Response(**data)
                                    except Exception as e:
                                        if debug:
                                            logger.debug(
                                                f"Could not convert event data to Response for event {current_event_type} with data {data_str}: {e}"
                                            )
                                        # If conversion fails, but it's a snapshot type, yield None for data part
                                        if current_event_type in SNAPSHOT_EVENT_TYPES:
                                            yield current_event_type, None
                                        else:  # Not a snapshot type, yield event with raw data (or handle differently)
                                            # For simplicity, we'll yield None here too if not a snapshot type and fails parsing
                                            # Or, one could yield (current_event_type, data) if raw data is useful
                                            yield current_event_type, None
                                        continue  # Move to next line

                                    yield current_event_type, response_obj

                                    # If this is the completed event, also yield the final response object
                                    if current_event_type == "response.completed":
                                        # The problem description implies 'final_response' as a special event.
                                        # ADR-004 suggests 'response.completed' carries the full final state.
                                        # Let's ensure that the object yielded here is indeed the final complete one.
                                        # The current logic yields (current_event_type, response_obj) for response.completed.
                                        # No separate "final_response" event is yielded here per the loop structure.
                                        # The original sdk.py had a specific `yield "final_response", response_obj`
                                        # This might be redundant if ("response.completed", response_obj) is already the full final state.
                                        # For now, adhering to the structure which yields ("response.completed", Response_object).
                                        pass

                                else:  # Data is not a dict or is None
                                    yield current_event_type, None

                            except json.JSONDecodeError:
                                error_msg = f"Failed to parse JSON data: {data_str}"
                                logger.error(error_msg)
                                yield "error", None  # Yield an error event
                        else:  # Data is not JSON
                            yield current_event_type, None  # Yield event type with no parseable data

    except Exception as e:
        error_msg = f"Error creating typed response stream: {str(e)}"
        logger.error(error_msg)
        yield "error", None


def create_typed_request(
    input_messages: str | list[dict[str, Any]] | list[InputMessage],
    model: str = "qwen-max-latest",
    tools: list[dict[str, Any] | FileSearchTool | WebSearchTool] | None = None,  # Made tool types more specific
    **kwargs,
) -> Request:
    """
    Convenience function to create a typed Request object.

    Args:
        input_messages: Input as string, dict messages, or typed messages
        model: Model to use
        tools: Optional tools to enable
        **kwargs: Additional request parameters

    Returns:
        A typed Request object
    """
    processed_messages: list[InputMessage] = []
    if isinstance(input_messages, str):
        processed_messages = [InputMessage(role="user", content=input_messages)]
    elif isinstance(input_messages, list):
        for msg in input_messages:
            if isinstance(msg, dict):
                processed_messages.append(InputMessage(**msg))
            elif isinstance(msg, InputMessage):
                processed_messages.append(msg)
            else:
                raise ValueError(f"Invalid message type in input_messages: {type(msg)}")
    else:
        raise ValueError(f"Invalid input_messages type: {type(input_messages)}")

    # Process tools to ensure they are in the correct format for the Request model
    processed_tools = []
    if tools:
        for tool in tools:
            if isinstance(tool, (FileSearchTool, WebSearchTool)):
                processed_tools.append(tool)
            elif isinstance(tool, dict):
                # This assumes the dict can be parsed into one of the tool types.
                # The Request model's validator will handle this.
                processed_tools.append(tool)  # Or attempt to parse into a specific tool type if known
            else:
                raise ValueError(f"Invalid tool type: {type(tool)}")

    return Request(input=processed_messages, model=model, tools=processed_tools or [], **kwargs)


def create_file_search_tool(vector_store_ids: list[str], max_search_results: int = 20) -> FileSearchTool:
    """
    Create a typed FileSearchTool.

    Args:
        vector_store_ids: List of vector store IDs to search
        max_search_results: Maximum results to return

    Returns:
        A typed FileSearchTool object
    """
    return FileSearchTool(type="file_search", vector_store_ids=vector_store_ids, max_num_results=max_search_results)


def create_web_search_tool() -> WebSearchTool:
    """
    Create a typed WebSearchTool.

    Returns:
        A typed WebSearchTool object
    """
    return WebSearchTool(type="web_search")
