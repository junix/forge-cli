#!/usr/bin/env python3
"""Test reasoning events directly."""

import asyncio
from forge_cli.sdk import astream_response

async def test_reasoning():
    # Test with high effort
    event_count = 0
    reasoning_events = []
    
    async for event_type, event_data in astream_response(
        input_messages=[{"role": "user", "content": "Calculate 15 + 27 step by step"}],
        model="qwen-max-latest",
        effort="high",
        debug=True
    ):
        event_count += 1
        if "reasoning" in event_type:
            reasoning_events.append((event_type, event_data))
            print(f"\nREASONING EVENT: {event_type}")
            if event_data:
                print(f"DATA: {event_data}")
                
    print(f"\nTotal events: {event_count}")
    print(f"Reasoning events found: {len(reasoning_events)}")

if __name__ == "__main__":
    asyncio.run(test_reasoning())