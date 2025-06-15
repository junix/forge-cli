from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from forge_cli.sdk.config import BASE_URL
from forge_cli.sdk.types import (
    DeleteResponse,
    Vectorstore,
    VectorStoreQueryResponse,
    VectorStoreQueryResultItem,
    VectorStoreSummary,
)

# Assuming Pydantic models and SDK functions are accessible via these imports
from forge_cli.sdk.vectorstore import (
    async_create_vectorstore,
    async_delete_vectorstore,
    async_get_vectorstore,
    async_get_vectorstore_summary,
    async_join_files_to_vectorstore,
    async_query_vectorstore,
)


# A fixture for the mock http client
@pytest_asyncio.fixture
async def mock_http_client():
    # Important: Patch the correct path for async_make_request used by vectorstore.py
    with patch("forge_cli.sdk.vectorstore.async_make_request", new_callable=AsyncMock) as mock_make_request:
        yield mock_make_request


# --- Test Data Helper ---
def create_mock_vectorstore_data(vs_id: str, name: str, status: str = "active") -> dict:
    now = datetime.now(UTC)
    return {
        "id": vs_id,
        "object": "vector_store",  # API response field name
        "name": name,
        "description": "Test Vector Store",
        "file_ids": ["file_1", "file_2"],
        "metadata": {"env": "test"},
        "status": status,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "bytes": 10240,
        "file_counts": {  # Assuming FileCounts model fields
            "in_progress": 0,
            "completed": 2,
            "failed": 0,
            "cancelled": 0,
            "total": 2,
        },
        "task_id": "task_vs_create_123",
        "last_task_status": "completed",
        "last_processed_at": now.isoformat(),
    }


# --- Tests for async_create_vectorstore ---
@pytest.mark.asyncio
async def test_async_create_vectorstore_success(mock_http_client):
    vs_name = "MyTestVS"
    mock_vs_data = create_mock_vectorstore_data("vs_new_123", vs_name, status="creating")
    mock_http_client.return_value = (200, mock_vs_data)

    result = await async_create_vectorstore(name=vs_name, description="Test Vector Store", file_ids=["file_1"])

    assert isinstance(result, Vectorstore)
    assert result.id == "vs_new_123"
    assert result.name == vs_name
    assert result.status == "creating"  # As per mock data
    assert result.file_counts.completed == 2

    expected_url = f"{BASE_URL}/v1/vector_stores"
    mock_http_client.assert_called_once()
    call_args = mock_http_client.call_args
    assert call_args[0][0] == "POST"
    assert call_args[0][1] == expected_url
    assert call_args[1]["json_payload"]["name"] == vs_name


# --- Tests for async_get_vectorstore ---
@pytest.mark.asyncio
async def test_async_get_vectorstore_success(mock_http_client):
    vs_id = "vs_existing_456"
    mock_vs_data = create_mock_vectorstore_data(vs_id, "ExistingVS")
    mock_http_client.return_value = (200, mock_vs_data)

    result = await async_get_vectorstore(vector_store_id=vs_id)

    assert isinstance(result, Vectorstore)
    assert result.id == vs_id
    assert result.name == "ExistingVS"

    expected_url = f"{BASE_URL}/v1/vector_stores/{vs_id}"
    mock_http_client.assert_called_once_with("GET", expected_url)


# --- Tests for async_query_vectorstore ---
@pytest.mark.asyncio
async def test_async_query_vectorstore_success(mock_http_client):
    vs_id = "vs_query_789"
    query_text = "What is AI?"
    mock_query_item_data = {
        "id": "chunk_abc",
        "vector_store_id": vs_id,
        "file_id": "file_source_1",
        "score": 0.95,
        "text": "AI is artificial intelligence.",
        "metadata": {"page": 1},
        "created_at": datetime.now(UTC).isoformat(),
    }
    mock_response_data = {
        "object": "list",
        "data": [mock_query_item_data],
        "vector_store_id": vs_id,
        "query": query_text,
        "top_k": 1,
    }
    mock_http_client.return_value = (200, mock_response_data)

    result = await async_query_vectorstore(vector_store_id=vs_id, query=query_text, top_k=1)

    assert isinstance(result, VectorStoreQueryResponse)
    assert result.vector_store_id == vs_id
    assert len(result.data) == 1
    assert isinstance(result.data[0], VectorStoreQueryResultItem)
    assert result.data[0].id == "chunk_abc"
    assert result.data[0].score == 0.95

    expected_url = f"{BASE_URL}/v1/vector_stores/{vs_id}/search"
    mock_http_client.assert_called_once()
    call_args = mock_http_client.call_args
    assert call_args[1]["json_payload"]["query"] == query_text


