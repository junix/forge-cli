#!/usr/bin/env python3
"""Direct test of reasoning with typed API."""

import asyncio
from forge_cli.sdk import astream_typed_response
from forge_cli.response._types import Request, InputMessage

async def test_reasoning():
    # Create a request with high effort
    request = Request(
        input=[InputMessage(role="user", content="Explain step by step: What is 25 * 17?")],
        model="qwen-max-latest",
        effort="high",
        temperature=0.7,
        max_output_tokens=2000,
    )
    
    print("Testing reasoning with effort=high...")
    event_count = 0
    reasoning_events = []
    
    async for event_type, response in astream_typed_response(request, debug=True):
        event_count += 1
        print(f"[{event_count}] {event_type}")
        
        if "reasoning" in event_type:
            reasoning_events.append(event_type)
            
    print(f"\nTotal events: {event_count}")
    print(f"Reasoning events: {reasoning_events}")
    
    if reasoning_events:
        print("\n✅ Reasoning events were fired!")
    else:
        print("\n⚠️  No reasoning events found")

if __name__ == "__main__":
    asyncio.run(test_reasoning())