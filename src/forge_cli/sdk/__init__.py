"""
Knowledge Forge API SDK Client

This SDK provides methods to interact with the Knowledge Forge API for managing files,
vector stores, and generating responses.
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
    async_create_response,
    async_fetch_response,
    create_stream_callback,
    validate_input_messages,
)
from .typed_api import (
    astream_typed_response,
    async_create_typed_response,
    create_file_search_tool,
    create_typed_request,
    create_web_search_tool,
)
from .utils import (
    example_response_usage,
    get_citation_count,
    get_response_text,
    get_tool_call_results,
    has_tool_calls,
    has_uncompleted_tool_calls,
    print_file_results,
    print_response_results,
    print_vectorstore_results,
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
    "BASE_URL",
    "async_upload_file",
    "async_check_task_status",
    "async_wait_for_task_completion",
    "async_fetch_file",
    "async_delete_file",
    "async_create_vectorstore",
    "async_query_vectorstore",
    "async_get_vectorstore",
    "async_delete_vectorstore",
    "async_join_files_to_vectorstore",
    "async_get_vectorstore_summary",
    "validate_input_messages",
    "create_stream_callback",
    "async_create_response",
    "async_fetch_response",
    "async_create_typed_response",
    "astream_typed_response",
    "create_typed_request",
    "create_file_search_tool",
    "create_web_search_tool",
    "print_file_results",
    "print_vectorstore_results",
    "print_response_results",
    "get_response_text",
    "has_tool_calls",
    "get_tool_call_results",
    "get_citation_count",
    "has_uncompleted_tool_calls",
    "example_response_usage",
]
