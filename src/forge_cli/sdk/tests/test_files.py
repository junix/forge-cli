from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from forge_cli.sdk.config import BASE_URL  # For constructing URLs if needed in mocks

# Assuming Pydantic models and SDK functions are accessible via these imports
# Adjust paths if necessary based on actual project structure for tests
from forge_cli.sdk.files import (
    async_check_task_status,
    async_delete_file,
    async_fetch_file,
    async_upload_file,
    async_wait_for_task_completion,
)
from forge_cli.sdk.types import DeleteResponse, File, TaskStatus


# A fixture for the mock http client
@pytest_asyncio.fixture
async def mock_http_client():
    with patch("forge_cli.sdk.files.async_make_request", new_callable=AsyncMock) as mock_make_request:
        yield mock_make_request


# --- Tests for async_upload_file ---
@pytest.mark.asyncio
async def test_async_upload_file_success(mock_http_client):
    mock_response_data = {
        "id": "file_123",
        "object": "file",
        "custom_id": "my_custom_file_id",
        "filename": "test_file.txt",
        "bytes": 1024,
        "content_type": "text/plain",
        "md5": "abcdef123456",
        "purpose": "general",
        "status": "uploaded",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "task_id": "task_abc123",
    }
    mock_http_client.return_value = (200, mock_response_data)

    # Create a dummy file for upload
    with open("dummy_test_file.txt", "w") as f:
        f.write("This is a test file.")

    result = await async_upload_file(path="dummy_test_file.txt", purpose="general", custom_id="my_custom_file_id")

    assert isinstance(result, File)
    assert result.id == "file_123"
    assert result.filename == "test_file.txt"  # This will be dummy_test_file.txt from the FormData
    assert result.custom_id == "my_custom_file_id"
    assert result.task_id == "task_abc123"

    # Clean up dummy file
    import os

    os.remove("dummy_test_file.txt")

    # Check if async_make_request was called correctly
    expected_url = f"{BASE_URL}/v1/files"
    # FormData is tricky to assert directly, focus on URL and method
    mock_http_client.assert_called_once()
    call_args = mock_http_client.call_args
    assert call_args[0][0] == "POST"
    assert call_args[0][1] == expected_url
    # We can check for specific fields in FormData if aiohttp.FormData allows easy inspection
    # For now, checking the presence of 'data' argument which should be FormData
    assert "data" in call_args[1]


# --- Tests for async_check_task_status ---
@pytest.mark.asyncio
async def test_async_check_task_status_success(mock_http_client):
    mock_response_data = {
        "id": "task_abc123",
        "object": "task",
        "type": "file_processing",
        "status": "completed",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "result": {"file_id": "file_123", "message": "Processed successfully"},
        "resource_id": "file_123",
    }
    mock_http_client.return_value = (200, mock_response_data)

    task_id = "task_abc123"
    result = await async_check_task_status(task_id)

    assert isinstance(result, TaskStatus)
    assert result.id == task_id
    assert result.status == "completed"
    assert result.result["file_id"] == "file_123"

    expected_url = f"{BASE_URL}/v1/tasks/{task_id}"
    mock_http_client.assert_called_once_with("GET", expected_url)


# --- Tests for async_delete_file ---
@pytest.mark.asyncio
async def test_async_delete_file_success_200(mock_http_client):
    file_id_to_delete = "file_xyz789"
    mock_response_data = {
        "id": file_id_to_delete,
        "object": "file",  # Make sure this matches the Pydantic model's alias if used
        "deleted": True,
    }
    mock_http_client.return_value = (200, mock_response_data)

    result = await async_delete_file(file_id_to_delete)

    assert isinstance(result, DeleteResponse)
    assert result.id == file_id_to_delete
    assert result.deleted is True
    assert result.object_field == "file"  # Check aliased field

    expected_url = f"{BASE_URL}/v1/files/{file_id_to_delete}"
    mock_http_client.assert_called_once_with("DELETE", expected_url)


