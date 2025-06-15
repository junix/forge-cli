from typing import Any

from forge_cli.response._types import Response
# Import async_create_response from .response for example_response_usage
from .response import async_create_response


def print_file_results(upload_result: dict[str, str | int | float | bool | list | dict]) -> None:
    """Print formatted file upload results."""
    if upload_result:
        print(f"File uploaded: {upload_result.get('filename')}")
        print(f"File ID: {upload_result.get('id')}")
        print(f"Size: {upload_result.get('bytes')} bytes")
        if upload_result.get("task_id"):
            print(f"Processing task: {upload_result.get('task_id')}")


def print_vectorstore_results(result: dict[str, str | int | float | bool | list | dict], query: str) -> None:
    """Print formatted vector store query results."""
    if result and result.get("data"): # Ensure 'data' key exists and is not empty
        print(f"Found {len(result['data'])} results for query: '{query}'")
        for i, item in enumerate(result["data"], 1):
            print(f"\nResult #{i}:")
            print(f"  Score: {item.get('score', 'N/A'):.4f}")
            print(f"  File: {item.get('filename', 'N/A')} (ID: {item.get('file_id', 'N/A')})")
            # Ensure content is a list and not empty before accessing
            content_list = item.get("content")
            if content_list and isinstance(content_list, list) and len(content_list) > 0:
                content_item = content_list[0] # Take the first content item
                if isinstance(content_item, dict):
                    content_text = content_item.get("text", "")
                    if content_text:
                        if len(content_text) > 100:
                            content_text = content_text[:100] + "..."
                        print(f"  Content: {content_text}")
    elif result:
        print(f"No data found in results for query: '{query}'")
    else:
        print(f"No results for query: '{query}'")


def print_response_results(result: Response | dict[str, str | int | float | bool | list | dict]) -> None:
    """Print formatted response results."""
    if isinstance(result, Response):
        # Use the output_text property for Response objects
        if result.output_text:
            print(f"Assistant: {result.output_text}")
        else:
            print("Assistant: [No text output]")
    elif result and "output" in result and isinstance(result["output"], list):
        # Fallback for dict format
        assistant_output_found = False
        for msg in result["output"]:
            if isinstance(msg, dict) and msg.get("role") == "assistant" and "content" in msg:
                assistant_output_found = True
                content = msg["content"]
                if isinstance(content, list): # Content can be a list of parts (e.g. text, tool_call)
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            print(f"Assistant: {item.get('text', '')}")
                        # Could add handling for other content types if needed
                elif isinstance(content, str): # Content can also be a simple string
                    print(f"Assistant: {content}")
        if not assistant_output_found:
             print("Assistant: [No assistant output in the expected format]")
    else:
        print("Assistant: [Invalid or empty result format]")


def get_response_text(response: Response) -> str:
    """Extract text content from a Response object."""
    return response.output_text if response and response.output_text else ""


def has_tool_calls(response: Response) -> bool:
    """Check if the response contains any tool calls."""
    if not response or not response.output:
        return False
    return any(
        hasattr(item, "type") and ("tool_call" in item.type or item.type == "function_call")
        for item in response.output
    )


def get_tool_call_results(response: Response) -> list[dict[str, Any]]:
    """Extract tool call results from a Response object."""
    results = []
    if not response or not response.output:
        return results
    for item in response.output:
        if hasattr(item, "type") and ("tool_call" in item.type or item.type == "function_call"):
            if hasattr(item, "results") and item.results: # 'results' is the attribute in the Pydantic model
                results.extend(item.results)
    return results


def get_citation_count(response: Response) -> int:
    """Count the number of citations in a Response object."""
    if not response:
        return 0
    citation_items = response.collect_citable_items()
    return len(citation_items)


def has_uncompleted_tool_calls(response: Response) -> bool:
    """Check if the response has any uncompleted tool calls."""
    if not response:
        return False
    return len(response.uncompleted_tool_calls) > 0


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
    # Create a response with file search
    # Note: This example assumes a vector store 'vs_example' exists.
    # In a real scenario, you'd create or ensure this vector store exists.
    print("Attempting to create a response with file search (ensure 'vs_example' vector store exists)...")
    response = await async_create_response(
        input_messages="What information is available about machine learning?",
        model="qwen-max-latest", # Using a common model name
        tools=[{"type": "file_search", "file_search": {"vector_store_ids": ["vs_example"], "max_num_results": 10}}],
    )

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
    if hasattr(response, 'contain_non_internal_tool_call'): # Check if method exists
        print(f"Contains non-internal tools: {response.contain_non_internal_tool_call()}")

    # Citation management
    citable_items = response.collect_citable_items()
    print(f"Found {len(citable_items)} citable items")

    # Install citation IDs for display
    # The method name in Response model is install_citation_id (singular)
    citations_with_ids = response.install_citation_id()
    print(f"Assigned citation IDs to {len(citations_with_ids)} items")

    # Get actual citations used in the response
    referenced_citations = response.get_cited_annotations()
    print(f"Actually referenced: {len(referenced_citations)} citations")

    # Content compression examples
    if len(citable_items) > 0:
        print("\n--- Content Compression ---")
        # Remove duplicates
        deduplicated_response = response.deduplicate() # Returns a new Response object
        print(f"After deduplication: {len(deduplicated_response.collect_citable_items())} citable items")

        # Remove unreferenced chunks
        # The method is compact_retrieve_chunks and takes a strategy string
        compact_response = response.compact_retrieve_chunks(strategy="nonrefed") # Returns new Response
        print(f"After removing unreferenced (nonrefed strategy): {len(compact_response.collect_citable_items())} citable items")

    # Usage statistics
    if response.usage:
        print("\n--- Usage Statistics ---")
        print(f"Token usage: {response.usage.total_tokens} total")
        print(f"Input tokens: {response.usage.input_tokens}")
        print(f"Output tokens: {response.usage.output_tokens}")
    else:
        print("\nNo usage statistics available.")

    # Brief representation for debugging
    # The method is brief_repr and takes a strategy string
    if hasattr(response, 'brief_repr'): # Check if method exists
        brief_response = response.brief_repr(strategy="smart") # Returns new Response
        print(f"\nBrief representation (smart strategy) created with {len(brief_response.output)} output items")

    print("\n--- Example Usage End ---")
