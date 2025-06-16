"""Main entry point - updated to use typed API by default with proper chat support."""

import argparse
import asyncio
import os
import sys
from typing import TYPE_CHECKING

# Use absolute imports from top-level directory
from forge_cli.chat.controller import ChatController
from forge_cli.config import SearchConfig

# Import the TestDataset loader
from forge_cli.dataset import TestDataset

# Registry no longer needed - using v3 directly
# Note: Registry system removed - all processing now handled by v3 renderers
from forge_cli.sdk import astream_typed_response
from forge_cli.stream.handler_typed import TypedStreamHandler

from .common.logger import logger

if TYPE_CHECKING:
    from forge_cli.display.v3.base import Display


def create_display(config: SearchConfig) -> "Display":
    """Create appropriate display based on configuration using v3 architecture."""
    # Import v3 components
    from forge_cli.display.v3.base import Display

    # Determine if we're in chat mode
    in_chat_mode = getattr(config, "chat_mode", False) or getattr(config, "chat", False)
    mode = "chat" if in_chat_mode else "default"

    # Choose renderer based on configuration
    if getattr(config, "json_output", False):
        # JSON output with Rich live updates
        from forge_cli.display.v3.renderers.json import JsonDisplayConfig, JsonRenderer

        json_config = JsonDisplayConfig(
            pretty_print=True,
            include_metadata=getattr(config, "debug", False),
            include_usage=not getattr(config, "quiet", False),
            show_panel=not getattr(config, "quiet", False),  # No panel in quiet mode
            panel_title="🔍 Knowledge Forge JSON Response" if in_chat_mode else "📋 JSON Response",
            syntax_theme="monokai",
            line_numbers=not in_chat_mode
            and not getattr(config, "quiet", False),  # No line numbers in chat or quiet mode
        )
        renderer = JsonRenderer(config=json_config)

    elif not getattr(config, "use_rich", True):
        # Plain text output
        from forge_cli.display.v3.renderers.plaintext import PlaintextDisplayConfig, PlaintextRenderer

        plain_config = PlaintextDisplayConfig(
            show_reasoning=getattr(config, "show_reasoning", True),
            show_citations=True,
            show_usage=not getattr(config, "quiet", False),
            show_metadata=getattr(config, "debug", False),
        )
        renderer = PlaintextRenderer(config=plain_config)

    else:
        # Rich terminal UI (default)
        from forge_cli.display.v3.renderers.rich import RichDisplayConfig, RichRenderer

        display_config = RichDisplayConfig(
            show_reasoning=getattr(config, "show_reasoning", True),
            show_citations=True,
            show_tool_details=True,
            show_usage=not getattr(config, "quiet", False),
            show_metadata=getattr(config, "debug", False),
        )
        renderer = RichRenderer(config=display_config, in_chat_mode=in_chat_mode)

    # Create v3 display
    return Display(renderer, mode=mode)


async def process_search(config: SearchConfig, question: str) -> dict[str, str | int | float | bool | list] | None:
    """Process search with the typed API."""
    # Note: Registry initialization removed - processing handled by v3 renderers

    # Create display
    display = create_display(config)

    # Create typed stream handler
    handler = TypedStreamHandler(display, debug=config.debug)

    # Create a temporary conversation state for single-turn search
    from forge_cli.models.conversation import ConversationState

    conversation = ConversationState(model=config.model)

    # Prepare typed request using conversation state
    request = conversation.new_request(question, config)

    # Stream and process with typed API
    event_stream = astream_typed_response(request, debug=config.debug)
    response = await handler.handle_stream(event_stream, question, config.vec_ids)

    # Return response information
    return {
        "response_id": response.id if response else None,
        "model": response.model if response else None,
        "usage": response.usage if response else None,
        "citations": response,  # Return full response for citation extraction
        "vector_store_ids": config.vec_ids,  # Use config vector store IDs directly
    }


