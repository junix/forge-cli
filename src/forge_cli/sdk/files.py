from __future__ import annotations

import asyncio
import mimetypes
from pathlib import Path

import aiohttp  # Keep for FormData
from loguru import logger

from .config import BASE_URL
from .http_client import async_make_request

# Import new types
from .types import DeleteResponse, File, TaskStatus  # Updated imports


async def async_upload_file(
    path: str = None,
    url: str = None,
    name: str = None,
    file_type: str = None,
    purpose: str = "general",
    custom_id: str = None,
    id: str = None,  # Alias for custom_id
    md5: str = None,
    request_id: str = None,
    skip_exists: bool = False,
    parse_options: dict[str, str] = None,
) -> File:  # Changed return type
    """
    Asynchronously upload a file to the Knowledge Forge API and return the file details.

    Args:
        path: Path to the file to upload (mutually exclusive with url)
        url: URL of the file to download and upload (mutually exclusive with path)
        name: Name of the file (required when using url)
        file_type: MIME type of the file (required when using url)
        purpose: The intended purpose of the file (e.g., "qa", "general")
        custom_id: Optional custom ID for the file (deprecated, use 'id')
        id: Optional custom UUID for the file (must be valid UUID format)
        md5: Optional MD5 hash of the file (32-character hex string)
        request_id: Optional request ID for tracking
        skip_exists: Whether to skip upload if file with same MD5 exists
        parse_options: Optional dict of parsing options. Keys: "abstract", "summary",
                      "outline", "keywords", "contexts", "graph", "vectorize",
                      "outline_json_style", "fast_mode". Values: "enable" or "disable".

    Returns:
        File object containing file details including id and task_id

    Raises:
        ValueError: If invalid parameters are provided
        FileNotFoundError: If file path doesn't exist
    """
    # Validate parameters
    if not path and not url:
        raise ValueError("Must provide either 'path' or 'url'")
    
    if path and url:
        raise ValueError("Cannot provide both 'path' and 'url'")
    
    if url and (not name or not file_type):
        raise ValueError("When using 'url', must provide 'name' and 'file_type'")

    # Handle backward compatibility for custom_id
    file_id = id or custom_id

    api_url = f"{BASE_URL}/v1/files"
    form_data = aiohttp.FormData()

    if path:
        # File upload
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        content_type, _ = mimetypes.guess_type(str(file_path))
        if content_type is None:
            content_type = "application/octet-stream"

        form_data.add_field(
            "file",
            open(file_path, "rb"),
            filename=file_path.name,
            content_type=content_type,
        )
    else:
        # URL upload
        form_data.add_field("url", url)
        form_data.add_field("name", name)
        form_data.add_field("file_type", file_type)

    # Common fields
    form_data.add_field("purpose", purpose)

    if file_id:
        form_data.add_field("id", file_id)

    if md5:
        form_data.add_field("md5", md5)

    if request_id:
        form_data.add_field("request_id", request_id)

    if skip_exists:
        form_data.add_field("skip_exists", "true")

    if parse_options:
        import json
        form_data.add_field("parse_options", json.dumps(parse_options))

    status_code, response_data = await async_make_request("POST", api_url, data=form_data)

    if status_code == 200 and isinstance(response_data, dict):
        try:
            return File.model_validate(response_data)  # Parse to File model
        except Exception as e:  # Handle Pydantic validation error
            logger.error(
                f"Failed to parse successful file upload response into File model: {e}. Response: {response_data}"
            )
            raise Exception(f"Upload succeeded but failed to parse response. Error: {e}")
    elif status_code == 200 and isinstance(response_data, str):
        raise Exception(
            f"Upload failed: Server returned 200 but response was not valid JSON. Response: {response_data}"
        )
    else:
        # Errors are raised by async_make_request or this is a fallback
        raise Exception(f"Upload failed with status {status_code}. Response: {response_data}")


