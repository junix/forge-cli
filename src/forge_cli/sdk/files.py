import asyncio
import mimetypes
from pathlib import Path

import aiohttp
from loguru import logger

from .config import BASE_URL


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
                    logger.warning(f"File with ID {file_id} not found")
                    return None
                elif response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Fetch file failed with status {response.status}: {error_text}")
                    return None

                result = await response.json()
                return result
    except Exception as e:
        logger.error(f"Error fetching file: {str(e)}")
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
        async with aiohttp.ClientSession() as session:
            async with session.delete(url) as response:
                if response.status == 404:
                    logger.warning(f"File with ID {file_id} not found")
                    return False
                elif response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Delete file failed with status {response.status}: {error_text}")
                    return False

                result = await response.json()
                return result.get("deleted", False)
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        return False