async def start_chat_mode(
    config: SearchConfig, initial_question: str | None = None, resume_conversation_id: str | None = None
) -> None:
    """Start interactive chat mode with typed API."""
    # Note: Registry initialization removed - processing handled by v3 renderers

    # Create display
    display = create_display(config)

    # Create chat controller
    controller = ChatController(config, display)

    # Resume existing conversation if requested
    if resume_conversation_id:
        try:
            from forge_cli.models.conversation import ConversationState

            controller.conversation = ConversationState.load_by_id(resume_conversation_id)
            display.show_status(
                f"📂 Resumed conversation {resume_conversation_id} with {controller.conversation.get_message_count()} messages"
            )

        except FileNotFoundError:
            display.show_error(f"Conversation {resume_conversation_id} not found")
            return
        except Exception as e:
            display.show_error(f"Failed to resume conversation: {e}")
            return

    # Patch the controller to use typed API
    async def typed_send_message(content: str) -> None:
        """Send message using typed API with proper chat support."""
        # Create a fresh display for this message
        message_display = create_display(config)

        # Set display to chat mode - use the Display's mode property
        message_display.mode = "chat"

        # Create typed request with full conversation history (automatically adds user message)
        request = controller.conversation.new_request(content, config)

        # Create typed handler and stream
        handler = TypedStreamHandler(message_display, debug=config.debug)

        # Stream the response
        event_stream = astream_typed_response(request, debug=config.debug)
        response = await handler.handle_stream(event_stream, content, config.vec_ids)

        # Update conversation state from response (includes adding assistant message)
        if response:
            controller.conversation.update_from_response(response)

    # Replace method
    controller.send_message = typed_send_message

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

    except Exception:
        logger.exeption("Chat error")


async def main():
    """Main function to handle command line arguments and run the request."""
    # Check if no arguments provided
    show_help = len(sys.argv) == 1

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Refactored multi-tool search using Knowledge Forge SDK (typed API)",
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

    # Resume conversation argument
    parser.add_argument(
        "--resume",
        "-r",
        type=str,
        help="Resume an existing conversation by ID",
    )

    # Legacy API argument (for backward compatibility)
    parser.add_argument(
        "--legacy-api",
        action="store_true",
        help="Use legacy dict-based API (not recommended)",
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
        print('  python -m hello_file_search_refactored -q "What information is in these documents?"')
        print("  python -m hello_file_search_refactored --vec-id vec_123 -t file-search")
        print()
        print("  # Web search:")
        print('  python -m hello_file_search_refactored -t web-search -q "Latest AI news"')
        print()
        print("  # Both tools:")
        print("  python -m hello_file_search_refactored -t file-search -t web-search --vec-id vec_123")
        print()
        print("  # Interactive chat mode:")
        print("  python -m hello_file_search_refactored --chat")
        print("  python -m hello_file_search_refactored -i -t file-search --vec-id vec_123")
        return

    # Handle version
    if args.version:
        from . import __version__

        print(f"Knowledge Forge File Search Refactored v{__version__}")
        return

    # Warn about legacy API
    if args.legacy_api:
        print("⚠️  Warning: Using legacy dict-based API. Consider using the typed API (default).")
        print("   The legacy API will be deprecated in future versions.")
        sys.exit(1)

    # Handle dataset if provided
    dataset = None
    if getattr(args, "dataset", None):
        dataset = TestDataset.from_json(args.dataset)
        if not args.quiet:
            print(f"Loaded dataset from {args.dataset}")
            print(f"  Vector Store ID: {dataset.vectorstore_id}")
            print(f"  Files: {len(dataset.files)}")

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

    # Check if resume mode is requested
    if hasattr(args, "resume") and args.resume:
        # Resume existing conversation
        await start_chat_mode(config, None, args.resume)
    elif config.chat_mode:
        # If a question was provided with -q, send it as the first message
        initial_question = args.question if args.question != "What information can you find in the documents?" else None
        await start_chat_mode(config, initial_question)
    else:
        # Run single-turn search
        await process_search(config, args.question)


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
