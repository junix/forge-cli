#!/usr/bin/env python3
"""Test with debug output to see events."""

import asyncio
from forge_cli.main import prepare_request, create_display
from forge_cli.config import SearchConfig
from forge_cli.sdk import astream_typed_response
from forge_cli.stream.handler_typed import TypedStreamHandler

async def test():
    # Create config with file search
    config = SearchConfig()
    config.enabled_tools = ["file-search"]
    config.vec_ids = ["test_vec_id"]
    config.debug = True
    
    # Create display
    display = create_display(config)
    
    # Prepare request
    request = prepare_request(config, "Tell me about Python programming")
    
    # Create handler
    handler = TypedStreamHandler(display, debug=True)
    
    # Stream response
    print("Starting stream...")
    try:
        event_stream = astream_typed_response(request, debug=True)
        state = await handler.handle_stream(event_stream, "Tell me about Python programming")
        print(f"\nFinal state: {state.event_count} events, usage: {state.usage}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())