async def async_check_task_status(task_id: str) -> TaskStatus:  # Changed return type
    """
    Check the status of a task by its ID.

    Args:
        task_id: The ID of the task to check

    Returns:
        TaskStatus object containing task status information
    """
    url = f"{BASE_URL}/v1/tasks/{task_id}"

    status_code, response_data = await async_make_request("GET", url)

    if status_code == 200 and isinstance(response_data, dict):
        try:
            return TaskStatus.model_validate(response_data)  # Parse to TaskStatus model
        except Exception as e:  # Handle Pydantic validation error
            logger.error(
                f"Failed to parse successful task status response into TaskStatus model: {e}. Response: {response_data}"
            )
            raise Exception(f"Task status check succeeded but failed to parse response. Error: {e}")
    elif status_code == 200 and isinstance(response_data, str):
        raise Exception(
            f"Task status check failed: Server returned 200 but response was not valid JSON. Response: {response_data}"
        )
    else:
        raise Exception(f"Task status check failed with status {status_code}. Response: {response_data}")


async def async_wait_for_task_completion(
    task_id: str, poll_interval: int = 2, max_attempts: int = 60
) -> TaskStatus:  # Changed return type
    """
    Wait for a task to complete by polling its status.

    Args:
        task_id: The ID of the task to wait for
        poll_interval: How often to check the task status (in seconds)
        max_attempts: Maximum number of status checks before giving up

    Returns:
        TaskStatus object containing the final task status
    """
    attempts = 0

    while attempts < max_attempts:
        task_status_obj = await async_check_task_status(task_id)  # Already returns TaskStatus

        # Check if task is complete based on the status field of TaskStatus model
        if task_status_obj.status in ["completed", "failed", "cancelled"]:  # Added "cancelled"
            return task_status_obj

        await asyncio.sleep(poll_interval)
        attempts += 1

    raise TimeoutError(
        f"Task {task_id} did not complete within the allowed time. Last status: {task_status_obj.status if 'task_status_obj' in locals() else 'unknown'}"
    )


async def async_fetch_file(file_id: str) -> File | None:  # Changed return type
    """
    Asynchronously fetch file information by its ID.

    Args:
        file_id: The ID of the file to fetch

    Returns:
        File object containing file details or None if not found
    """
    url = f"{BASE_URL}/v1/files/{file_id}/content"  # Assuming content endpoint returns full File object

    try:
        status_code, response_data = await async_make_request("GET", url)

        if status_code == 200 and isinstance(response_data, dict):
            try:
                return File.model_validate(response_data)  # Parse to File model
            except Exception as e:
                logger.error(
                    f"Fetch file {file_id} succeeded but failed to parse response into File model: {e}. Response: {response_data}"
                )
                return None  # Or raise, depending on desired strictness
        elif status_code == 404:
            return None
        elif status_code == 200 and isinstance(response_data, str):
            logger.error(
                f"Fetch file {file_id} failed: Server returned 200 but response was not valid JSON. Content: {response_data}"
            )
            return None
        else:
            logger.error(f"Fetch file {file_id} returned unhandled status {status_code}. Data: {response_data}")
            return None  # Or raise exception
    except Exception as e:
        logger.error(f"Error fetching file {file_id}: {str(e)}")
        return None


async def async_fetch_document_content(document_id: str):
    """
    Asynchronously fetch document content by its ID.
    This function handles the actual API response structure for document content.

    Args:
        document_id: The ID of the document to fetch

    Returns:
        DocumentResponse object containing document details or None if not found
    """
    from .file_types import DocumentResponse

    url = f"{BASE_URL}/v1/files/{document_id}/content"

    try:
        status_code, response_data = await async_make_request("GET", url)

        if status_code == 200 and isinstance(response_data, dict):
            try:
                return DocumentResponse.model_validate(response_data)
            except Exception as e:
                logger.error(
                    f"Fetch document {document_id} succeeded but failed to parse response: {e}. Response keys: {list(response_data.keys()) if response_data else 'None'}"
                )
                return None
        elif status_code == 404:
            return None
        elif status_code == 200 and isinstance(response_data, str):
            logger.error(
                f"Fetch document {document_id} failed: Server returned 200 but response was not valid JSON. Content: {response_data}"
            )
            return None
        else:
            logger.error(f"Fetch document {document_id} returned unhandled status {status_code}. Data: {response_data}")
            return None
    except Exception as e:
        logger.error(f"Error fetching document {document_id}: {str(e)}")
        return None


