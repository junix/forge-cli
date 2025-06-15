from loguru import logger

from .config import BASE_URL
from .http_client import async_make_request


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
        status_code, response_data = await async_make_request("POST", url, json_payload=payload)
        if status_code == 200 and isinstance(response_data, dict):
            return response_data
        elif status_code == 200 and isinstance(response_data, str):
            logger.error(f"Vector store creation failed: Server returned 200 but response was not valid JSON. Name: {name}, Custom ID: {custom_id}. Content: {response_data}")
            return None
        # Non-200 errors are raised by async_make_request.
        # If we reach here for other statuses, it's an issue with async_make_request or unhandled case.
        # However, the design is that async_make_request handles raising exceptions for errors.
        # So, this path should ideally not be hit for error statuses.
        # If it's a non-200 status that async_make_request didn't raise for, log it.
        elif status_code != 200: # Should have been raised by http_client
             logger.error(f"Vector store creation for {name} returned unhandled status {status_code}. Data: {response_data}")
             return None
        return None # Fallback
    except Exception as e:
        logger.error(f"Error creating vector store '{name}': {str(e)}")
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
        status_code, response_data = await async_make_request("POST", url, json_payload=payload)
        if status_code == 200 and isinstance(response_data, dict):
            return response_data
        elif status_code == 200 and isinstance(response_data, str):
            logger.error(f"Vector store query failed: Server returned 200 but response was not valid JSON. VSID: {vector_store_id}. Content: {response_data}")
            return None
        elif status_code != 200: # Should have been raised by http_client
             logger.error(f"Vector store query for {vector_store_id} returned unhandled status {status_code}. Data: {response_data}")
             return None
        return None # Fallback
    except Exception as e:
        logger.error(f"Error querying vector store {vector_store_id}: {str(e)}")
        return None


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
        status_code, response_data = await async_make_request("GET", url)
        if status_code == 200 and isinstance(response_data, dict):
            return response_data
        elif status_code == 404:
            # Logging handled by async_make_request
            return None
        elif status_code == 200 and isinstance(response_data, str):
            logger.error(f"Get vector store failed: Server returned 200 but response was not valid JSON. VSID: {vector_store_id}. Content: {response_data}")
            return None
        elif status_code != 200: # Should have been raised by http_client
             logger.error(f"Get vector store for {vector_store_id} returned unhandled status {status_code}. Data: {response_data}")
             return None
        return None # Fallback
    except Exception as e:
        logger.error(f"Error getting vector store {vector_store_id}: {str(e)}")
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
        status_code, response_data = await async_make_request("DELETE", url)
        if status_code == 200 and isinstance(response_data, dict):
            return response_data.get("deleted", False)
        elif status_code == 404:
            # Logging handled by async_make_request
            return False
        elif status_code == 200 and isinstance(response_data, str): # Should be JSON
            logger.error(f"Delete vector store failed: Server returned 200 but response was not valid JSON. VSID: {vector_store_id}. Content: {response_data}")
            return False
        elif status_code != 200: # Should have been raised by http_client
             logger.error(f"Delete vector store for {vector_store_id} returned unhandled status {status_code}. Data: {response_data}")
             return False
        return False # Fallback
    except Exception as e:
        logger.error(f"Error deleting vector store {vector_store_id}: {str(e)}")
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
        status_code, response_data = await async_make_request("POST", url, json_payload=payload)
        if status_code == 200 and isinstance(response_data, dict):
            return response_data
        elif status_code == 200 and isinstance(response_data, str):
            logger.error(f"Join files to vector store failed: Server returned 200 but response was not valid JSON. VSID: {vector_store_id}. Content: {response_data}")
            return None
        elif status_code != 200: # Should have been raised by http_client
             logger.error(f"Join files to vector store for {vector_store_id} returned unhandled status {status_code}. Data: {response_data}")
             return None
        return None # Fallback
    except Exception as e:
        logger.error(f"Error joining files to vector store {vector_store_id}: {str(e)}")
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
        status_code, response_data = await async_make_request("GET", url, params=params)
        if status_code == 200 and isinstance(response_data, dict):
            return response_data
        elif status_code == 404:
            # Logging handled by async_make_request
            return None
        elif status_code == 200 and isinstance(response_data, str):
            logger.error(f"Get vector store summary failed: Server returned 200 but response was not valid JSON. VSID: {vector_store_id}. Content: {response_data}")
            return None
        elif status_code != 200: # Should have been raised by http_client
             logger.error(f"Get vector store summary for {vector_store_id} returned unhandled status {status_code}. Data: {response_data}")
             return None
        return None # Fallback
    except Exception as e:
        logger.error(f"Error getting vector store summary for {vector_store_id}: {str(e)}")
        return None
