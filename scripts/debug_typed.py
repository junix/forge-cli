#!/usr/bin/env python3
"""
Debug client script using typed API for Knowledge Forge.

This script demonstrates the use of typed Request/Response objects with the streaming API.
It shows how to work with Response snapshots during streaming (per ADR-004).
"""

import argparse
import asyncio
import os

# Add parent directory to path to import forge_cli
import sys
from pathlib import Path

from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))

from forge_cli.response._types import FileSearchTool, Request, Response, WebSearchTool
from forge_cli.response._types.web_search_tool import UserLocation
from forge_cli.sdk import astream_typed_response, create_typed_request

# Use environment variable for server URL if available
BASE_URL = os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999")

# Default IDs for testing
DEFAULT_VECTOR_STORE_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
DEFAULT_FILE_ID = "f8e5d7c6-b9a8-4321-9876-543210abcdef"


def print_section_header(title: str):
    """Print a beautiful section header."""
    logger.info("=" * 80)
    logger.info(f"🔍 {title}")
    logger.info("=" * 80)


def log_response_snapshot(event_type: str, response: Response | None, event_number: int):
    """Log Response object information from streaming snapshot."""
    if response is None:
        logger.bind(index=event_number, event=event_type).info("📡 Event (no response data)")
        return

    # Log event with response data
    logger.bind(
        index=event_number,
        event=event_type,
        response_id=response.id,
        status=response.status,
        model=response.model,
    ).info("📡 Response Snapshot")

    # Log specific details based on event type
    if event_type == "response.created":
        logger.info("🆕 Response Created:")
        logger.info(f"   ID: {response.id}")
        logger.info(f"   Model: {response.model}")
        logger.info(f"   Status: {response.status}")

    elif event_type == "response.reasoning_summary_text.delta":
        # Extract reasoning using Response methods
        reasoning_items = [item for item in response.output if hasattr(item, "type") and item.type == "reasoning"]
        if reasoning_items:
            logger.info("🧠 Reasoning Update:")
            for item in reasoning_items:
                if hasattr(item, "summary"):
                    for summary_item in item.summary:
                        if hasattr(summary_item, "text"):
                            text = summary_item.text
                            preview = text[:200] + "..." if len(text) > 200 else text
                            logger.info(f"   Length: {len(text)} chars")
                            logger.info(f"   Preview: {preview}")

    elif event_type == "response.file_search_call.searching":
        # Find file search tool calls
        tool_calls = [item for item in response.output if hasattr(item, "type") and item.type == "file_search_call"]
        if tool_calls:
            logger.info("🔍 File Search Started:")
            for call in tool_calls:
                if hasattr(call, "queries"):
                    logger.info(f"   Queries: {call.queries}")

    elif event_type == "response.file_search_call.completed":
        # Count search results using Response methods
        tool_calls = [item for item in response.output if hasattr(item, "type") and item.type == "file_search_call"]
        total_results = 0
        for call in tool_calls:
            if hasattr(call, "results") and call.results:
                total_results += len(call.results)
        logger.info(f"✅ File Search Completed - Found {total_results} results")

    elif event_type == "response.output_text.delta":
        # Use Response's output_text property
        if response.output_text:
            preview = response.output_text[:100] + "..." if len(response.output_text) > 100 else response.output_text
            logger.info(f"📝 Text Output: {preview}")

    elif event_type == "response.completed":
        logger.info("✅ Response Completed:")
        logger.info(f"   Status: {response.status}")
        if response.usage:
            logger.info(f"   Total Tokens: {response.usage.total_tokens}")
            logger.info(f"   Input Tokens: {response.usage.input_tokens}")
            logger.info(f"   Output Tokens: {response.usage.output_tokens}")

        # Check for citations
        citation_count = len(response.collect_citable_items())
        if citation_count > 0:
            logger.info(f"   Citations Available: {citation_count}")

        # Final text output
        if response.output_text:
            logger.info("📄 Final Output:")
            logger.info(f"{response.output_text}")


