"""Main entry point with typed API migration support."""

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

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
from forge_cli.processors.registry_typed import initialize_typed_registry
from forge_cli.sdk import astream_response, astream_typed_response, async_get_vectorstore
from forge_cli.stream.handler import StreamHandler
from forge_cli.stream.handler_typed import TypedStreamHandler
from forge_cli.response._types import Request, FileSearchTool, WebSearchTool
from forge_cli.response.adapters import MigrationHelper


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


def prepare_request_legacy(config: SearchConfig, question: str) -> dict[str, Any]:
    """Prepare request parameters for the legacy API."""
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


def prepare_request_typed(config: SearchConfig, question: str) -> Request:
    """Prepare typed request for the new API."""
    # Build tools list
    tools = []

    # File search tool
    if "file-search" in config.enabled_tools and config.vec_ids:
        tools.append(
            FileSearchTool(
                type="file_search",
                vector_store_ids=config.vec_ids,
                max_num_results=config.max_results,
            )
        )

    # Web search tool
    if "web-search" in config.enabled_tools:
        tool_params = {"type": "web_search"}
        location = config.get_web_location()
        if location:
            if "country" in location:
                tool_params["country"] = location["country"]
            if "city" in location:
                tool_params["city"] = location["city"]
        tools.append(WebSearchTool(**tool_params))

    # Create typed request
    return Request(
        input=[{"type": "text", "text": question}],
        model=config.model,
        tools=tools,
        temperature=config.temperature or 0.7,
        max_output_tokens=config.max_output_tokens or 2000,
    )


async def process_search_legacy(config: SearchConfig, question: str) -> Optional[Dict[str, Any]]:
    """Process search with the legacy dict-based API."""
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

    # Prepare request
    request = prepare_request_legacy(config, question)

    try:
        # Stream and process
        event_stream = astream_response(**request)
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


async def process_search_typed(config: SearchConfig, question: str) -> Optional[Dict[str, Any]]:
    """Process search with the typed API."""
    # Initialize typed processor registry
    initialize_typed_registry()

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

    # Create typed stream handler
    handler = TypedStreamHandler(display, debug=config.debug)

    # Prepare typed request
    request = prepare_request_typed(config, question)

    try:
        # Stream and process with typed API
        event_stream = astream_typed_response(request, debug=config.debug)
        state = await handler.handle_stream(event_stream, question)

        # Display vector store info if not in JSON mode
        if state and not config.json_output and config.vec_ids:
            await display_vectorstore_info(config.vec_ids, config.use_rich)

        # Convert state to response dict for compatibility
        return {
            "response_id": state.response_id,
            "model": state.model,
            "usage": state.usage,
            "event_count": state.event_count,
        }

    except Exception as e:
        display.show_error(f"Processing error: {str(e)}")
        if config.debug:
            import traceback
            traceback.print_exc()
        return None


async def process_search(config: SearchConfig, question: str, use_typed_api: bool = False) -> Optional[Dict[str, Any]]:
    """Process search with the appropriate API based on configuration."""
    if use_typed_api:
        return await process_search_typed(config, question)
    else:
        return await process_search_legacy(config, question)


async def start_chat_mode(config: SearchConfig, initial_question: Optional[str] = None, use_typed_api: bool = False) -> None:
    """Start interactive chat mode."""
    # Initialize appropriate processor registry
    if use_typed_api:
        initialize_typed_registry()
    else:
        initialize_default_registry()

    # Create display
    display = create_display(config)

    # Create chat controller with optional typed API support
    controller = ChatController(config, display)
    
    # If typed API is enabled, patch the controller's process method
    if use_typed_api:
        # Store original method
        original_process = controller.process_message
        
        async def typed_process_message(message: str) -> None:
            """Process message using typed API."""
            request = prepare_request_typed(config, message)
            handler = TypedStreamHandler(display, debug=config.debug)
            event_stream = astream_typed_response(request, debug=config.debug)
            await handler.handle_stream(event_stream, message)
        
        # Replace method
        controller.process_message = typed_process_message

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
                    vec_text.append("    🔑 ID: ", style="yellow")
                    vec_text.append(f"{vec_id}\n")
                    vec_text.append("    📝 Name: ", style="yellow")
                    vec_text.append(f"{vec_info.get('name', 'Unknown')}\n")

                    if vec_info.get("description"):
                        vec_text.append("    📄 Description: ", style="yellow")
                        vec_text.append(f"{vec_info.get('description')}\n")

                    file_count = len(vec_info.get("file_ids", []))
                    vec_text.append("    📊 File Count: ", style="yellow")
                    vec_text.append(f"{file_count}\n")

                    console.print(vec_text)
                else:
                    print(f"  🔍 Vector Store #{i}:")
                    print(f"    🔑 ID: {vec_id}")
                    print(f"    📝 Name: {vec_info.get('name', 'Unknown')}")

                    if vec_info.get("description"):
                        print(f"    📄 Description: {vec_info.get('description')}")

                    file_count = len(vec_info.get("file_ids", []))
                    print(f"    📊 File Count: {file_count}")
            else:
                if use_rich:
                    console.print(
                        f"  ❓ Vector Store #{i}: Unable to fetch details",
                        style="yellow",
                    )
                else:
                    print(f"  ❓ Vector Store #{i}: Unable to fetch details")

        except Exception as e:
            if use_rich:
                console.print(f"  ❌ Vector Store #{i}: Error - {e}", style="red")
            else:
                print(f"  ❌ Vector Store #{i}: Error - {e}")


