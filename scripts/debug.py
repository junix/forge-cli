#!/usr/bin/env python3
"""
Debug client script for Knowledge Forge API using SDK.

This script sends test requests to the server using the typed SDK API and displays responses
in a human-friendly format. It supports different types of requests to test various functionality:
- Plain chat (default)
- File search
- Web search
- File reader

The goal is to see server responses in a readable format to help debug API behavior.

Tool Choice Examples:
- Auto (default): --tool-choice auto
- None (no tools): --tool-choice none
- Required (must use a tool): --tool-choice required
- Specific function: --tool-choice '{"type": "function", "name": "search_documents"}'
- Hosted tools: --tool-choice '{"type": "file_search"}'
                --tool-choice '{"type": "web_search_preview"}'
                --tool-choice '{"type": "code_interpreter"}'
"""

import argparse

from loguru import logger

# Import SDK functions
from forge_cli.sdk import (
    astream_typed_response,
    create_file_search_tool,
    create_typed_request,
    create_web_search_tool,
)

# Default IDs for testing
DEFAULT_VECTOR_STORE_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
DEFAULT_FILE_ID = "8b0474ad-b156-4117-ad85-ca2cbcdd7afd"  # yxt.pdf on di
DEFAULT_FILE_ID = "9a7b86c4-470c-404d-8def-86d58e529555"  # yxt.pdf on local
DEFAULT_FILE_ID = "f8e5d7c6-b9a8-4321-9876-543210abcdef"


def print_section_header(title: str):
    """Print a beautiful section header."""
    logger.info("=" * 80)
    logger.info(f"🔍 {title}")
    logger.info("=" * 80)


def log_request_details(request_data: dict):
    """Log request details in a structured way."""
    # Use bind for structured request logging
    logger.bind(
        model=request_data.get("model"),
        effort=request_data.get("effort"),
        tools_count=len(request_data.get("tools", [])),
        tool_choice=request_data.get("tool_choice"),
        request_payload=request_data,
    ).debug("📤 Request")

    # Also show human-readable summary
    logger.info("📤 Request Details:")
    logger.info(f"   Model: {request_data.get('model')}")
    logger.info(f"   Effort: {request_data.get('effort')}")
    logger.info(f"   Tools: {len(request_data.get('tools', []))}")
    if "tool_choice" in request_data:
        logger.info(f"   Tool Choice: {request_data.get('tool_choice')}")


async def handle_typed_stream(request):
    """Handle typed streaming response and display them in a human-friendly way."""
    logger.info("🔄 Starting Typed Stream Processing")

    event_count = 0

    try:
        async for event_type, response_snapshot in astream_typed_response(request):
            event_count += 1

            # Use loguru bind for structured logging
            logger.bind(
                index=event_count, event=event_type, response_id=response_snapshot.id if response_snapshot else None
            ).info("📡 Stream Event")

            # Log event data in a human-friendly way
            log_event_data(event_type, response_snapshot, event_count)

            # Stop on final done event
            if event_type == "response.done":
                break

    except Exception as e:
        logger.error(f"Error in stream processing: {e}")

    logger.info(f"✅ Typed Stream Completed - Total events: {event_count}")


