import asyncio
import mimetypes
from pathlib import Path

import aiohttp # Keep for FormData, can be removed if FormData is handled differently or http_client handles it
from loguru import logger

from .config import BASE_URL
from .http_client import async_make_request


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

    status_code, response_data = await async_make_request("POST", url, data=form_data)

    if status_code == 200 and isinstance(response_data, dict):
        return response_data
    # Non-200 errors including JSON parsing failures for 200 status are raised by async_make_request
    # If response_data is str for 200, it means JSON parsing failed in async_make_request
    elif status_code == 200 and isinstance(response_data, str):
         raise Exception(f"Upload failed: Server returned 200 but response was not valid JSON. Response: {response_data}")
    # For other status codes, async_make_request would have raised an exception.
    # If it didn't (e.g. a case not covered), raise a generic error.
    else:
        raise Exception(f"Upload failed with status {status_code}. Response: {response_data}")


async def async_check_task_status(task_id: str) -> dict[str, str | int | float | bool | list | dict]:
    """
    Check the status of a task by its ID.

    Args:
        task_id: The ID of the task to check

    Returns:
        Dict containing task status information
    """
    url = f"{BASE_URL}/v1/tasks/{task_id}"

    status_code, response_data = await async_make_request("GET", url)

    if status_code == 200 and isinstance(response_data, dict):
        return response_data
    elif status_code == 200 and isinstance(response_data, str):
        raise Exception(f"Task status check failed: Server returned 200 but response was not valid JSON. Response: {response_data}")
    else:
        # Errors are raised by async_make_request, but as a fallback:
        raise Exception(f"Task status check failed with status {status_code}. Response: {response_data}")


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
    url = f"{BASE_URL}/v1/files/{file_id}/content"

    try:
        status_code, response_data = await async_make_request("GET", url)

        if status_code == 200 and isinstance(response_data, dict):
            return response_data
        elif status_code == 404:
            # Handled by async_make_request logging, no need to log again here.
            return None
        elif status_code == 200 and isinstance(response_data, str):
            # This case implies JSON parsing failed in async_make_request for a 200 response
            logger.error(f"Fetch file {file_id} failed: Server returned 200 but response was not valid JSON. Content: {response_data}")
            return None
        else:
            # For other status codes, async_make_request would have raised an exception.
            # If we reach here for other non-200 cases, it's unexpected.
            # Specific logging for non-200/404 already done by async_make_request if it didn't raise.
            # However, async_make_request is designed to raise for unhandled non-200/404.
            # This path should ideally not be hit if async_make_request works as specified.
            logger.error(f"Fetch file {file_id} returned unhandled status {status_code}. Data: {response_data}")
            return None
    except Exception as e:
        # Exceptions from async_make_request (like network errors or specific non-200s) are caught here.
        logger.error(f"Error fetching file {file_id}: {str(e)}")
        return None


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
        status_code, response_data = await async_make_request("DELETE", url)

        if status_code == 200 and isinstance(response_data, dict):
            return response_data.get("deleted", False)
        elif status_code == 404:
            # Handled by async_make_request logging.
            return False
        elif status_code == 200 and isinstance(response_data, str):
            logger.error(f"Delete file {file_id} failed: Server returned 200 but response was not valid JSON. Content: {response_data}")
            return False
        else:
            # async_make_request should raise for other error statuses.
            # This path implies an issue if reached for non-200/404 without an exception.
            logger.error(f"Delete file {file_id} returned unhandled status {status_code}. Data: {response_data}")
            return False
    except Exception as e:
        # Captures exceptions raised by async_make_request
        logger.error(f"Error deleting file {file_id}: {str(e)}")
        return False
