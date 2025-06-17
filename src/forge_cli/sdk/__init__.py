"""
Knowledge Forge API SDK Client - Typed API Edition

This SDK provides typed methods to interact with the Knowledge Forge API for managing files,
vector stores, and generating responses. All APIs now use Pydantic models for type safety
and better developer experience.

Recommended usage:
- Use async_create_typed_response() and astream_typed_response() for responses
- Use create_typed_request() to build requests with type validation
- Use create_file_search_tool() and create_web_search_tool() for tools
"""

from .config import BASE_URL
from .files import (
    async_check_task_status,
    async_delete_file,
    async_fetch_file,
    async_upload_file,
    async_wait_for_task_completion,
)
from .response import (
    async_fetch_response,  # Fetch existing responses by ID - returns typed Response
)
from .typed_api import (
    astream_typed_response,
    async_create_typed_response,
    create_file_search_tool,
    create_typed_request,
    create_web_search_tool,
)
from .utils import (
    has_tool_calls,
    has_uncompleted_tool_calls,
    print_file_results,
)
from .vectorstore import (
    async_create_vectorstore,
    async_delete_vectorstore,
    async_get_vectorstore,
    async_get_vectorstore_summary,
    async_join_files_to_vectorstore,
    async_query_vectorstore,
)

__all__ = [
    # Configuration
    "BASE_URL",
    # File operations (all use typed returns)
    "async_upload_file",
    "async_check_task_status",
    "async_wait_for_task_completion",
    "async_fetch_file",
    "async_delete_file",
    # Vector store operations (all use typed returns)
    "async_create_vectorstore",
    "async_query_vectorstore",
    "async_get_vectorstore",
    "async_delete_vectorstore",
    "async_join_files_to_vectorstore",
    "async_get_vectorstore_summary",
    # Response operations - TYPED API (recommended)
    "async_create_typed_response",
    "astream_typed_response",
    "create_typed_request",
    "create_file_search_tool",
    "create_web_search_tool",
    # Response fetch operation
    "async_fetch_response",  # Fetch existing responses by ID
    # Utility functions
    "print_file_results",
    "has_tool_calls",
    "has_uncompleted_tool_calls",
    "example_response_usage",
]