def log_event_data(event_type: str, response_snapshot, event_number: int):
    """Log event data in a structured and readable way."""
    if not response_snapshot:
        logger.info(f"📊 {event_type}: No response data")
        return

    # Extract key information based on event type
    if event_type == "response.created":
        logger.info("🆕 Response Created:")
        logger.info(f"   ID: {response_snapshot.id}")
        logger.info(f"   Model: {response_snapshot.model}")
        logger.info(f"   Status: {response_snapshot.status}")

    elif event_type == "response.reasoning_summary_text.delta":
        # Extract reasoning text if available
        reasoning_text = ""
        if hasattr(response_snapshot, "output") and response_snapshot.output:
            for item in response_snapshot.output:
                if hasattr(item, "type") and item.type == "reasoning":
                    if hasattr(item, "summary") and item.summary:
                        for summary_item in item.summary:
                            if hasattr(summary_item, "type") and summary_item.type == "summary_text":
                                reasoning_text = getattr(summary_item, "text", "")
                                break

        if reasoning_text:
            # Truncate long reasoning for readability
            display_text = reasoning_text[:200] + "..." if len(reasoning_text) > 200 else reasoning_text
            tokens_used = getattr(response_snapshot.usage, "total_tokens", 0) if response_snapshot.usage else 0
            logger.info("🧠 Reasoning Update:")
            logger.info(f"   Length: {len(reasoning_text)} chars")
            logger.info(f"   Tokens: {tokens_used}")
            logger.info(f"   Preview: {display_text}")

    elif event_type == "response.file_search_call.searching":
        logger.info("🔍 File Search Started")

    elif event_type == "response.file_search_call.completed":
        logger.info("✅ File Search Completed")

    elif event_type == "response.web_search_call.searching":
        logger.info("🌐 Web Search Started")

    elif event_type == "response.web_search_call.completed":
        logger.info("✅ Web Search Completed")

    elif event_type == "response.output_text.delta":
        # Extract output text if available
        text_content = ""
        if hasattr(response_snapshot, "output_text"):
            text_content = response_snapshot.output_text

        if text_content:
            preview = text_content[:100] + "..." if len(text_content) > 100 else text_content
            logger.info(f"📝 Text Output: {preview}")

    else:
        # For other events, show key fields
        logger.info(f"📊 {event_type}:")
        if hasattr(response_snapshot, "id"):
            logger.info(f"   ID: {response_snapshot.id}")
        if hasattr(response_snapshot, "status"):
            logger.info(f"   Status: {response_snapshot.status}")
        if hasattr(response_snapshot, "usage") and response_snapshot.usage:
            logger.info(f"   Usage: {response_snapshot.usage}")


async def send_plain_chat_request(model="qwen3-235b-a22b", effort="low", tool_choice=None, query=None):
    """Send a simple chat message without any tool usage using typed SDK."""
    print_section_header("PLAIN CHAT REQUEST")

    # Use custom query or default message
    content = query or "Hello! This is a debug test message. Please respond with a simple greeting."

    try:
        # Create typed request
        request = create_typed_request(
            input_messages=content,
            model=model,
            effort=effort,
            store=True,
            tool_choice=tool_choice,
        )

        log_request_details(request.model_dump(exclude_none=True))

        # Handle streaming response
        await handle_typed_stream(request)

    except Exception as e:
        logger.error(f"💥 Request Exception: {str(e)}")


async def send_file_search_request(
    vector_store_id=None,
    model="qwen3-235b-a22b",
    effort="low",
    tool_choice=None,
    query=None,
):
    """Send a request that triggers file search functionality using typed SDK."""
    print_section_header("FILE SEARCH REQUEST")

    if vector_store_id is None:
        vector_store_id = DEFAULT_VECTOR_STORE_ID

    # Use custom query or default message
    content = query or "Search for information about machine learning algorithms and explain the key concepts."

    try:
        # Create file search tool
        file_search_tool = create_file_search_tool(
            vector_store_ids=[vector_store_id],
            max_num_results=5,
        )

        # Create typed request
        request = create_typed_request(
            input_messages=content,
            model=model,
            effort=effort,
            store=True,
            tools=[file_search_tool],
            tool_choice=tool_choice,
        )

        log_request_details(request.model_dump(exclude_none=True))

        # Handle streaming response
        await handle_typed_stream(request)

    except Exception as e:
        logger.error(f"💥 Request Exception: {str(e)}")


