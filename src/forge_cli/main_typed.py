"""Main entry point for the forge-cli with typed API support."""

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Optional, Union, Dict, Any

# Import the TestDataset loader
from forge_cli.dataset import TestDataset

# Add parent directory to path for SDK import
sys.path.insert(0, str(Path(__file__).parent.parent))

# Use absolute imports from top-level directory
from forge_cli.chat.controller import ChatController
from forge_cli.config import SearchConfig
from forge_cli.display.registry import DisplayRegistry, initialize_default_displays
from forge_cli.display.v2.base import Display
from forge_cli.processors.registry import initialize_default_registry
from forge_cli.sdk import astream_response, astream_typed_response, async_get_vectorstore, create_typed_request
from forge_cli.stream.handler import StreamHandler
from forge_cli.response._types import Request, FileSearchTool, WebSearchTool
from forge_cli.response._types.web_search_tool import UserLocation


def create_display(config: SearchConfig) -> Display:
    """Create appropriate display based on configuration using the display registry."""
    # Initialize default displays if not already done
    initialize_default_displays()

    # Get the v2 display directly from registry
    try:
        return DisplayRegistry.get_display_for_config(config)
    except (ValueError, ImportError):
        # Fallback to v2 plain renderer if there's an error
        from forge_cli.display.v2.renderers.plain import PlainRenderer

        renderer = PlainRenderer()
        return Display(renderer)


def prepare_typed_request(config: SearchConfig, question: str) -> Request:
    """Prepare typed request for the API."""
    # Build tools list
    tools = []

    # File search tool
    if "file-search" in config.enabled_tools and config.vec_ids:
        tools.append(
            FileSearchTool(type="file_search", vector_store_ids=config.vec_ids, max_num_results=config.max_results)
        )

    # Web search tool
    if "web-search" in config.enabled_tools:
        user_location = None
        location = config.get_web_location()
        if location:
            user_location = UserLocation(
                type="approximate",
                country=location.get("country"),
                city=location.get("city"),
                region=location.get("region"),
                timezone=location.get("timezone"),
            )

        tools.append(WebSearchTool(type="web_search", search_context_size="medium", user_location=user_location))

    # Create typed request
    return create_typed_request(
        input_messages=question, model=config.model, effort=config.effort, tools=tools, store=True
    )


def prepare_dict_request(config: SearchConfig, question: str) -> dict[str, Any]:
    """Prepare dict-based request for backward compatibility."""
    # Base request
    request = {
        "input_messages": [
            {
                "role": "user",
                "id": "user_message_1",
                "content": question,
            }
        ],
        "model": config.model,
        "effort": config.effort,
        "store": True,
        "debug": config.debug,
    }

    # Add tools if enabled
    tools = []

    # File search tool
    if "file-search" in config.enabled_tools and config.vec_ids:
        tools.append(
            {
                "type": "file_search",
                "vector_store_ids": config.vec_ids,
                "max_num_results": config.max_results,
            }
        )

    # Web search tool
    if "web-search" in config.enabled_tools:
        web_tool = {"type": "web_search"}

        # Add location if provided
        location = config.get_web_location()
        if location:
            web_tool["user_location"] = {"type": "approximate", **location}

        tools.append(web_tool)

    # Add tools to request if any
    if tools:
        request["tools"] = tools

    return request


