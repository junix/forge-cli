#!/usr/bin/env python3
"""
Debug client script for Knowledge Forge API.

This script sends test requests to the server and displays responses in a human-friendly format.
It supports different types of requests to test various functionality:
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
import json
import os

import requests
from logger import logger

# Use environment variable for server URL if available, otherwise default to localhost
BASE_URL = os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999")

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


def log_request_details(url: str, method: str, request_data: dict):
    """Log request details in a structured way."""
    # Use bind for structured request logging
    logger.bind(
        method=method,
        url=url,
        model=request_data.get("model"),
        effort=request_data.get("effort"),
        tools_count=len(request_data.get("tools", [])),
        tool_choice=request_data.get("tool_choice"),
        request_payload=request_data,
    ).debug("📤 Request")

    # Also show human-readable summary
    logger.info(f"� {method} {url}")
    logger.info(f"   Model: {request_data.get('model')}")
    logger.info(f"   Effort: {request_data.get('effort')}")
    logger.info(f"   Tools: {len(request_data.get('tools', []))}")
    if "tool_choice" in request_data:
        logger.info(f"   Tool Choice: {request_data.get('tool_choice')}")


def log_response_details(status_code: int, headers: dict):
    """Log response details in a structured way."""
    # Use bind for structured response logging
    logger.bind(
        status_code=status_code,
        content_type=headers.get("content-type"),
        server=headers.get("server"),
        response_headers=dict(headers),
    ).debug("📥 Response")

    # Also show human-readable summary
    logger.info("📥 Response Details:")
    logger.info(f"   Status Code: {status_code}")
    logger.info(f"   Content Type: {headers.get('content-type', 'N/A')}")
    logger.info(f"   Server: {headers.get('server', 'N/A')}")


def handle_sse_stream(response):
    """Handle Server-Sent Events stream and display them in a human-friendly way."""
    logger.info("🔄 Starting SSE Stream Processing")

    event_count = 0
    current_event_type = None

    for line in response.iter_lines():
        if not line:
            continue

        line = line.decode("utf-8")

        if line.startswith("event:"):
            current_event_type = line[6:].strip()
            event_count += 1

            # Use loguru bind for structured logging
            logger.bind(index=event_count, event=current_event_type, payload=None).info("📡 SSE Event")

            # Stop on final done event
            if current_event_type == "response.done":
                break

        elif line.startswith("data:"):
            data_str = line[5:].strip()
            if data_str and (data_str.startswith("{") or data_str.startswith("[")):
                try:
                    data = json.loads(data_str)

                    # Use loguru bind with the actual payload
                    logger.bind(index=event_count, event=current_event_type, payload=data).debug("📦 Response")

                    # Also log human-friendly summary
                    log_event_data(current_event_type, data, event_count)

                except json.JSONDecodeError:
                    truncated_data = data_str[:100] + "..." if len(data_str) > 100 else data_str
                    logger.bind(
                        index=event_count,
                        event=current_event_type,
                        payload=truncated_data,
                    ).warning("⚠️ Failed to parse JSON data")

    logger.info(f"✅ SSE Stream Completed - Total events: {event_count}")


def log_event_data(event_type: str, data: dict, event_number: int):
    """Log event data in a structured and readable way."""
    # Extract key information based on event type
    if event_type == "response.created":
        logger.info("🆕 Response Created:")
        logger.info(f"   ID: {data.get('id', 'N/A')}")
        logger.info(f"   Model: {data.get('model', 'N/A')}")
        logger.info(f"   Status: {data.get('status', 'N/A')}")

    elif event_type == "response.reasoning_summary_text.delta":
        # Extract reasoning text
        reasoning_text = extract_reasoning_text(data)
        if reasoning_text:
            # Truncate long reasoning for readability
            display_text = reasoning_text[:200] + "..." if len(reasoning_text) > 200 else reasoning_text
            tokens_used = data.get("usage", {}).get("total_tokens", 0)
            logger.info("🧠 Reasoning Update:")
            logger.info(f"   Length: {len(reasoning_text)} chars")
            logger.info(f"   Tokens: {tokens_used}")
            logger.info(f"   Preview: {display_text}")

    elif event_type == "response.file_search_call.searching":
        queries = extract_search_queries(data)
        vector_stores = extract_vector_store_ids(data)
        logger.info("🔍 File Search Started:")
        logger.info(f"   Queries: {queries}")
        logger.info(f"   Vector Stores: {vector_stores}")

    elif event_type == "response.file_search_call.completed":
        results_count = extract_search_results_count(data)
        logger.info(f"✅ File Search Completed - Found {results_count} results")

    elif event_type == "response.web_search_call.searching":
        logger.info("🌐 Web Search Started")
        # Extract queries if available
        queries = data.get("queries", [])
        if queries:
            logger.info(f"   Queries: {queries}")

    elif event_type == "response.web_search_call.completed":
        logger.info("✅ Web Search Completed")
        # Extract results count if available
        results = data.get("results", [])
        if isinstance(results, list):
            logger.info(f"   Found {len(results)} results")

    elif event_type == "response.output_text.delta":
        text_content = extract_output_text(data)
        if text_content:
            preview = text_content[:100] + "..." if len(text_content) > 100 else text_content
            logger.info(f"📝 Text Output: {preview}")

    else:
        # For other events, show key fields
        key_fields = {k: v for k, v in data.items() if k in ["id", "status", "model", "usage"] and v is not None}
        if key_fields:
            logger.info(f"📊 {event_type}:")
            for key, value in key_fields.items():
                logger.info(f"   {key}: {value}")


def extract_reasoning_text(data: dict) -> str:
    """Extract reasoning text from event data."""
    output = data.get("output", [])
    for item in output:
        if item.get("type") == "reasoning":
            summary = item.get("summary", [])
            for summary_item in summary:
                if summary_item.get("type") == "summary_text":
                    return summary_item.get("text", "")
    return ""


def extract_search_queries(data: dict) -> list:
    """Extract search queries from event data."""
    # Check various locations where queries might be stored
    if "queries" in data:
        return data["queries"]

    output = data.get("output", [])
    for item in output:
        if item.get("type") == "file_search_call":
            return item.get("queries", [])
    return []


def extract_vector_store_ids(data: dict) -> list:
    """Extract vector store IDs from event data."""
    tools = data.get("tools", [])
    for tool in tools:
        if tool.get("type") == "file_search":
            return tool.get("vector_store_ids", [])
    return []


def extract_search_results_count(data: dict) -> int:
    """Extract search results count from event data."""
    output = data.get("output", [])
    for item in output:
        if item.get("type") == "file_search_call":
            results = item.get("results")
            if isinstance(results, list):
                return len(results)
    return 0


def extract_output_text(data: dict) -> str:
    """Extract output text from event data."""
    text_data = data.get("text", {})
    if isinstance(text_data, dict):
        return text_data.get("text", "")
    elif isinstance(text_data, str):
        return text_data
    return ""


def send_plain_chat_request(model="qwen3-235b-a22b", effort="low", tool_choice=None, query=None):
    """Send a simple chat message without any tool usage."""
    print_section_header("PLAIN CHAT REQUEST")

    # Use custom query or default message
    content = query or "Hello! This is a debug test message. Please respond with a simple greeting."

    request_data = {
        "model": model,
        "effort": effort,
        "store": True,
        "input": [
            {
                "role": "user",
                "id": "debug_message_1",
                "content": content,
            }
        ],
    }

    # Add tool_choice if specified
    if tool_choice is not None:
        request_data["tool_choice"] = tool_choice

    log_request_details(f"{BASE_URL}/v1/responses", "POST", request_data)

    try:
        response = requests.post(f"{BASE_URL}/v1/responses", json=request_data, stream=True, timeout=10)

        log_response_details(response.status_code, response.headers)

        if response.status_code == 200:
            handle_sse_stream(response)
        else:
            logger.error(
                "❌ Request Failed",
                status_code=response.status_code,
                error_body=(response.text[:500] + "..." if len(response.text) > 500 else response.text),
            )

    except requests.exceptions.ConnectionError as e:
        error_msg = str(e)[:200] + "..." if len(str(e)) > 200 else str(e)
        logger.error("🔌 Connection Error - Is the server running?")
        logger.error(f"   Server URL: {BASE_URL}")
        logger.error(f"   Error: {error_msg}")
    except requests.exceptions.Timeout as e:
        logger.error(f"⏰ Request Timeout (10 seconds): {str(e)}")
    except Exception as e:
        logger.error(f"💥 Request Exception: {str(e)}")


def send_file_search_request(
    vector_store_id=None,
    model="qwen3-235b-a22b",
    effort="low",
    tool_choice=None,
    query=None,
):
    """Send a request that triggers file search functionality."""
    print_section_header("FILE SEARCH REQUEST")

    if vector_store_id is None:
        vector_store_id = DEFAULT_VECTOR_STORE_ID

    # Use custom query or default message
    content = query or "Search for information about machine learning algorithms and explain the key concepts."

    request_data = {
        "model": model,
        "effort": effort,
        "store": True,
        "input": [
            {
                "role": "user",
                "id": "debug_message_1",
                "content": content,
            }
        ],
        "tools": [
            {
                "type": "file_search",
                "vector_store_ids": [vector_store_id],
                "max_num_results": 5,
            }
        ],
    }

    # Add tool_choice if specified
    if tool_choice is not None:
        request_data["tool_choice"] = tool_choice

    log_request_details(f"{BASE_URL}/v1/responses", "POST", request_data)

    try:
        response = requests.post(f"{BASE_URL}/v1/responses", json=request_data, stream=True)

        log_response_details(response.status_code, response.headers)

        if response.status_code == 200:
            handle_sse_stream(response)
        else:
            error_body = response.text[:500] + "..." if len(response.text) > 500 else response.text
            logger.error(f"❌ Request Failed - Status: {response.status_code}")
            logger.error(f"   Error Body: {error_body}")

    except requests.exceptions.ConnectionError as e:
        error_msg = str(e)[:200] + "..." if len(str(e)) > 200 else str(e)
        logger.error("🔌 Connection Error - Is the server running?")
        logger.error(f"   Server URL: {BASE_URL}")
        logger.error(f"   Error: {error_msg}")
    except requests.exceptions.Timeout as e:
        logger.error(f"⏰ Request Timeout (10 seconds): {str(e)}")
    except Exception as e:
        logger.error(f"💥 Request Exception: {str(e)}")


def send_web_search_request(model="qwen3-235b-a22b", effort="low", tool_choice=None, query=None):
    """Send a request that triggers web search functionality."""
    print_section_header("WEB SEARCH REQUEST")

    # Use custom query or default message
    content = query or "What are the latest developments in artificial intelligence? Please search for recent news."

    request_data = {
        "model": model,
        "effort": effort,
        "store": True,
        "input": [
            {
                "role": "user",
                "id": "debug_message_1",
                "content": content,
            }
        ],
        "tools": [
            {
                "type": "web_search",
                "search_context_size": "medium",
                "user_location": {
                    "type": "approximate",
                    "country": "US",
                    "city": "San Francisco",
                },
            }
        ],
    }

    # Add tool_choice if specified
    if tool_choice is not None:
        request_data["tool_choice"] = tool_choice

    log_request_details(f"{BASE_URL}/v1/responses", "POST", request_data)

    try:
        response = requests.post(f"{BASE_URL}/v1/responses", json=request_data, stream=True)

        log_response_details(response.status_code, response.headers)

        if response.status_code == 200:
            handle_sse_stream(response)
        else:
            logger.error(
                "❌ Request Failed",
                status_code=response.status_code,
                error_body=response.text,
            )

    except Exception as e:
        logger.error("💥 Request Exception", exception=str(e))


def send_file_reader_request(file_id=None, model="qwen3-235b-a22b", effort="low", tool_choice=None, query=None):
    """Send a request that triggers file reading functionality."""
    print_section_header("FILE READER REQUEST")

    if file_id is None:
        file_id = DEFAULT_FILE_ID

    # Use custom query or default message
    text_content = query or "出差南京可以报销多少？"

    request_data = {
        "model": model,
        "effort": effort,
        "store": True,
        "input": [
            {
                "role": "user",
                "id": "debug_message_1",
                "content": [
                    {"type": "input_file", "file_id": file_id},
                    {
                        "type": "input_text",
                        "text": text_content,
                    },
                ],
            }
        ],
    }

    # Add tool_choice if specified
    if tool_choice is not None:
        request_data["tool_choice"] = tool_choice

    log_request_details(f"{BASE_URL}/v1/responses", "POST", request_data)

    try:
        response = requests.post(f"{BASE_URL}/v1/responses", json=request_data, stream=True)

        log_response_details(response.status_code, response.headers)

        if response.status_code == 200:
            handle_sse_stream(response)
        else:
            logger.error(
                "❌ Request Failed",
                status_code=response.status_code,
                error_body=response.text,
            )

    except Exception as e:
        logger.error("💥 Request Exception", exception=str(e))


def send_multi_tool_request(
    tasks,
    vector_store_id=None,
    file_id=None,
    model="qwen3-235b-a22b",
    effort="low",
    tool_choice=None,
    query=None,
):
    """Send a request that uses multiple tools together."""
    print_section_header("MULTI-TOOL REQUEST")

    # Use custom query or generate based on tasks
    if not query:
        if "file-search" in tasks and "web-search" in tasks:
            query = "Compare information from the documents with current web information on artificial intelligence advancements."
        elif "file-reader" in tasks and "file-search" in tasks:
            query = "Analyze the uploaded file and search for related information in the vector store."
        else:
            query = "Provide comprehensive analysis using all available tools."

    request_data = {
        "model": model,
        "effort": effort,
        "store": True,
        "input": [
            {
                "role": "user",
                "id": "debug_message_1",
                "content": query,
            }
        ],
        "tools": [],
    }

    # Add tools based on tasks
    if "file-search" in tasks:
        if vector_store_id is None:
            vector_store_id = DEFAULT_VECTOR_STORE_ID
        request_data["tools"].append(
            {
                "type": "file_search",
                "vector_store_ids": [vector_store_id],
                "max_num_results": 5,
            }
        )
        logger.info(f"   📚 Added file search tool with vector store: {vector_store_id}")

    if "web-search" in tasks:
        request_data["tools"].append(
            {
                "type": "web_search",
                "search_context_size": "medium",
                "user_location": {
                    "type": "approximate",
                    "country": "US",
                    "city": "San Francisco",
                },
            }
        )
        logger.info("   🌐 Added web search tool")

    # Handle file reader differently - it goes in the input content
    if "file-reader" in tasks:
        if file_id is None:
            file_id = DEFAULT_FILE_ID
        # Convert content to array format for file input
        request_data["input"][0]["content"] = [
            {"type": "input_file", "file_id": file_id},
            {"type": "input_text", "text": query},
        ]
        logger.info(f"   📄 Added file reader with file ID: {file_id}")

    # Add tool_choice if specified
    if tool_choice is not None:
        request_data["tool_choice"] = tool_choice

    log_request_details(f"{BASE_URL}/v1/responses", "POST", request_data)

    try:
        response = requests.post(f"{BASE_URL}/v1/responses", json=request_data, stream=True)

        log_response_details(response.status_code, response.headers)

        if response.status_code == 200:
            handle_sse_stream(response)
        else:
            logger.error(
                "❌ Request Failed",
                status_code=response.status_code,
                error_body=response.text,
            )

    except Exception as e:
        logger.error("💥 Request Exception", exception=str(e))


def main():
    """Main function to handle command line arguments and execute the appropriate test."""
    parser = argparse.ArgumentParser(
        description="Debug client for Knowledge Forge API - sends test requests and displays raw responses"
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

    logger.info("🚀 Knowledge Forge API Debug Client")
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
    if tool_choice is not None:
        logger.info(f"   Tool Choice: {tool_choice}")

    # Execute the appropriate test based on task type
    if args.task and len(args.task) > 1:
        # Multi-tool request
        send_multi_tool_request(
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
            send_file_search_request(args.vector_store_id, args.model, args.effort, tool_choice, args.query)
        elif task == "web-search":
            send_web_search_request(args.model, args.effort, tool_choice, args.query)
        elif task == "file-reader":
            send_file_reader_request(args.file_id, args.model, args.effort, tool_choice, args.query)
    else:
        # Plain chat request
        send_plain_chat_request(args.model, args.effort, tool_choice, args.query)

    logger.info("🎉 Debug session completed successfully!")


if __name__ == "__main__":
    main()