async def main():
    """Main function to handle command line arguments and run the request."""
    # Check if no arguments provided
    show_help = len(sys.argv) == 1

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Refactored multi-tool search using Knowledge Forge SDK (with typed API support)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Query argument
    parser.add_argument(
        "--question",
        "-q",
        type=str,
        default="What information can you find in the documents?",
        help="Question to ask",
    )

    # Vector store arguments
    parser.add_argument(
        "--vec-id",
        action="append",
        default=None,
        help="Vector store ID(s) to search in (can specify multiple)",
    )
    # Dataset argument
    parser.add_argument(
        "--dataset",
        type=str,
        help="Path to dataset JSON file with vectorstore ID and file configurations",
    )

    # Model arguments
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default="qwen-max-latest",
        help="Model to use for the response",
    )
    parser.add_argument(
        "--effort",
        "-e",
        type=str,
        choices=["low", "medium", "high", "dev"],
        default="low",
        help="Effort level for the response",
    )

    # Search arguments
    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Maximum number of search results per vector store",
    )

    # Tool arguments
    parser.add_argument(
        "--tool",
        "-t",
        action="append",
        choices=["file-search", "web-search"],
        help="Enable specific tools (can specify multiple)",
    )

    # Web search location
    parser.add_argument(
        "--country",
        type=str,
        help="Country for web search location context",
    )
    parser.add_argument(
        "--city",
        type=str,
        help="City for web search location context",
    )

    # Display arguments
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Enable debug output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--quiet",
        "-Q",
        action="store_true",
        help="Quiet mode - minimal output",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    parser.add_argument(
        "--throttle",
        type=int,
        default=0,
        help="Throttle output (milliseconds between tokens)",
    )

    # Server argument
    parser.add_argument(
        "--server",
        default=os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999"),
        help="Server URL",
    )

    # Chat mode argument
    parser.add_argument(
        "--chat",
        "--interactive",
        "-i",
        action="store_true",
        help="Start interactive chat mode",
    )

    # Typed API argument
    parser.add_argument(
        "--typed-api",
        action="store_true",
        help="Use typed API (experimental)",
    )

    # Other arguments
    parser.add_argument(
        "--version",
        "-v",
        action="store_true",
        help="Show version and exit",
    )

    args = parser.parse_args()

    # Show help if no arguments
    if show_help and not any(arg in sys.argv for arg in ["-h", "--help"]):
        parser.print_help()
        print("\nExample usage:")
        print("  # File search:")
        print('  python -m forge_cli.main_typed_migration -q "What information is in these documents?"')
        print("  python -m forge_cli.main_typed_migration --vec-id vec_123 -t file-search")
        print()
        print("  # Web search:")
        print('  python -m forge_cli.main_typed_migration -t web-search -q "Latest AI news"')
        print()
        print("  # Both tools:")
        print("  python -m forge_cli.main_typed_migration -t file-search -t web-search --vec-id vec_123")
        print()
        print("  # Interactive chat mode:")
        print("  python -m forge_cli.main_typed_migration --chat")
        print("  python -m forge_cli.main_typed_migration -i -t file-search --vec-id vec_123")
        print()
        print("  # Typed API (experimental):")
        print("  python -m forge_cli.main_typed_migration --typed-api -q 'test query'")
        return

    # Handle version
    if args.version:
        from . import __version__

        print(f"Knowledge Forge File Search Refactored v{__version__}")
        return

    # Handle dataset if provided
    dataset = None
    if hasattr(args, "dataset") and args.dataset:
        try:
            dataset = TestDataset.from_json(args.dataset)
            if not args.quiet:
                print(f"Loaded dataset from {args.dataset}")
                print(f"  Vector Store ID: {dataset.vectorstore_id}")
                print(f"  Files: {len(dataset.files)}")
        except Exception as e:
            print(f"Error loading dataset: {e}")
    
    # Create configuration
    config = SearchConfig.from_args(args)

    # Use vectorstore ID from dataset if no command line vec_ids provided
    if dataset and dataset.vectorstore_id and not args.vec_id:
        config.vec_ids = [dataset.vectorstore_id]
        # Enable file-search tool when using dataset
        if "file-search" not in config.enabled_tools:
            config.enabled_tools.append("file-search")

    # Use default vector IDs if none provided
    if not config.vec_ids:
        config.vec_ids = SearchConfig().vec_ids

    # Default to file-search if vec_ids provided but no tools specified
    if not config.enabled_tools and config.vec_ids:
        config.enabled_tools = ["file-search"]

    # Update environment if server specified
    if config.server_url != os.environ.get("KNOWLEDGE_FORGE_URL"):
        os.environ["KNOWLEDGE_FORGE_URL"] = config.server_url
        if not config.quiet and not config.json_output:
            print(f"🔗 Using server: {config.server_url}")

    # Show typed API status if enabled
    if args.typed_api and not config.quiet:
        print("🚀 Using typed API (experimental)")

    # Check if chat mode is requested
    if config.chat_mode:
        # If a question was provided with -q, send it as the first message
        initial_question = args.question if args.question != "What information can you find in the documents?" else None
        await start_chat_mode(config, initial_question, use_typed_api=args.typed_api)
    else:
        # Run single-turn search
        await process_search(config, args.question, use_typed_api=args.typed_api)


def run_main_async():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nChat interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_main_async()