async def send_web_search_request(model="qwen3-235b-a22b", effort="low", tool_choice=None, query=None):
    """Send a request that triggers web search functionality using typed SDK."""
    print_section_header("WEB SEARCH REQUEST")

    # Use custom query or default message
    content = query or "What are the latest developments in artificial intelligence? Please search for recent news."

    try:
        # Create web search tool
        web_search_tool = create_web_search_tool()

        # Create typed request
        request = create_typed_request(
            input_messages=content,
            model=model,
            effort=effort,
            store=True,
            tools=[web_search_tool],
            tool_choice=tool_choice,
        )

        log_request_details(request.model_dump(exclude_none=True))

        # Handle streaming response
        await handle_typed_stream(request)

    except Exception as e:
        logger.error(f"💥 Request Exception: {str(e)}")


async def send_file_reader_request(file_id=None, model="qwen3-235b-a22b", effort="low", tool_choice=None, query=None):
    """Send a request that triggers file reading functionality using typed SDK."""
    print_section_header("FILE READER REQUEST")

    if file_id is None:
        file_id = DEFAULT_FILE_ID

    # Use custom query or default message
    text_content = query or "出差南京可以报销多少？"

    try:
        # Create typed request with file input
        request = create_typed_request(
            input_messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_file", "file_id": file_id},
                        {"type": "input_text", "text": text_content},
                    ],
                }
            ],
            model=model,
            effort=effort,
            store=True,
            tool_choice=tool_choice,
        )

        log_request_details(request.model_dump(exclude_none=True))

        # Handle streaming response
        await handle_typed_stream(request)

    except Exception as e:
        logger.error(f"💥 Request Exception: {str(e)}")


async def send_multi_tool_request(
    tasks,
    vector_store_id=None,
    file_id=None,
    model="qwen3-235b-a22b",
    effort="low",
    tool_choice=None,
    query=None,
):
    """Send a request that uses multiple tools together using typed SDK."""
    print_section_header("MULTI-TOOL REQUEST")

    # Use custom query or generate based on tasks
    if not query:
        if "file-search" in tasks and "web-search" in tasks:
            query = "Compare information from the documents with current web information on artificial intelligence advancements."
        elif "file-reader" in tasks and "file-search" in tasks:
            query = "Analyze the uploaded file and search for related information in the vector store."
        else:
            query = "Provide comprehensive analysis using all available tools."

    try:
        tools = []
        input_messages = query

        # Add tools based on tasks
        if "file-search" in tasks:
            if vector_store_id is None:
                vector_store_id = DEFAULT_VECTOR_STORE_ID
            file_search_tool = create_file_search_tool(
                vector_store_ids=[vector_store_id],
                max_num_results=5,
            )
            tools.append(file_search_tool)
            logger.info(f"   📚 Added file search tool with vector store: {vector_store_id}")

        if "web-search" in tasks:
            web_search_tool = create_web_search_tool()
            tools.append(web_search_tool)
            logger.info("   🌐 Added web search tool")

        # Handle file reader differently - it goes in the input content
        if "file-reader" in tasks:
            if file_id is None:
                file_id = DEFAULT_FILE_ID
            # Convert content to array format for file input
            input_messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_file", "file_id": file_id},
                        {"type": "input_text", "text": query},
                    ],
                }
            ]
            logger.info(f"   📄 Added file reader with file ID: {file_id}")

        # Create typed request
        request = create_typed_request(
            input_messages=input_messages,
            model=model,
            effort=effort,
            store=True,
            tools=tools if tools else None,
            tool_choice=tool_choice,
        )

        log_request_details(request.model_dump(exclude_none=True))

        # Handle streaming response
        await handle_typed_stream(request)

    except Exception as e:
        logger.error(f"💥 Request Exception: {str(e)}")


