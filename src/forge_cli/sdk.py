#!/usr/bin/env python3
"""
Knowledge Forge API SDK - Client library for interacting with the Knowledge Forge API.

Design Guidelines:
1. All API functions MUST have an async version - sync versions are not needed
2. Use consistent naming: async_<action>_<resource> (e.g., async_upload_file, async_fetch_response)
3. All functions should handle errors gracefully and return None or appropriate default value on failure
4. Use proper type annotations for parameters and return values
5. Provide comprehensive docstrings for all functions

The SDK uses environment variables for configuration:
- KNOWLEDGE_FORGE_URL: API server URL (default: http://localhost:9999)
"""

import asyncio
import json
import mimetypes
import os
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, overload

import aiohttp
from loguru import logger

# Import typed API support - required!
from forge_cli.response._types import (
    FileSearchTool,
    InputMessage,
    Request,
    Response,
    ResponseCompletedEvent,
    ResponseStreamEvent,
    ResponseTextDeltaEvent,
    WebSearchTool,
)
from forge_cli.response.adapters import (
    ResponseAdapter,
    StreamEventAdapter,
    ToolAdapter,
)

# Use environment variable for server URL if available, otherwise default to localhost
BASE_URL = os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999")


async def async_upload_file(
    path: str,
    purpose: str = "general",
    custom_id: str = None,
    skip_exists: bool = False,
) -> dict[str, str | int | float | bool | list | dict]:
    """
    Asynchronously upload a file to the Knowledge Forge API and return the file details.

    Args:
        path: Path to the file to upload
        purpose: The intended purpose of the file (e.g., "qa", "general")
        custom_id: Optional custom ID for the file
        skip_exists: Whether to skip upload if file with same MD5 exists

    Returns:
        Dict containing file details including id and task_id
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    url = f"{BASE_URL}/v1/files"

    # Detect the actual content type of the file
    content_type, _ = mimetypes.guess_type(str(file_path))
    if content_type is None:
        content_type = "application/octet-stream"  # fallback for unknown types

    # Prepare form data
    form_data = aiohttp.FormData()
    form_data.add_field(
        "file",
        open(file_path, "rb"),
        filename=file_path.name,
        content_type=content_type,
    )
    form_data.add_field("purpose", purpose)

    if custom_id:
        form_data.add_field("id", custom_id)

    if skip_exists:
        form_data.add_field("skip_exists", "true")

    # Upload the file (aiohttp automatically sets Content-Type with boundary for FormData)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=form_data) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Upload failed with status {response.status}: {error_text}")

            result = await response.json()
            return result


async def async_check_task_status(task_id: str) -> dict[str, str | int | float | bool | list | dict]:
    """
    Check the status of a task by its ID.

    Args:
        task_id: The ID of the task to check

    Returns:
        Dict containing task status information
    """
    url = f"{BASE_URL}/v1/tasks/{task_id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Task status check failed with status {response.status}: {error_text}")

            result = await response.json()
            return result


async def async_wait_for_task_completion(
    task_id: str, poll_interval: int = 2, max_attempts: int = 60
) -> dict[str, str | int | float | bool | list | dict]:
    """
    Wait for a task to complete by polling its status.

    Args:
        task_id: The ID of the task to wait for
        poll_interval: How often to check the task status (in seconds)
        max_attempts: Maximum number of status checks before giving up

    Returns:
        Dict containing the final task status
    """
    attempts = 0

    while attempts < max_attempts:
        task_status = await async_check_task_status(task_id)
        status = task_status.get("status")

        # Check if task is complete
        if status in ["completed", "failed", "completed_with_errors"]:
            return task_status

        # Wait before checking again
        await asyncio.sleep(poll_interval)
        attempts += 1

    raise TimeoutError(f"Task {task_id} did not complete within the allowed time")


async def async_fetch_file(file_id: str) -> dict[str, str | int | float | bool | list | dict] | None:
    """
    Asynchronously fetch file information by its ID.

    Args:
        file_id: The ID of the file to fetch

    Returns:
        Dict containing file details or None if not found
    """
    url = f"{BASE_URL}/v1/files/{file_id}/content"  # Fixed: Use correct endpoint

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 404:
                    print(f"File with ID {file_id} not found")
                    return None
                elif response.status != 200:
                    error_text = await response.text()
                    print(f"Fetch file failed with status {response.status}: {error_text}")
                    return None

                result = await response.json()
                return result
    except Exception as e:
        print(f"Error fetching file: {str(e)}")
        return None


async def async_create_vectorstore(
    name: str,
    description: str = None,
    file_ids: list[str] = None,
    custom_id: str = None,
    metadata: dict[str, str | int | float | bool | list | dict] = None,
) -> dict[str, str | int | float | bool | list | dict] | None:
    """
    Asynchronously create a new vector store.

    Args:
        name: Name of the vector store
        description: Optional description of the vector store
        file_ids: Optional list of file IDs to include in the vector store
        custom_id: Optional custom ID for the vector store
        metadata: Optional additional metadata for the vector store

    Returns:
        Dict containing vector store details or None if creation failed
    """
    url = f"{BASE_URL}/v1/vector_stores"

    # Prepare request payload
    payload = {
        "name": name,
    }

    if custom_id:
        payload["id"] = custom_id

    if description:
        payload["description"] = description

    if file_ids:
        payload["file_ids"] = file_ids

    if metadata:
        payload["metadata"] = metadata

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Vector store creation failed with status {response.status}: {error_text}")
                    return None

                result = await response.json()
                return result
    except Exception as e:
        print(f"Error creating vector store: {str(e)}")
        return None


async def async_query_vectorstore(
    vector_store_id: str,
    query: str,
    top_k: int = 10,
    filters: dict[str, str | int | float | bool | list | dict] = None,
) -> dict[str, str | int | float | bool | list | dict] | None:
    """
    Asynchronously query a vector store.

    Args:
        vector_store_id: ID of the vector store to query
        query: Search query text
        top_k: Number of results to return (default: 10)
        filters: Optional filters to apply to the search

    Returns:
        Dict containing search results or None if query failed
    """
    url = f"{BASE_URL}/v1/vector_stores/{vector_store_id}/search"

    # Prepare request payload
    payload = {
        "query": query,
        "top_k": top_k,
    }

    if filters:
        payload["filters"] = filters

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Vector store query failed with status {response.status}: {error_text}")
                    return None

                result = await response.json()
                return result
    except Exception as e:
        print(f"Error querying vector store: {str(e)}")
        return None


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
                print(f"\nError: {data.get('message', 'Unknown error occurred')}")

    return stream_callback


@overload
async def astream_response(
    input_messages: str | list[dict[str, str]],
    model: str = "qwen-max",
    effort: str = "low",
    store: bool = True,
    temperature: float = 0.7,
    max_output_tokens: int = 1000,
    tools: list[dict[str, str | int | float | bool | list | dict]] = None,
    debug: bool = False,
    typed: bool = False,
) -> AsyncIterator[tuple[str, dict[str, Any] | None]]: ...


@overload
async def astream_response(
    input_messages: str | list[dict[str, str]],
    model: str = "qwen-max",
    effort: str = "low",
    store: bool = True,
    temperature: float = 0.7,
    max_output_tokens: int = 1000,
    tools: list[dict[str, str | int | float | bool | list | dict]] = None,
    debug: bool = False,
    typed: bool = True,
) -> AsyncIterator[tuple[str, ResponseStreamEvent | None]]: ...


async def astream_response(
    input_messages: str | list[dict[str, str]],
    model: str = "qwen-max",
    effort: str = "low",
    store: bool = True,
    temperature: float = 0.7,
    max_output_tokens: int = 1000,
    tools: list[dict[str, str | int | float | bool | list | dict]] = None,
    debug: bool = False,
    typed: bool = False,
):
    """
    Asynchronously stream a response using the Knowledge Forge API, yielding SSE events.
    This is an alternative to the callback approach that's easier to use in many cases.

    Args:
        input_messages: String or list of message objects with role and content
        model: The model to use for generating the response
        effort: The effort level for the response ("low", "medium", "high")
        store: Whether to store the response in the database
        temperature: The temperature for response generation
        max_output_tokens: The maximum number of tokens to generate
        tools: Optional list of tools to use for the response
        typed: If True, yields typed ResponseStreamEvent objects (requires response._types)

    Yields:
        Tuples of (event_type, event_data) representing SSE events.
        If typed=True, event_data will be ResponseStreamEvent objects.
    """
    # Typed API is now always available
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

    # Initialize current event type
    current_event_type = ""

    if debug:
        logger.debug(f"Streaming response with payload:\n{json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    error_msg = f"Response creation failed with status {response.status}: {error_text}"
                    logger.error(error_msg)
                    yield "error", {"message": error_msg}
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

                        # Yield the event type without data
                        yield current_event_type, None
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
                                
                                # Yield typed event if requested
                                if typed:
                                    try:
                                        typed_event = StreamEventAdapter.parse_event({
                                            "type": current_event_type,
                                            **data
                                        })
                                        yield current_event_type, typed_event
                                    except Exception:
                                        # Fallback to dict if typing fails
                                        yield current_event_type, data
                                else:
                                    yield current_event_type, data

                                # If this is the completed event, also yield the final response
                                if current_event_type == "response.completed":
                                    if typed:
                                        yield "final_response", typed_event if 'typed_event' in locals() else data
                                    else:
                                        yield "final_response", data
                            except json.JSONDecodeError:
                                error_msg = f"Failed to parse JSON data: {data_str}"
                                logger.error(error_msg)
                                yield "error", {"message": error_msg}

    except Exception as e:
        error_msg = f"Error creating response: {str(e)}"
        logger.error(error_msg)
        yield "error", {"message": error_msg}


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
) -> dict[str, str | int | float | bool | list | dict]:
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

    Returns:
        Dict containing the final response data
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
        print(f"Creating response with payload:\n{json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Response creation failed with status {response.status}: {error_text}")
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
                                print(f"Failed to parse JSON data: {data_str}")

    except Exception as e:
        print(f"Error creating response: {str(e)}")
        return None

    return final_response


# Additional API functions that were missing


async def async_delete_file(file_id: str) -> bool:
    """
    Asynchronously delete a file by its ID.

    Args:
        file_id: The ID of the file to delete

    Returns:
        True if successfully deleted, False otherwise
    """
    url = f"{BASE_URL}/v1/files/{file_id}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(url) as response:
                if response.status == 404:
                    print(f"File with ID {file_id} not found")
                    return False
                elif response.status != 200:
                    error_text = await response.text()
                    print(f"Delete file failed with status {response.status}: {error_text}")
                    return False

                result = await response.json()
                return result.get("deleted", False)
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
        return False


async def async_get_vectorstore(vector_store_id: str) -> dict[str, str | int | float | bool | list | dict] | None:
    """
    Asynchronously get vector store information by its ID.

    Args:
        vector_store_id: The ID of the vector store to fetch

    Returns:
        Dict containing vector store details or None if not found
    """
    url = f"{BASE_URL}/v1/vector_stores/{vector_store_id}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 404:
                    print(f"Vector store with ID {vector_store_id} not found")
                    return None
                elif response.status != 200:
                    error_text = await response.text()
                    print(f"Get vector store failed with status {response.status}: {error_text}")
                    return None

                result = await response.json()
                return result
    except Exception as e:
        print(f"Error getting vector store: {str(e)}")
        return None


async def async_delete_vectorstore(vector_store_id: str) -> bool:
    """
    Asynchronously delete a vector store by its ID.

    Args:
        vector_store_id: The ID of the vector store to delete

    Returns:
        True if successfully deleted, False otherwise
    """
    url = f"{BASE_URL}/v1/vector_stores/{vector_store_id}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(url) as response:
                if response.status == 404:
                    print(f"Vector store with ID {vector_store_id} not found")
                    return False
                elif response.status != 200:
                    error_text = await response.text()
                    print(f"Delete vector store failed with status {response.status}: {error_text}")
                    return False

                result = await response.json()
                return result.get("deleted", False)
    except Exception as e:
        print(f"Error deleting vector store: {str(e)}")
        return False


async def async_join_files_to_vectorstore(
    vector_store_id: str, file_ids: list[str]
) -> dict[str, str | int | float | bool | list | dict] | None:
    """
    Asynchronously join files to an existing vector store.

    Args:
        vector_store_id: The ID of the vector store
        file_ids: List of file IDs to join to the vector store

    Returns:
        Dict containing updated vector store details or None if failed
    """
    url = f"{BASE_URL}/v1/vector_stores/{vector_store_id}"

    payload = {"join_file_ids": file_ids}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Join files to vector store failed with status {response.status}: {error_text}")
                    return None

                result = await response.json()
                return result
    except Exception as e:
        print(f"Error joining files to vector store: {str(e)}")
        return None


async def async_get_vectorstore_summary(
    vector_store_id: str, model: str = "qwen-max", max_tokens: int = 1000
) -> dict[str, str | int | float | bool | list | dict] | None:
    """
    Asynchronously get vector store summary.

    Args:
        vector_store_id: The ID of the vector store
        model: The model to use for generating the summary
        max_tokens: Maximum tokens for the summary

    Returns:
        Dict containing summary information or None if failed
    """
    url = f"{BASE_URL}/v1/vector_stores/{vector_store_id}/summary"

    # Use query parameters for GET request
    params = {"model": model, "max_tokens": max_tokens}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 404:
                    print(f"Vector store with ID {vector_store_id} not found")
                    return None
                elif response.status != 200:
                    error_text = await response.text()
                    print(f"Get vector store summary failed with status {response.status}: {error_text}")
                    return None

                result = await response.json()
                return result
    except Exception as e:
        print(f"Error getting vector store summary: {str(e)}")
        return None


async def async_fetch_response(response_id: str) -> dict[str, str | int | float | bool | list | dict] | None:
    """
    Asynchronously fetch a response by its ID.

    Args:
        response_id: The ID of the response to fetch

    Returns:
        Dict containing the response data or None if not found/error
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
                return result
    except Exception as e:
        logger.error(f"Error fetching response: {str(e)}")
        return None


