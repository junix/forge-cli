#!/usr/bin/env python3
"""
File search example using typed API v2 with new stream handler.

This demonstrates using the fully typed API with the new TypedStreamHandler
that supports both dict and typed Response objects.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from forge_cli.config import SearchConfig
from forge_cli.sdk import astream_typed_response
from forge_cli.models import Request, FileSearchTool
from forge_cli.stream.handler_typed import TypedStreamHandler
from forge_cli.display.registry import create_display


async def main():
    """Main entry point."""
    # Configuration
    config = SearchConfig(
        quiet=False,
        debug=True,
        vector_store_ids=["<your-vector-store-id>"],  # Replace with actual ID
    )

    # Create display
    display = create_display("v2", format="rich", config=config)

    # Create stream handler with typed support
    handler = TypedStreamHandler(display, debug=config.debug)

    # Example query
    query = "What information is in these documents about machine learning?"

    print(f"🔍 Searching for: {query}\n")

    # Create request with typed tools
    request = Request(
        input=[{"type": "text", "text": query}],
        model="qwen-max-latest",
        tools=[
            FileSearchTool(
                type="file_search",
                vector_store_ids=config.vector_store_ids,
                max_num_results=5,
            )
        ],
        temperature=0.7,
        max_output_tokens=2000,
    )

    try:
        # Get typed stream
        stream = astream_typed_response(request, debug=config.debug)

        # Handle stream with typed handler
        state = await handler.handle_stream(stream, query)

        # Show final statistics
        print("\n" + "=" * 50)
        print("📊 Final Statistics:")
        print(f"   Response ID: {state.response_id}")
        print(f"   Model: {state.model}")
        print(f"   Events processed: {state.event_count}")
        print(f"   Output items: {len(state.output_items)}")

        # Show tool states
        if state.tool_states:
            print("\n🔧 Tool Execution:")
            for tool_type, tool_state in state.tool_states.items():
                info = tool_state.to_display_info()
                print(f"   {tool_type}:")
                print(f"      Status: {tool_state.status}")
                if "results_count" in info:
                    print(f"      Results: {info['results_count']}")
                if "query_time" in info:
                    print(f"      Query time: {info['query_time']:.2f}s")
                if "retrieval_time" in info:
                    print(f"      Total time: {info['retrieval_time']:.2f}s")

        # Show usage
        if state.usage:
            print(f"\n💰 Token Usage:")
            print(f"   Input: {state.usage.get('input_tokens', 0)}")
            print(f"   Output: {state.usage.get('output_tokens', 0)}")
            print(f"   Total: {state.usage.get('total_tokens', 0)}")

        # Show file mappings
        if state.file_id_to_name:
            print(f"\n📁 Files Referenced:")
            for file_id, filename in state.file_id_to_name.items():
                print(f"   {filename} ({file_id})")

    except KeyboardInterrupt:
        print("\n\n⚠️  Search interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if config.debug:
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
