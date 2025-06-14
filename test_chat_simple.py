#!/usr/bin/env python3
"""Simple test to isolate chat error."""

import asyncio
from forge_cli.config import SearchConfig
from forge_cli.main import start_chat_mode

async def test():
    """Test chat mode startup."""
    config = SearchConfig(
        chat_mode=True,
        quiet=True,
        debug=True,
    )
    
    print("Starting chat mode...")
    try:
        # Just try to start it
        task = asyncio.create_task(start_chat_mode(config))
        
        # Wait a short time
        await asyncio.sleep(0.1)
        
        # Cancel the task
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            print("Chat mode cancelled successfully")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())