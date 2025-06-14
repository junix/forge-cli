#!/usr/bin/env python3
"""
Debug script to capture ALL events and find where reasoning is located.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from commands.sdk import astream_response


async def debug_all_events():
    """Capture and analyze all events to find reasoning."""

    print("Capturing ALL events to find reasoning...")
    print("=" * 80)

    input_messages = [{"role": "user", "content": "云学堂的报销流程是什么？"}]
    tools = [
        {
            "type": "file_search",
            "vector_store_ids": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"],
            "max_num_results": 5,
        }
    ]

    all_events = []

    try:
        async for event_type, event_data in astream_response(
            input_messages=input_messages, model="qwen-max-latest", effort="low", store=False, tools=tools, debug=False
        ):
            # Store every event
            all_events.append(
                {
                    "type": event_type,
                    "has_data": event_data is not None,
                    "data_keys": list(event_data.keys()) if event_data and isinstance(event_data, dict) else None,
                }
            )

            # Deep search for anything that looks like reasoning
            if event_data:
                found_items = search_for_reasoning(event_data, event_type)
                for item in found_items:
                    print(f"\n🎯 FOUND in {event_type}:")
                    print(f"   Path: {item['path']}")
                    print(f"   Content: {item['content'][:100]}...")

            if event_type == "done":
                break

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()

    # Summary
    print("\n" + "=" * 80)
    print("Event Summary:")
    event_types = {}
    for event in all_events:
        event_type = event["type"]
        if event_type not in event_types:
            event_types[event_type] = {"count": 0, "has_data": False, "keys": set()}
        event_types[event_type]["count"] += 1
        if event["has_data"]:
            event_types[event_type]["has_data"] = True
            if event["data_keys"]:
                event_types[event_type]["keys"].update(event["data_keys"])

    for event_type, info in sorted(event_types.items()):
        print(f"\n{event_type}:")
        print(f"  Count: {info['count']}")
        print(f"  Has data: {info['has_data']}")
        if info["keys"]:
            print(f"  Keys: {sorted(info['keys'])}")


def search_for_reasoning(data, path="root", found_items=None):
    """Recursively search for reasoning-like content."""
    if found_items is None:
        found_items = []

    if isinstance(data, dict):
        # Check for specific keys that might contain reasoning
        for key in ["reasoning", "thinking", "thought", "summary", "rationale", "explanation"]:
            if key in data:
                found_items.append({"path": f"{path}.{key}", "content": str(data[key])})

        # Check for Chinese reasoning indicators
        for key, value in data.items():
            if isinstance(value, str) and any(
                word in value for word in ["用户问的是", "我需要", "首先", "根据", "分析"]
            ):
                found_items.append({"path": f"{path}.{key}", "content": value})

        # Recurse into dict values
        for key, value in data.items():
            search_for_reasoning(value, f"{path}.{key}", found_items)

    elif isinstance(data, list):
        # Recurse into list items
        for i, item in enumerate(data):
            search_for_reasoning(item, f"{path}[{i}]", found_items)

    elif isinstance(data, str):
        # Check if string contains reasoning indicators
        if len(data) > 50 and any(word in data for word in ["用户问的是", "我需要", "首先", "根据", "分析"]):
            found_items.append({"path": path, "content": data})

    return found_items


if __name__ == "__main__":
    asyncio.run(debug_all_events())