async def process_search(config: SearchConfig, question: str) -> Optional[Dict[str, Any]]:
    """Process search with the given configuration, supporting both typed and dict APIs."""
    # Initialize processor registry
    initialize_default_registry()

    # Create display
    display = create_display(config)

    # Show request info
    display.show_request_info(
        {
            "question": question,
            "vec_ids": config.vec_ids,
            "model": config.model,
            "effort": config.effort,
            "max_results": config.max_results,
            "tools": config.enabled_tools,
        }
    )

    # Create stream handler
    handler = StreamHandler(display, debug=config.debug)

    try:
        # Check if typed API is enabled
        use_typed = config.use_typed_api if hasattr(config, "use_typed_api") else False

        if use_typed:
            # Use typed API
            request = prepare_typed_request(config, question)
            # Note: StreamHandler needs to be updated to handle typed responses
            # For now, we'll use the dict API with a compatibility layer
            event_stream = astream_typed_response(request, debug=config.debug)
        else:
            # Use dict API (current default)
            request = prepare_dict_request(config, question)
            event_stream = astream_response(**request)

        # Stream and process
        response = await handler.handle_stream(event_stream, question)

        # Display vector store info if not in JSON mode
        if response and not config.json_output and config.vec_ids:
            await display_vectorstore_info(config.vec_ids, config.use_rich)

        return response

    except Exception as e:
        display.show_error(f"Processing error: {str(e)}")
        if config.debug:
            import traceback

            traceback.print_exc()
        return None


async def start_chat_mode(config: SearchConfig, initial_question: Optional[str] = None) -> None:
    """Start interactive chat mode with typed API support."""
    # Initialize processor registry
    initialize_default_registry()

    # Create display
    display = create_display(config)

    # Create chat controller
    controller = ChatController(config, display)

    # Show welcome
    controller.show_welcome()

    # If initial question provided, process it first
    if initial_question:
        await controller.send_message(initial_question)

    # Start chat loop
    controller.running = True

    try:
        while controller.running:
            # Get user input
            user_input = await controller.get_user_input()

            if user_input is None:  # EOF or interrupt
                break

            # Process the input
            continue_chat = await controller.process_input(user_input)

            if not continue_chat:
                break

    except KeyboardInterrupt:
        display.show_status("\n\n👋 Chat interrupted. Goodbye!")

    except Exception as e:
        display.show_error(f"Chat error: {str(e)}")
        if config.debug:
            import traceback

            traceback.print_exc()


async def display_vectorstore_info(vec_ids: list[str], use_rich: bool = True) -> None:
    """Display information about the vector stores."""
    if use_rich:
        from rich.console import Console
        from rich.text import Text

        console = Console()
        console.print(Text("\n📚 Vector Store Information:", style="cyan bold"))
    else:
        print("\n📚 Vector Store Information:")

    for i, vec_id in enumerate(vec_ids, 1):
        try:
            vec_info = await async_get_vectorstore(vec_id)
            if vec_info:
                if use_rich:
                    from rich.text import Text

                    vec_text = Text()
                    vec_text.append(f"  🔍 Vector Store #{i}:\n", style="blue bold")
                    vec_text.append(f"     ID: {vec_id}\n", style="white")
                    vec_text.append(f"     Name: {vec_info.get('name', 'N/A')}\n", style="white")
                    vec_text.append(f"     Status: {vec_info.get('status', 'N/A')}\n", style="white")
                    vec_text.append(f"     File count: {vec_info.get('file_count', 0)}\n", style="white")

                    from rich.console import Console

                    console = Console()
                    console.print(vec_text)
                else:
                    print(f"  🔍 Vector Store #{i}:")
                    print(f"     ID: {vec_id}")
                    print(f"     Name: {vec_info.get('name', 'N/A')}")
                    print(f"     Status: {vec_info.get('status', 'N/A')}")
                    print(f"     File count: {vec_info.get('file_count', 0)}")
            else:
                msg = f"  ❌ Vector Store #{i}: {vec_id} (Not found)"
                if use_rich:
                    from rich.console import Console

                    console = Console()
                    console.print(msg, style="red")
                else:
                    print(msg)
        except Exception as e:
            msg = f"  ⚠️  Vector Store #{i}: {vec_id} (Error: {str(e)})"
            if use_rich:
                from rich.console import Console

                console = Console()
                console.print(msg, style="yellow")
            else:
                print(msg)