async def main():
    """Main function to handle command line arguments and execute the appropriate test."""
    parser = argparse.ArgumentParser(
        description="Debug client for Knowledge Forge API using typed SDK - sends test requests and displays responses"
    )
    parser.add_argument(
        "--task",
        "-t",
        nargs="*",
        choices=["file-search", "web-search", "file-reader"],
        help="Type(s) of request to send. Can specify multiple tasks for multi-tool usage. If not specified, sends a plain chat request.",
    )
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        help="Custom query to send with the request",
    )
    parser.add_argument(
        "--vector-store-id",
        default=DEFAULT_VECTOR_STORE_ID,
        help=f"Vector store ID to use for file search (default: {DEFAULT_VECTOR_STORE_ID})",
    )
    parser.add_argument(
        "--file-id",
        default=DEFAULT_FILE_ID,
        help=f"File ID to use for file reader (default: {DEFAULT_FILE_ID})",
    )
    parser.add_argument(
        "--effort",
        "-e",
        choices=["dev", "low", "medium", "high"],
        default="low",
        help="Effort level for the request (default: low)",
    )
    parser.add_argument(
        "--model",
        "-m",
        default="qwen3-235b-a22b",
        help="Model name to use for the request (default: qwen3-235b-a22b)",
    )
    parser.add_argument(
        "--tool-choice",
        "-tc",
        help=(
            "Tool choice parameter. Options: "
            "'auto' (model decides), "
            "'none' (no tools), "
            "'required' (must use tool), "
            '\'{"type": "function", "name": "tool_name"}\' (specific function), '
            '\'{"type": "file_search"}\' (hosted tool). '
            "Hosted tools: file_search, web_search_preview, computer_use_preview, code_interpreter, mcp, image_generation"
        ),
    )

    args = parser.parse_args()

    # Parse tool_choice argument
    tool_choice = None
    if args.tool_choice:
        if args.tool_choice in ["auto", "none", "required"]:
            tool_choice = args.tool_choice
        else:
            # Try to parse as JSON for specific tool choice
            try:
                tool_choice = json.loads(args.tool_choice)
                # Validate structure
                if not isinstance(tool_choice, dict):
                    logger.error("Invalid tool_choice format. Must be a JSON object.")
                    return

                # Check for function tool
                if tool_choice.get("type") == "function":
                    if "name" not in tool_choice:
                        logger.error("Function tool choice requires 'name' field")
                        return
                # Check for hosted tools
                elif tool_choice.get("type") in [
                    "file_search",
                    "web_search_preview",
                    "computer_use_preview",
                    "code_interpreter",
                    "mcp",
                    "image_generation",
                ]:
                    # Valid hosted tool, no additional fields required
                    pass
                else:
                    logger.error(f"Unknown tool type: {tool_choice.get('type')}")
                    logger.error(
                        "Valid types: function, file_search, web_search_preview, computer_use_preview, code_interpreter, mcp, image_generation"
                    )
                    return
            except json.JSONDecodeError:
                logger.error(f"Invalid tool_choice value: {args.tool_choice}")
                logger.error("Valid values: 'auto', 'none', 'required', or JSON object for specific tool")
                return

    logger.info("🚀 Knowledge Forge API Debug Client (Typed SDK)")

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
    if tool_choice is not None:
        logger.info(f"   Tool Choice: {tool_choice}")

    # Execute the appropriate test based on task type
    if args.task and len(args.task) > 1:
        # Multi-tool request
        await send_multi_tool_request(
            args.task,
            args.vector_store_id,
            args.file_id,
            args.model,
            args.effort,
            tool_choice,
            args.query,
        )
    elif args.task and len(args.task) == 1:
        # Single tool request
        task = args.task[0]
        if task == "file-search":
            await send_file_search_request(args.vector_store_id, args.model, args.effort, tool_choice, args.query)
        elif task == "web-search":
            await send_web_search_request(args.model, args.effort, tool_choice, args.query)
        elif task == "file-reader":
            await send_file_reader_request(args.file_id, args.model, args.effort, tool_choice, args.query)
    else:
        # Plain chat request
        await send_plain_chat_request(args.model, args.effort, tool_choice, args.query)

    logger.info("🎉 Debug session completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
