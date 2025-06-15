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

# Note: Legacy dict-based response functions are deprecated
# Use typed_api functions instead for new code
from .response import (
    async_fetch_response,  # Keep this as it returns typed Response
    validate_input_messages,  # Keep this utility function
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
    # Legacy response operations (kept for compatibility)
    "async_fetch_response",  # Returns typed Response
    "validate_input_messages",  # Utility function
    # Utility functions
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