async def async_delete_file(file_id: str) -> DeleteResponse | None:  # Changed return type
    """
    Asynchronously delete a file by its ID.

    Args:
        file_id: The ID of the file to delete

    Returns:
        DeleteResponse object if successfully deleted, None otherwise
    """
    url = f"{BASE_URL}/v1/files/{file_id}"

    try:
        status_code, response_data = await async_make_request("DELETE", url)

        if status_code == 200 and isinstance(response_data, dict):
            try:
                # Assuming the response_data for a successful delete matches DeleteResponse structure
                # e.g., {"id": "file_id", "object": "file", "deleted": True}
                return DeleteResponse.model_validate(response_data)
            except Exception as e:
                logger.error(
                    f"Delete file {file_id} succeeded but failed to parse response into DeleteResponse model: {e}. Response: {response_data}"
                )
                # Fallback if parsing fails but operation might have succeeded.
                # Consider if API guarantees this structure or if a simpler True/False based on status is safer.
                # For now, returning None if parsing fails for a 200.
                return None
        elif status_code == 404:
            return None  # File not found, so not deleted, but not an error in the call itself
        elif status_code == 200 and isinstance(response_data, str):  # Should be JSON
            logger.error(
                f"Delete file {file_id} failed: Server returned 200 but response was not valid JSON. Content: {response_data}"
            )
            return None
        # For other non-200 status codes, async_make_request is expected to raise an exception.
        # If it doesn't, or if we need to handle specific codes (e.g., 204 No Content for delete),
        # that logic would be here. A 204 might mean success but no body to parse.
        # For 204 No Content specifically:
        # elif status_code == 204:
        #     return DeleteResponse(id=file_id, object_field="file", deleted=True)
        else:
            # This path implies an unhandled status or an issue if async_make_request didn't raise.
            logger.error(f"Delete file {file_id} returned unhandled status {status_code}. Data: {response_data}")
            return None
    except Exception as e:
        logger.error(f"Error deleting file {file_id}: {str(e)}")
        return None


async def async_update_document(
    document_id: str,
    title: str = None,
    author: str = None,
    read_progress: float = None,
    bookmarks: list[int] = None,
    highlights: list[str] = None,
    notes: list[str] = None,
    related_docs: list[str] = None,
    is_favorite: bool = None,
    owner: str = None,
    permissions: list[str] = None,
    metadata: dict = None,
    vector_store_ids: list[str] = None,
) -> dict | None:
    """
    Asynchronously update a document's metadata and properties.

    Args:
        document_id: The ID of the document to update
        title: Optional new title for the document
        author: Optional new author for the document
        read_progress: Optional reading progress (0.0 to 1.0)
        bookmarks: Optional list of bookmark page numbers
        highlights: Optional list of highlighted text snippets
        notes: Optional list of notes
        related_docs: Optional list of related document IDs
        is_favorite: Optional favorite status
        owner: Optional owner identifier
        permissions: Optional list of permissions
        metadata: Optional metadata dictionary
        vector_store_ids: Optional list of vector store IDs

    Returns:
        Dictionary with update confirmation or None if update failed
    """
    url = f"{BASE_URL}/v1/files/{document_id}/content"
    payload = {}

    # Add non-None parameters to payload
    if title is not None:
        payload["title"] = title
    if author is not None:
        payload["author"] = author
    if read_progress is not None:
        payload["read_progress"] = read_progress
    if bookmarks is not None:
        payload["bookmarks"] = bookmarks
    if highlights is not None:
        payload["highlights"] = highlights
    if notes is not None:
        payload["notes"] = notes
    if related_docs is not None:
        payload["related_docs"] = related_docs
    if is_favorite is not None:
        payload["is_favorite"] = is_favorite
    if owner is not None:
        payload["owner"] = owner
    if permissions is not None:
        payload["permissions"] = permissions
    if metadata is not None:
        payload["metadata"] = metadata
    if vector_store_ids is not None:
        payload["vector_store_ids"] = vector_store_ids

    if not payload:
        logger.error("No update parameters provided for document update")
        return None

    try:
        status_code, response_data = await async_make_request("POST", url, json_payload=payload)
        if status_code == 200 and isinstance(response_data, dict):
            return response_data
        elif status_code == 200 and isinstance(response_data, str):
            logger.error(
                f"Document update failed: Server returned 200 but response was not valid JSON. Doc ID: {document_id}. Content: {response_data}"
            )
            return None
        elif status_code == 404:
            logger.error(f"Document {document_id} not found")
            return None
        elif status_code != 200:
            logger.error(
                f"Document update for {document_id} returned unhandled status {status_code}. Data: {response_data}"
            )
            return None
        return None
    except Exception as e:
        logger.error(f"Error updating document {document_id}: {str(e)}")
        return None
