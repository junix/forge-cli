from __future__ import annotations

from loguru import logger

from .config import BASE_URL
from .http_client import async_make_request

# Import new types
from .types import DeleteResponse, Vectorstore, VectorStoreQueryResponse, VectorStoreSummary  # Updated imports


async def async_create_vectorstore(
    name: str,
    description: str = None,
    file_ids: list[str] = None,
    custom_id: str = None,
    metadata: dict[str, str | int | float | bool | list | dict] = None,
) -> Vectorstore | None:  # Changed return type
    """
    Asynchronously create a new vector store.
    ...
    Returns:
        Vectorstore object containing vector store details or None if creation failed
    """
    url = f"{BASE_URL}/v1/vector_stores"
    payload = {"name": name}
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
            try:
                return Vectorstore.model_validate(response_data)
            except Exception as e:
                logger.error(
                    f"Vector store creation for {name} succeeded but failed to parse response: {e}. Data: {response_data}"
                )
                return None
        elif status_code == 200 and isinstance(response_data, str):
            logger.error(
                f"Vector store creation failed: Server returned 200 but response was not valid JSON. Name: {name}. Content: {response_data}"
            )
            return None
        elif status_code != 200:
            logger.error(
                f"Vector store creation for {name} returned unhandled status {status_code}. Data: {response_data}"
            )
            return None
        return None
    except Exception as e:
        logger.error(f"Error creating vector store '{name}': {str(e)}")
        return None


async def async_query_vectorstore(
    vector_store_id: str,
    query: str,
    top_k: int = 10,
    filters: dict[str, str | int | float | bool | list | dict] = None,
) -> VectorStoreQueryResponse | None:  # Changed return type
    """
    Asynchronously query a vector store.
    ...
    Returns:
        VectorStoreQueryResponse object containing search results or None if query failed
    """
    url = f"{BASE_URL}/v1/vector_stores/{vector_store_id}/search"
    payload = {"query": query, "top_k": top_k}
    if filters:
        payload["filters"] = filters

    try:
        status_code, response_data = await async_make_request("POST", url, json_payload=payload)
        if status_code == 200 and isinstance(response_data, dict):
            try:
                return VectorStoreQueryResponse.model_validate(response_data)
            except Exception as e:
                logger.error(
                    f"Vector store query for {vector_store_id} succeeded but failed to parse response: {e}. Data: {response_data}"
                )
                return None
        elif status_code == 200 and isinstance(response_data, str):
            logger.error(
                f"Vector store query failed: Server returned 200 but response was not valid JSON. VSID: {vector_store_id}. Content: {response_data}"
            )
            return None
        elif status_code != 200:
            logger.error(
                f"Vector store query for {vector_store_id} returned unhandled status {status_code}. Data: {response_data}"
            )
            return None
        return None
    except Exception as e:
        logger.error(f"Error querying vector store {vector_store_id}: {str(e)}")
        return None


async def async_get_vectorstore(vector_store_id: str) -> Vectorstore | None:  # Changed return type
    """
    Asynchronously get vector store information by its ID.
    ...
    Returns:
        Vectorstore object containing vector store details or None if not found
    """
    url = f"{BASE_URL}/v1/vector_stores/{vector_store_id}"

    try:
        status_code, response_data = await async_make_request("GET", url)
        if status_code == 200 and isinstance(response_data, dict):
            try:
                return Vectorstore.model_validate(response_data)
            except Exception as e:
                logger.error(
                    f"Get vector store {vector_store_id} succeeded but failed to parse response: {e}. Data: {response_data}"
                )
                return None
        elif status_code == 404:
            return None
        elif status_code == 200 and isinstance(response_data, str):
            logger.error(
                f"Get vector store failed: Server returned 200 but response was not valid JSON. VSID: {vector_store_id}. Content: {response_data}"
            )
            return None
        elif status_code != 200:
            logger.error(
                f"Get vector store for {vector_store_id} returned unhandled status {status_code}. Data: {response_data}"
            )
            return None
        return None
    except Exception as e:
        logger.error(f"Error getting vector store {vector_store_id}: {str(e)}")
        return None


async def async_delete_vectorstore(vector_store_id: str) -> DeleteResponse | None:  # Changed return type
    """
    Asynchronously delete a vector store by its ID.
    ...
    Returns:
        DeleteResponse object if successfully deleted, None otherwise
    """
    url = f"{BASE_URL}/v1/vector_stores/{vector_store_id}"

    try:
        status_code, response_data = await async_make_request("DELETE", url)
        if status_code == 200 and isinstance(response_data, dict):
            try:
                # Assuming API returns e.g. {"id": vs_id, "object": "vector_store", "deleted": True}
                return DeleteResponse.model_validate(response_data)
            except Exception as e:
                logger.error(
                    f"Delete vector store {vector_store_id} succeeded but failed to parse response: {e}. Data: {response_data}"
                )
                return None
        elif status_code == 204:  # Handle No Content for successful delete
            return DeleteResponse(id=vector_store_id, object_field="vector_store", deleted=True)
        elif status_code == 404:
            return None
        elif status_code == 200 and isinstance(response_data, str):
            logger.error(
                f"Delete vector store failed: Server returned 200 but response was not valid JSON. VSID: {vector_store_id}. Content: {response_data}"
            )
            return None
        elif status_code != 200:
            logger.error(
                f"Delete vector store for {vector_store_id} returned unhandled status {status_code}. Data: {response_data}"
            )
            return None
        return None
    except Exception as e:
        logger.error(f"Error deleting vector store {vector_store_id}: {str(e)}")
        return None