# Utility functions for result handling


def print_file_results(upload_result: dict[str, str | int | float | bool | list | dict]) -> None:
    """Print formatted file upload results."""
    if upload_result:
        print(f"File uploaded: {upload_result.get('filename')}")
        print(f"File ID: {upload_result.get('id')}")
        print(f"Size: {upload_result.get('bytes')} bytes")
        if upload_result.get("task_id"):
            print(f"Processing task: {upload_result.get('task_id')}")


def print_vectorstore_results(result: dict[str, str | int | float | bool | list | dict], query: str) -> None:
    """Print formatted vector store query results."""
    if result:
        print(f"Found {len(result['data'])} results for query: '{query}'")
        for i, item in enumerate(result["data"], 1):
            print(f"\nResult #{i}:")
            print(f"  Score: {item['score']:.4f}")
            print(f"  File: {item['filename']} (ID: {item['file_id']})")
            if item["content"] and len(item["content"]) > 0:
                content_text = item["content"][0].get("text", "")
                if content_text:
                    if len(content_text) > 100:
                        content_text = content_text[:100] + "..."
                    print(f"  Content: {content_text}")


def print_response_results(result: dict[str, str | int | float | bool | list | dict]) -> None:
    """Print formatted response results."""
    if result and "output" in result:
        for msg in result["output"]:
            if msg.get("role") == "assistant" and "content" in msg:
                content = msg["content"]
                if isinstance(content, list):
                    for item in content:
                        if item.get("type") == "text":
                            print(f"Assistant: {item.get('text', '')}")
                else:
                    print(f"Assistant: {content}")