# --- Tests for async_delete_vectorstore ---
@pytest.mark.asyncio
async def test_async_delete_vectorstore_success_200(mock_http_client):
    vs_id_to_delete = "vs_del_200"
    mock_response_data = {"id": vs_id_to_delete, "object": "vector_store", "deleted": True}
    mock_http_client.return_value = (200, mock_response_data)

    result = await async_delete_vectorstore(vs_id_to_delete)

    assert isinstance(result, DeleteResponse)
    assert result.id == vs_id_to_delete
    assert result.deleted is True
    assert result.object_field == "vector_store"

    expected_url = f"{BASE_URL}/v1/vector_stores/{vs_id_to_delete}"
    mock_http_client.assert_called_once_with("DELETE", expected_url)


@pytest.mark.asyncio
async def test_async_delete_vectorstore_success_204(mock_http_client):
    vs_id_to_delete = "vs_del_204"
    mock_http_client.return_value = (204, None)  # 204 No Content

    result = await async_delete_vectorstore(vs_id_to_delete)

    assert isinstance(result, DeleteResponse)
    assert result.id == vs_id_to_delete
    assert result.deleted is True
    assert result.object_field == "vector_store"

    expected_url = f"{BASE_URL}/v1/vector_stores/{vs_id_to_delete}"
    mock_http_client.assert_called_once_with("DELETE", expected_url)


# --- Tests for async_join_files_to_vectorstore ---
@pytest.mark.asyncio
async def test_async_join_files_to_vectorstore_success(mock_http_client):
    vs_id = "vs_join_files"
    files_to_join = ["file_x", "file_y"]
    # API likely returns the updated vector store object
    mock_updated_vs_data = create_mock_vectorstore_data(vs_id, "VSWithJoinedFiles")
    mock_updated_vs_data["file_ids"].extend(files_to_join)  # Simulate files added
    mock_http_client.return_value = (200, mock_updated_vs_data)

    result = await async_join_files_to_vectorstore(vector_store_id=vs_id, file_ids=files_to_join)

    assert isinstance(result, Vectorstore)
    assert result.id == vs_id
    assert "file_x" in result.file_ids
    assert "file_y" in result.file_ids

    expected_url = f"{BASE_URL}/v1/vector_stores/{vs_id}"
    mock_http_client.assert_called_once()
    call_args = mock_http_client.call_args
    assert call_args[1]["json_payload"]["join_file_ids"] == files_to_join


# --- Tests for async_get_vectorstore_summary ---
@pytest.mark.asyncio
async def test_async_get_vectorstore_summary_success(mock_http_client):
    vs_id = "vs_summary_1"
    mock_summary_data = {
        "vector_store_id": vs_id,
        "summary_text": "This is a summary of the vector store.",
        "model_used": "qwen-max",
        "created_at": datetime.now(UTC).isoformat(),
        "token_count": 50,
    }
    mock_http_client.return_value = (200, mock_summary_data)

    result = await async_get_vectorstore_summary(vector_store_id=vs_id)

    assert isinstance(result, VectorStoreSummary)
    assert result.vector_store_id == vs_id
    assert result.summary_text == "This is a summary of the vector store."
    assert result.model_used == "qwen-max"

    expected_url = f"{BASE_URL}/v1/vector_stores/{vs_id}/summary"
    mock_http_client.assert_called_once()
    call_args = mock_http_client.call_args
    assert call_args[1]["params"]["model"] == "qwen-max"  # Check default model


# TODO: Add tests for error cases (API non-200, Pydantic validation failures, etc.)
# and edge cases (e.g., empty query results).
