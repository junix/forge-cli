from typing import Any

from forge_cli.response._types import Response

# Import typed API functions for example_response_usage
from .typed_api import async_create_typed_response, create_file_search_tool, create_typed_request
from .types import File


def print_file_results(upload_result: File) -> None:
    """Print formatted file upload results."""
    if upload_result:
        print(f"File uploaded: {upload_result.filename}")
        print(f"File ID: {upload_result.id}")
        print(f"Size: {upload_result.bytes} bytes")
        if upload_result.task_id:
            print(f"Processing task: {upload_result.task_id}")


def has_tool_calls(response: Response) -> bool:
    """Check if the response contains any tool calls."""
    if not response or not response.output:
        return False
    return any(
        hasattr(item, "type") and ("tool_call" in item.type or item.type == "function_call") for item in response.output
    )


def has_uncompleted_tool_calls(response: Response) -> bool:
    """Check if the response has any uncompleted tool calls."""
    if not response or not response.output:
        return False

    # Check for tool calls that are not completed
    for item in response.output:
        if hasattr(item, "type") and ("tool_call" in item.type or item.type == "function_call"):
            if hasattr(item, "status") and (item.status is None or item.status in ["in_progress", "incomplete"]):
                return True
    return False


async def example_response_usage() -> None:
    """
    Example function demonstrating Response object features.

    This function shows how to:
    - Create a response with tools
    - Extract text content
    - Work with citations
    - Analyze tool calls
    - Use compression features
    """
    # Create a response with file search using typed API
    # Note: This example assumes a vector store 'vs_example' exists.
    # In a real scenario, you'd create or ensure this vector store exists.
    print(
        "Attempting to create a response with file search using typed API (ensure 'vs_example' vector store exists)..."
    )

    # Create typed request with file search tool
    request = create_typed_request(
        input_messages="What information is available about machine learning?",
        model="qwen-max-latest",  # Using a common model name
        tools=[create_file_search_tool(vector_store_ids=["vs_example"], max_search_results=10)],
    )

    response = await async_create_typed_response(request)

    if not response:
        print("Failed to create response for example_response_usage.")
        return

    print(f"\n--- Response Details ({response.id if response.id else 'N/A'}) ---")
    # Basic text extraction
    print(f"Response text: {response.output_text if response.output_text else '[No text output]'}")
    print(f"Status: {response.status}")
    print(f"Model: {response.model}")

    # Tool call analysis
    print(f"Has tool calls: {has_tool_calls(response)}")
    print(f"Has uncompleted tool calls: {has_uncompleted_tool_calls(response)}")
    if hasattr(response, "contain_non_internal_tool_call"):  # Check if method exists
        print(f"Contains non-internal tools: {response.contain_non_internal_tool_call()}")

    # Citation management
    citable_items = response.collect_citable_items()
    print(f"Found {len(citable_items)} citable items")

    # Install citation IDs for display
    citations_with_ids = response.install_citation_id()
    print(f"Assigned citation IDs to {len(citations_with_ids)} items")

    # Get actual citations used in the response
    referenced_citations = response.get_cited_annotations()
    print(f"Actually referenced: {len(referenced_citations)} citations")

    # Content compression examples
    if len(citable_items) > 0:
        print("\n--- Content Compression ---")
        # Remove duplicates
        deduplicated_response = response.deduplicate()  # Returns a new Response object
        print(f"After deduplication: {len(deduplicated_response.collect_citable_items())} citable items")

        # Remove unreferenced chunks - using correct parameter name 'mode'
        compact_response = response.compact_retrieve_chunks(mode="nonrefed")  # Returns new Response
        print(
            f"After removing unreferenced (nonrefed mode): {len(compact_response.collect_citable_items())} citable items"
        )

    # Usage statistics
    if response.usage:
        print("\n--- Usage Statistics ---")
        print(f"Token usage: {response.usage.total_tokens} total")
        print(f"Input tokens: {response.usage.input_tokens}")
        print(f"Output tokens: {response.usage.output_tokens}")
    else:
        print("\nNo usage statistics available.")

    print("\n--- Example Usage End ---")