async def stream_with_typed_api(request: Request, debug: bool = False):
    """Stream a response using typed Request/Response objects."""
    logger.info("🔄 Starting Typed SSE Stream Processing")

    event_count = 0
    final_response = None

    try:
        async for event_type, response in astream_typed_response(request, debug=debug):
            event_count += 1
            log_response_snapshot(event_type, response, event_count)

            # Store the final response
            if event_type == "response.completed" and response:
                final_response = response

            # Stop on done event
            if event_type == "done":
                break

    except Exception as e:
        logger.error(f"💥 Streaming Exception: {str(e)}")

    logger.info(f"✅ SSE Stream Completed - Total events: {event_count}")

    # Process final response with advanced features
    if final_response:
        logger.info("\n" + "=" * 80)
        logger.info("📊 FINAL RESPONSE ANALYSIS")
        logger.info("=" * 80)

        # Install citation IDs
        citable_items = final_response.install_citation_id()
        if citable_items:
            logger.info(f"📚 Installed {len(citable_items)} citation IDs")

        # Check for tool calls
        if any(hasattr(item, "type") and "tool_call" in item.type for item in final_response.output):
            logger.info("🛠️  Response contains tool calls")

        # Get compressed version
        compressed = final_response.compact()
        if compressed and compressed.get("removed_chunks", 0) > 0:
            logger.info(f"🗜️  Compression removed {compressed['removed_chunks']} duplicate chunks")

    return final_response


async def send_plain_chat_request(model="qwen-max-latest", effort="low", query=None, debug=False):
    """Send a simple chat message using typed API."""
    print_section_header("TYPED PLAIN CHAT REQUEST")

    # Create typed request
    content = query or "Hello! This is a debug test using typed API. Please respond with a simple greeting."
    request = create_typed_request(input_messages=content, model=model, effort=effort, store=True)

    logger.info("📤 Typed Request:")
    logger.info(f"   Model: {request.model}")
    logger.info(f"   Effort: {request.effort}")
    logger.info(f"   Message: {content}")

    await stream_with_typed_api(request, debug=debug)


async def send_file_search_request(
    vector_store_id=None, model="qwen-max-latest", effort="low", query=None, debug=False
):
    """Send a file search request using typed API."""
    print_section_header("TYPED FILE SEARCH REQUEST")

    if vector_store_id is None:
        vector_store_id = DEFAULT_VECTOR_STORE_ID

    content = query or "Search for information about machine learning algorithms and explain the key concepts."

    # Create typed request with file search tool
    request = create_typed_request(
        input_messages=content,
        model=model,
        effort=effort,
        tools=[FileSearchTool(type="file_search", vector_store_ids=[vector_store_id], max_num_results=5)],
        store=True,
    )

    logger.info("📤 Typed Request:")
    logger.info(f"   Model: {request.model}")
    logger.info(f"   Effort: {request.effort}")
    logger.info(f"   Vector Store: {vector_store_id}")
    logger.info(f"   Tools: {len(request.tools)}")
    logger.info(f"   Query: {content}")

    response = await stream_with_typed_api(request, debug=debug)

    # Demonstrate citation features
    if response and response.output_text:
        cited_annotations = response.get_cited_annotations()
        if cited_annotations:
            logger.info(f"\n📎 Found {len(cited_annotations)} referenced citations in the response")


async def send_web_search_request(model="qwen-max-latest", effort="low", query=None, debug=False):
    """Send a web search request using typed API."""
    print_section_header("TYPED WEB SEARCH REQUEST")

    content = query or "What are the latest developments in artificial intelligence? Please search for recent news."

    # Create typed request with web search tool
    request = create_typed_request(
        input_messages=content,
        model=model,
        effort=effort,
        tools=[
            WebSearchTool(
                type="web_search",
                search_context_size="medium",
                user_location=UserLocation(type="approximate", country="US", city="San Francisco"),
            )
        ],
        store=True,
    )

    logger.info("📤 Typed Request:")
    logger.info(f"   Model: {request.model}")
    logger.info(f"   Effort: {request.effort}")
    logger.info("   Tools: Web Search")
    logger.info(f"   Query: {content}")

    await stream_with_typed_api(request, debug=debug)