@pytest.mark.asyncio
async def test_async_delete_file_success_204(mock_http_client):
    file_id_to_delete = "file_abc555"
    # For 204, response_data might be None or an empty dict/str depending on http_client
    # The refactored sdk/files.py has specific handling for 204 to construct DeleteResponse
    mock_http_client.return_value = (204, None)

    result = await async_delete_file(file_id_to_delete)

    assert isinstance(result, DeleteResponse)
    assert result.id == file_id_to_delete
    assert result.deleted is True
    assert result.object_field == "file"

    expected_url = f"{BASE_URL}/v1/files/{file_id_to_delete}"
    mock_http_client.assert_called_once_with("DELETE", expected_url)


@pytest.mark.asyncio
async def test_async_fetch_file_success(mock_http_client):
    file_id_to_fetch = "file_tuv001"
    mock_response_data = {
        "id": file_id_to_fetch,
        "object": "file",
        "filename": "fetched_file.dat",
        "bytes": 2048,
        "content_type": "application/octet-stream",
        "purpose": "storage",
        "status": "available",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    mock_http_client.return_value = (200, mock_response_data)

    result = await async_fetch_file(file_id_to_fetch)

    assert isinstance(result, File)
    assert result.id == file_id_to_fetch
    assert result.bytes == 2048

    expected_url = f"{BASE_URL}/v1/files/{file_id_to_fetch}/content"
    mock_http_client.assert_called_once_with("GET", expected_url)


@pytest.mark.asyncio
async def test_async_fetch_file_not_found(mock_http_client):
    file_id_to_fetch = "file_nonexistent"
    mock_http_client.return_value = (404, None)  # Or some error dict API might return

    result = await async_fetch_file(file_id_to_fetch)
    assert result is None

    expected_url = f"{BASE_URL}/v1/files/{file_id_to_fetch}/content"
    mock_http_client.assert_called_once_with("GET", expected_url)


# Test for async_wait_for_task_completion
@pytest.mark.asyncio
async def test_async_wait_for_task_completion_completes_immediately(mock_http_client):
    task_id = "task_completed_fast"
    final_status_data = {
        "id": task_id,
        "object": "task",
        "type": "some_operation",
        "status": "completed",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "result": {"data": "done"},
    }
    # Mock async_check_task_status directly or its underlying async_make_request
    # Here, we mock async_make_request which is called by async_check_task_status
    mock_http_client.return_value = (200, final_status_data)

    result = await async_wait_for_task_completion(task_id, poll_interval=0.1, max_attempts=3)

    assert isinstance(result, TaskStatus)
    assert result.status == "completed"
    assert result.id == task_id
    mock_http_client.assert_called_once()  # Should be called once as it completes immediately


@pytest.mark.asyncio
async def test_async_wait_for_task_completion_polls_then_completes(mock_http_client):
    task_id = "task_polls_then_done"
    in_progress_data = {
        "id": task_id,
        "object": "task",
        "type": "some_operation",
        "status": "in_progress",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    completed_data = {
        "id": task_id,
        "object": "task",
        "type": "some_operation",
        "status": "completed",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "result": {"final_data": "all_good"},
    }
    # Simulate sequence: in_progress, in_progress, completed
    mock_http_client.side_effect = [(200, in_progress_data), (200, in_progress_data), (200, completed_data)]

    result = await async_wait_for_task_completion(task_id, poll_interval=0.01, max_attempts=5)  # Small poll interval

    assert isinstance(result, TaskStatus)
    assert result.status == "completed"
    assert result.id == task_id
    assert mock_http_client.call_count == 3


@pytest.mark.asyncio
async def test_async_wait_for_task_completion_timeout(mock_http_client):
    task_id = "task_times_out"
    in_progress_data = {
        "id": task_id,
        "object": "task",
        "type": "some_operation",
        "status": "in_progress",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    mock_http_client.return_value = (200, in_progress_data)  # Always returns in_progress

    with pytest.raises(TimeoutError) as excinfo:
        await async_wait_for_task_completion(task_id, poll_interval=0.01, max_attempts=3)

    assert task_id in str(excinfo.value)
    assert mock_http_client.call_count == 3


# TODO: Add tests for error cases (API returns non-200 status, Pydantic validation failures)
# For Pydantic validation failure, you'd mock async_make_request to return (200, malformed_dict)
# and assert that the SDK function raises an Exception or returns None as designed.