# Note: In production code, consider implementing these print functions as async functions
# for consistent use with the async API. For now, they remain synchronous as they don't
# perform any I/O operations beyond printing to console.


# Typed API functions - Using the new type system


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
                            continue
                        if line.startswith("data:"):
                            data_str = line[5:].strip()
                            if data_str.startswith("{"):
                                try:
                                    data = json.loads(data_str)
                                    if data.get("type") == "response.completed":
                                        final_data = data
                                except json.JSONDecodeError:
                                    pass
                    
                    if final_data:
                        return ResponseAdapter.from_dict(final_data)
                    else:
                        raise Exception("No final response received from stream")
                else:
                    # Non-streaming response
                    result = await response.json()
                    return ResponseAdapter.from_dict(result)
    
    except Exception as e:
        logger.error(f"Error creating typed response: {str(e)}")
        raise


async def astream_typed_response(
    request: Request,
    debug: bool = False,
) -> AsyncIterator[tuple[str, ResponseStreamEvent]]:
    """
    Stream a response using a typed Request object, yielding typed events.
    
    Args:
        request: A typed Request object with all configuration
        debug: Enable debug logging
        
    Yields:
        Tuples of (event_type, typed_event) where typed_event is a ResponseStreamEvent
    """
    # Use the existing streaming function with typed=True
    messages = request.input_as_typed_messages()
    dict_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
    
    tools = []
    if request.tools:
        for tool in request.tools:
            if hasattr(tool, 'as_openai_tool'):
                tools.append(tool.as_openai_tool())
            else:
                tools.append(tool)
    
    async for event_type, event_data in astream_response(
        input_messages=dict_messages,
        model=request.model,
        effort=request.effort or "low",
        store=request.store if request.store is not None else True,
        temperature=request.temperature or 0.7,
        max_output_tokens=request.max_output_tokens or 1000,
        tools=tools if tools else None,
        debug=debug,
        typed=True,
    ):
        yield event_type, event_data


def create_typed_request(
    input_messages: Union[str, List[Dict[str, Any]], List[InputMessage]],
    model: str = "qwen-max-latest",
    tools: Optional[List[Union[Dict[str, Any], "Tool"]]] = None,
    **kwargs
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
    return ResponseAdapter.create_request(
        input_messages=input_messages,
        model=model,
        tools=tools,
        **kwargs
    )


def create_file_search_tool(
    vector_store_ids: List[str],
    max_search_results: int = 20
) -> FileSearchTool:
    """
    Create a typed FileSearchTool.
    
    Args:
        vector_store_ids: List of vector store IDs to search
        max_search_results: Maximum results to return
        
    Returns:
        A typed FileSearchTool object
    """
    return ToolAdapter.create_file_search_tool(
        vector_store_ids=vector_store_ids,
        max_search_results=max_search_results
    )


def create_web_search_tool() -> WebSearchTool:
    """
    Create a typed WebSearchTool.
    
    Returns:
        A typed WebSearchTool object
    """
    return ToolAdapter.create_web_search_tool()
