#!/usr/bin/env python3
"""
Main CLI entry point using typed API with full typed support.

This version uses:
- astream_typed_response for type-safe streaming
- TypedStreamHandler for handling both dict and typed responses
- TypedProcessorRegistry for processor management
- Full Request/Response type system
"""

import argparse
import asyncio
import sys
from typing import Optional

from forge_cli.config import SearchConfig
from forge_cli.sdk import astream_typed_response
from forge_cli.models import Request, FileSearchTool, WebSearchTool
from forge_cli.stream.handler_typed import TypedStreamHandler
from forge_cli.display.registry import create_display
from forge_cli.chat.controller import ChatController
from loguru import logger


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Knowledge Forge CLI - Typed API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic query
  %(prog)s -q "What is machine learning?"
  
  # File search with vector store
  %(prog)s -q "Find information about transformers" --vec-id vs_12345
  
  # Web search with location
  %(prog)s -t web-search -q "Latest AI news" --country US --city "San Francisco"
  
  # Interactive chat mode
  %(prog)s --chat
  
  # Debug mode with JSON output
  %(prog)s -q "test query" --debug --json
        """,
    )

    # Query options
    parser.add_argument("-q", "--query", type=str, help="Query to send to the API")
    parser.add_argument(
        "-t", "--tools", nargs="+", choices=["file-search", "web-search"], default=[], help="Tools to enable"
    )

    # Tool-specific options
    parser.add_argument(
        "--vec-id", "--vector-store-id", dest="vector_store_ids", nargs="+", help="Vector store IDs for file search"
    )
    parser.add_argument("--country", type=str, help="Country for web search")
    parser.add_argument("--city", type=str, help="City for web search")

    # Model options
    parser.add_argument("--model", type=str, default="qwen-max-latest", help="Model to use (default: qwen-max-latest)")
    parser.add_argument(
        "--effort", choices=["low", "medium", "high"], default="medium", help="Effort level for the response"
    )
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature for response generation (0.0-1.0)")
    parser.add_argument("--max-tokens", type=int, default=2000, help="Maximum output tokens")

    # Display options
    parser.add_argument("--format", choices=["rich", "plain", "json"], default="rich", help="Output format")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("--quiet", "-Q", action="store_true", help="Minimal output")
    parser.add_argument("--debug", "-d", action="store_true", help="Show debug information")
    parser.add_argument("--json", action="store_true", help="Output as JSON (alias for --format json)")

    # Interactive mode
    parser.add_argument("--chat", "-i", action="store_true", help="Interactive chat mode")

    # Advanced options
    parser.add_argument("--throttle", type=int, default=0, help="Throttle output (ms between tokens)")
    parser.add_argument("--server", type=str, help="Override server URL")

    return parser.parse_args()


async def run_single_query(args: argparse.Namespace, config: SearchConfig) -> None:
    """Run a single query with typed API."""
    # Create display
    format_type = "json" if args.json else args.format
    display = create_display(format=format_type, config=config)

    # Create stream handler
    handler = TypedStreamHandler(display, debug=args.debug)

    # Build tools list
    tools = []

    if "file-search" in args.tools and args.vector_store_ids:
        tools.append(
            FileSearchTool(
                type="file_search",
                vector_store_ids=args.vector_store_ids,
                max_num_results=5,
            )
        )

    if "web-search" in args.tools:
        tool_params = {"type": "web_search"}
        if args.country:
            tool_params["country"] = args.country
        if args.city:
            tool_params["city"] = args.city
        tools.append(WebSearchTool(**tool_params))

    # Create request
    request = Request(
        input=[{"type": "text", "text": args.query}],
        model=args.model,
        tools=tools,
        temperature=args.temperature,
        max_output_tokens=args.max_tokens,
    )

    try:
        # Get typed stream
        stream = astream_typed_response(request, debug=args.debug)

        # Handle stream
        state = await handler.handle_stream(stream, args.query)

        # Show summary if not quiet
        if not args.quiet and format_type != "json":
            print("\n" + "=" * 50)
            print(f"✅ Response completed")
            print(f"   Events: {state.event_count}")
            if state.usage:
                print(f"   Tokens: {state.usage.get('total_tokens', 0)}")

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


async def run_chat_mode(args: argparse.Namespace, config: SearchConfig) -> None:
    """Run interactive chat mode with typed API."""
    # Create display
    display = create_display(format="rich", config=config)

    # Create chat controller with typed API
    controller = ChatController(
        config=config,
        display=display,
        initial_tools=args.tools,
        initial_query=args.query,
        use_typed_api=True,  # Use typed API
    )

    # Run chat loop
    await controller.run()


async def main() -> None:
    """Main entry point."""
    args = parse_arguments()

    # Create config
    config = SearchConfig(
        quiet=args.quiet,
        debug=args.debug,
        no_color=args.no_color,
        throttle_ms=args.throttle,
        vector_store_ids=args.vector_store_ids or [],
        country=args.country,
        city=args.city,
        model=args.model,
        effort=args.effort,
        temperature=args.temperature,
        max_output_tokens=args.max_tokens,
    )

    # Override server if specified
    if args.server:
        import os

        os.environ["KNOWLEDGE_FORGE_URL"] = args.server

    # Run appropriate mode
    if args.chat:
        await run_chat_mode(args, config)
    elif args.query:
        await run_single_query(args, config)
    else:
        print("Error: Either --query or --chat must be specified")
        print("Try --help for usage information")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