def main():
    """Main entry point with typed API support."""
    parser = argparse.ArgumentParser(
        description="Knowledge Forge CLI - Modern tools for document search and AI interaction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Existing arguments
    parser.add_argument(
        "question",
        nargs="?",
        help="Question to ask (if not provided, enters interactive mode)",
    )

    parser.add_argument(
        "--vec-id",
        "--vector-store-id",
        dest="vec_ids",
        nargs="+",
        help="Vector store IDs for file search",
    )

    parser.add_argument(
        "--model",
        "-m",
        default="qwen-max-latest",
        help="Model to use (default: qwen-max-latest)",
    )

    parser.add_argument(
        "--effort",
        "-e",
        choices=["low", "medium", "high"],
        default="low",
        help="Effort level (default: low)",
    )

    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Show debug information",
    )

    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )

    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Output in JSON format",
    )

    parser.add_argument(
        "--quiet",
        "-Q",
        action="store_true",
        help="Quiet mode - minimal output",
    )

    parser.add_argument(
        "--chat",
        "-i",
        action="store_true",
        help="Start in interactive chat mode",
    )

    parser.add_argument(
        "--tools",
        "-t",
        nargs="+",
        choices=["file-search", "web-search"],
        default=["file-search"],
        help="Tools to enable (default: file-search)",
    )

    parser.add_argument(
        "--max-results",
        type=int,
        default=20,
        help="Maximum number of search results (default: 20)",
    )

    parser.add_argument(
        "--country",
        help="Country for web search location",
    )

    parser.add_argument(
        "--city",
        help="City for web search location",
    )

    parser.add_argument(
        "--throttle",
        type=int,
        default=0,
        help="Throttle display updates in milliseconds (default: 0)",
    )

    parser.add_argument(
        "--server",
        help="Override server URL",
    )

    # New argument for typed API
    parser.add_argument(
        "--typed-api",
        action="store_true",
        help="Use typed Request/Response API (experimental)",
    )

    # Test dataset support
    parser.add_argument(
        "--dataset",
        help="Path to test dataset YAML file",
    )

    parser.add_argument(
        "--dataset-filter",
        help="Filter dataset by test ID pattern",
    )

    args = parser.parse_args()

    # Override server URL if provided
    if args.server:
        os.environ["KNOWLEDGE_FORGE_URL"] = args.server

    # Create configuration
    config = SearchConfig(
        vec_ids=args.vec_ids or [],
        model=args.model,
        effort=args.effort,
        debug=args.debug,
        use_rich=not args.no_color,
        json_output=args.json_output,
        quiet=args.quiet,
        enabled_tools=args.tools,
        max_results=args.max_results,
        country=args.country,
        city=args.city,
        throttle_ms=args.throttle,
    )

    # Add typed API flag to config
    if args.typed_api:
        config.use_typed_api = True

    # Handle dataset testing
    if args.dataset:
        dataset = TestDataset.load(args.dataset)
        if args.dataset_filter:
            dataset = dataset.filter(args.dataset_filter)

        if not config.use_rich:
            print(f"Loaded {len(dataset.tests)} tests from {args.dataset}")

        # Run each test
        for test in dataset.tests:
            if not config.use_rich:
                print(f"\n--- Test: {test.id} ---")
                print(f"Query: {test.query}")

            # Override config with test settings
            test_config = config.model_copy()
            if test.vec_ids:
                test_config.vec_ids = test.vec_ids
            if test.tools:
                test_config.enabled_tools = test.tools

            # Run the test
            asyncio.run(process_search(test_config, test.query))

    # Regular operation
    elif args.chat or (not args.question and sys.stdin.isatty()):
        # Interactive chat mode
        asyncio.run(start_chat_mode(config, args.question))
    elif args.question:
        # Single question mode
        asyncio.run(process_search(config, args.question))
    else:
        # Read from stdin
        question = sys.stdin.read().strip()
        if question:
            asyncio.run(process_search(config, question))
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
