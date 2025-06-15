import aiohttp
from loguru import logger

from .config import BASE_URL


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
                    logger.error(f"Vector store creation failed with status {response.status}: {error_text}")
                    return None

                result = await response.json()
                return result
    except Exception as e:
        logger.error(f"Error creating vector store: {str(e)}")
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
                    logger.error(f"Vector store query failed with status {response.status}: {error_text}")
                    return None

                result = await response.json()
                return result
    except Exception as e:
        logger.error(f"Error querying vector store: {str(e)}")
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
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 404:
                    logger.warning(f"Vector store with ID {vector_store_id} not found")
                    return None
                elif response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Get vector store failed with status {response.status}: {error_text}")
                    return None

                result = await response.json()
                return result
    except Exception as e:
        logger.error(f"Error getting vector store: {str(e)}")
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
                    logger.warning(f"Vector store with ID {vector_store_id} not found")
                    return False
                elif response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Delete vector store failed with status {response.status}: {error_text}")
                    return False

                result = await response.json()
                return result.get("deleted", False)
    except Exception as e:
        logger.error(f"Error deleting vector store: {str(e)}")
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
                    logger.error(f"Join files to vector store failed with status {response.status}: {error_text}")
                    return None

                result = await response.json()
                return result
    except Exception as e:
        logger.error(f"Error joining files to vector store: {str(e)}")
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
                    logger.warning(f"Vector store with ID {vector_store_id} not found")
                    return None
                elif response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Get vector store summary failed with status {response.status}: {error_text}")
                    return None

                result = await response.json()
                return result
    except Exception as e:
        logger.error(f"Error getting vector store summary: {str(e)}")
        return None
