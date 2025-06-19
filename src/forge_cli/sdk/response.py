from __future__ import annotations

"""
Response module - Typed API only.

This module now only contains utility functions that work with typed Response objects.
All dict-based response creation functions have been removed in favor of typed_api.py.
"""

import aiohttp
from loguru import logger

from forge_cli.response._types import Response

from .config import BASE_URL

# All legacy dict-based response creation functions have been removed.
# Use typed_api.py functions instead:
# - async_create_typed_response() instead of async_create_response()
# - astream_typed_response() instead of create_stream_callback() + async_create_response()
# - create_typed_request() to build requests with type validation


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