async def send_multi_tool_request(
    tasks, vector_store_id=None, model="qwen-max-latest", effort="low", query=None, debug=False
):
    """Send a multi-tool request using typed API."""
    print_section_header("TYPED MULTI-TOOL REQUEST")

    # Build tools list
    tools = []

    if "file-search" in tasks:
        if vector_store_id is None:
            vector_store_id = DEFAULT_VECTOR_STORE_ID
        tools.append(FileSearchTool(type="file_search", vector_store_ids=[vector_store_id], max_num_results=5))
        logger.info(f"   📚 Added file search tool with vector store: {vector_store_id}")

    if "web-search" in tasks:
        tools.append(
            WebSearchTool(
                type="web_search",
                search_context_size="medium",
                user_location=UserLocation(type="approximate", country="US", city="San Francisco"),
            )
        )
        logger.info("   🌐 Added web search tool")

    # Generate query based on tools
    if not query:
        if "file-search" in tasks and "web-search" in tasks:
            query = "Compare information from the documents with current web information on artificial intelligence advancements."
        else:
            query = "Provide comprehensive analysis using all available tools."

    # Create typed request
    request = create_typed_request(input_messages=query, model=model, effort=effort, tools=tools, store=True)

    logger.info("📤 Typed Request:")
    logger.info(f"   Model: {request.model}")
    logger.info(f"   Effort: {request.effort}")
    logger.info(f"   Tools: {len(request.tools)}")
    logger.info(f"   Query: {query}")

    response = await stream_with_typed_api(request, debug=debug)

    # Demonstrate advanced Response features
    if response:
        # Check for non-internal tool calls
        if response.contain_non_internal_tool_call():
            logger.info("\n⚠️  Response contains external tool calls that need execution")

        # Show brief representation
        brief = response.brief_repr(mode="smart")
        logger.info(f"\n📊 Brief representation has {len(brief.output)} output items")


async def main():
    """Main function to handle command line arguments and execute tests."""
    parser = argparse.ArgumentParser(
        description="Debug client using typed API for Knowledge Forge - demonstrates Response objects in streaming"
    )
    parser.add_argument(
        "--task",
        "-t",
        nargs="*",
        choices=["file-search", "web-search"],
        help="Type(s) of request to send. Can specify multiple for multi-tool usage.",
    )
    parser.add_argument("--query", "-q", type=str, help="Custom query to send with the request")
    parser.add_argument(
        "--vector-store-id",
        default=DEFAULT_VECTOR_STORE_ID,
        help=f"Vector store ID for file search (default: {DEFAULT_VECTOR_STORE_ID})",
    )
    parser.add_argument(
        "--effort", "-e", choices=["dev", "low", "medium", "high"], default="low", help="Effort level (default: low)"
    )
    parser.add_argument("--model", "-m", default="qwen-max-latest", help="Model name (default: qwen-max-latest)")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    logger.info("🚀 Knowledge Forge Typed API Debug Client")
    logger.info(f"   Server URL: {BASE_URL}")

    # Display task information
    if args.task and len(args.task) > 0:
        if len(args.task) == 1:
            logger.info(f"   Task Type: {args.task[0]}")
        else:
            logger.info(f"   Task Types: {', '.join(args.task)} (multi-tool)")
    else:
        logger.info("   Task Type: plain-chat")

    logger.info(f"   Model: {args.model}")
    logger.info(f"   Effort Level: {args.effort}")
    if args.query:
        logger.info(f"   Custom Query: {args.query}")

    # Execute the appropriate test
    if args.task and len(args.task) > 1:
        # Multi-tool request
        await send_multi_tool_request(args.task, args.vector_store_id, args.model, args.effort, args.query, args.debug)
    elif args.task and len(args.task) == 1:
        # Single tool request
        task = args.task[0]
        if task == "file-search":
            await send_file_search_request(args.vector_store_id, args.model, args.effort, args.query, args.debug)
        elif task == "web-search":
            await send_web_search_request(args.model, args.effort, args.query, args.debug)
    else:
        # Plain chat request
        await send_plain_chat_request(args.model, args.effort, args.query, args.debug)

    logger.info("\n🎉 Typed API debug session completed!")


if __name__ == "__main__":
    asyncio.run(main())