async def async_join_files_to_vectorstore(
    vector_store_id: str, file_ids: list[str]
) -> Vectorstore | None:  # Changed return type
    """
    Asynchronously join files to an existing vector store.
    ...
    Returns:
        Vectorstore object containing updated vector store details or None if failed
    """
    url = f"{BASE_URL}/v1/vector_stores/{vector_store_id}"
    payload = {"join_file_ids": file_ids}

    try:
        status_code, response_data = await async_make_request("POST", url, json_payload=payload)
        if status_code == 200 and isinstance(response_data, dict):
            try:
                return Vectorstore.model_validate(response_data)  # API likely returns updated VS object
            except Exception as e:
                logger.error(
                    f"Join files to VS {vector_store_id} succeeded but failed to parse response: {e}. Data: {response_data}"
                )
                return None
        elif status_code == 200 and isinstance(response_data, str):
            logger.error(
                f"Join files to vector store failed: Server returned 200 but response was not valid JSON. VSID: {vector_store_id}. Content: {response_data}"
            )
            return None
        elif status_code != 200:
            logger.error(
                f"Join files to vector store for {vector_store_id} returned unhandled status {status_code}. Data: {response_data}"
            )
            return None
        return None
    except Exception as e:
        logger.error(f"Error joining files to vector store {vector_store_id}: {str(e)}")
        return None


async def async_get_vectorstore_summary(
    vector_store_id: str, model: str = "qwen-max", max_tokens: int = 1000
) -> VectorStoreSummary | None:  # Changed return type
    """
    Asynchronously get vector store summary.
    ...
    Returns:
        VectorStoreSummary object containing summary information or None if failed
    """
    url = f"{BASE_URL}/v1/vector_stores/{vector_store_id}/summary"
    params = {"model": model, "max_tokens": max_tokens}

    try:
        status_code, response_data = await async_make_request("GET", url, params=params)
        if status_code == 200 and isinstance(response_data, dict):
            try:
                return VectorStoreSummary.model_validate(response_data)
            except Exception as e:
                logger.error(
                    f"Get VS summary for {vector_store_id} succeeded but failed to parse response: {e}. Data: {response_data}"
                )
                return None
        elif status_code == 404:
            return None
        elif status_code == 200 and isinstance(response_data, str):
            logger.error(
                f"Get vector store summary failed: Server returned 200 but response was not valid JSON. VSID: {vector_store_id}. Content: {response_data}"
            )
            return None
        elif status_code != 200:
            logger.error(
                f"Get vector store summary for {vector_store_id} returned unhandled status {status_code}. Data: {response_data}"
            )
            return None
        return None
    except Exception as e:
        logger.error(f"Error getting vector store summary for {vector_store_id}: {str(e)}")
        return None


async def async_modify_vectorstore(
    vector_store_id: str,
    name: str = None,
    description: str = None,
    metadata: dict[str, str] = None,
    expires_after: int = None,
    join_file_ids: list[str] = None,
    left_file_ids: list[str] = None,
) -> Vectorstore | None:
    """
    Asynchronously modify an existing vector store.

    Args:
        vector_store_id: The ID of the vector store to modify
        name: Optional new name for the vector store
        description: Optional new description for the vector store
        metadata: Optional new metadata key-value pairs
        expires_after: Optional new expiration policy (seconds)
        join_file_ids: Optional list of file IDs to add to the vector store
        left_file_ids: Optional list of file IDs to remove from the vector store

    Returns:
        Vectorstore object with updated information or None if modification failed
    """
    url = f"{BASE_URL}/v1/vector_stores/{vector_store_id}"
    payload = {}

    # Add non-None parameters to payload
    if name is not None:
        payload["name"] = name
    if description is not None:
        payload["description"] = description
    if metadata is not None:
        payload["metadata"] = metadata
    if expires_after is not None:
        payload["expires_after"] = expires_after
    if join_file_ids is not None:
        payload["join_file_ids"] = join_file_ids
    if left_file_ids is not None:
        payload["left_file_ids"] = left_file_ids

    if not payload:
        logger.error("No update parameters provided for vector store modification")
        return None

    try:
        status_code, response_data = await async_make_request("POST", url, json_payload=payload)
        if status_code == 200 and isinstance(response_data, dict):
            try:
                return Vectorstore.model_validate(response_data)
            except Exception as e:
                logger.error(
                    f"Vector store modification for {vector_store_id} succeeded but failed to parse response: {e}. Data: {response_data}"
                )
                return None
        elif status_code == 200 and isinstance(response_data, str):
            logger.error(
                f"Vector store modification failed: Server returned 200 but response was not valid JSON. VSID: {vector_store_id}. Content: {response_data}"
            )
            return None
        elif status_code == 404:
            logger.error(f"Vector store {vector_store_id} not found")
            return None
        elif status_code != 200:
            logger.error(
                f"Vector store modification for {vector_store_id} returned unhandled status {status_code}. Data: {response_data}"
            )
            return None
        return None
    except Exception as e:
        logger.error(f"Error modifying vector store {vector_store_id}: {str(e)}")
        return None
