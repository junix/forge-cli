#!/usr/bin/env python3
"""
Debug script to log all streaming events from the Knowledge Forge API.
This helps identify what events are being fired and their structure.
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the current directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

# Import SDK functions
from commands.sdk import astream_response


async def log_all_events(question: str, vec_ids: list, model: str = "qwen-max-latest", effort: str = "low"):
    """Log all events from the streaming response."""

    print(f"\n{'=' * 80}")
    print(f"🔍 Event Logger - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Question: {question}")
    print(f"Model: {model}, Effort: {effort}")
    print(f"{'=' * 80}\n")

    # Create input messages
    input_messages = [{"role": "user", "content": question}]

    # Add file search tool if vectorstore IDs provided
    tools = (
        [
            {
                "type": "file_search",
                "vector_store_ids": vec_ids,
                "max_num_results": 5,
            }
        ]
        if vec_ids
        else None
    )

    # Track events
    event_count = {}
    reasoning_found = False

    try:
        async for event_type, event_data in astream_response(
            input_messages=input_messages,
            model=model,
            effort=effort,
            store=False,
            tools=tools,
            debug=False,
        ):
            # Count event types
            event_count[event_type] = event_count.get(event_type, 0) + 1

            # Log the event
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{timestamp}] EVENT: {event_type}")

            # Log event data based on type
            if event_data:
                # Special handling for different event types
                if event_type == "response.output_item.added":
                    if "item" in event_data:
                        item = event_data["item"]
                        item_type = item.get("type", "unknown")
                        print(f"  └─ Item Type: {item_type}")

                        if item_type == "reasoning":
                            reasoning_found = True
                            print("  └─ 🎯 REASONING FOUND!")
                            if "summary" in item:
                                for i, summary in enumerate(item.get("summary", [])):
                                    if summary.get("type") == "summary_text":
                                        text = summary.get("text", "")
                                        print(f"  └─ Summary[{i}]: {text[:100]}...")

                        elif item_type == "message":
                            role = item.get("role", "unknown")
                            print(f"  └─ Role: {role}")

                elif event_type == "response.output_text.delta":
                    text = event_data.get("text", "")
                    if isinstance(text, str):
                        print(f"  └─ Text: {text[:50]}..." if len(text) > 50 else f"  └─ Text: {text}")

                elif event_type == "response.file_search_call.searching":
                    queries = event_data.get("queries", [])
                    print(f"  └─ Queries: {queries}")

                elif event_type == "response.reasoning_summary_text.delta":
                    reasoning_found = True
                    delta = event_data.get("delta", "")
                    print(f"  └─ 🎯 REASONING DELTA: {delta[:100]}...")

                else:
                    # For other events, show a summary of the data
                    data_str = json.dumps(event_data, ensure_ascii=False)
                    if len(data_str) > 200:
                        print(f"  └─ Data: {data_str[:200]}...")
                    else:
                        print(f"  └─ Data: {data_str}")

            if event_type == "done":
                break

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()

    # Summary
    print(f"\n{'=' * 80}")
    print("📊 Event Summary:")
    for event_type, count in sorted(event_count.items()):
        print(f"  - {event_type}: {count}")

    if reasoning_found:
        print("\n✅ Reasoning events were detected!")
    else:
        print("\n⚠️  No reasoning events detected.")

    print(f"{'=' * 80}\n")


async def main():
    parser = argparse.ArgumentParser(description="Debug event logger for Knowledge Forge streaming")
    parser.add_argument(
        "--question",
        "-q",
        default="Tell me about the reimbursement process",
        help="Question to ask",
    )
    parser.add_argument("--vec-id", action="append", default=None, help="Vector store ID(s)")
    parser.add_argument("--model", "-m", default="qwen-max-latest", help="Model to use")
    parser.add_argument(
        "--effort",
        "-e",
        default="low",
        choices=["low", "medium", "high", "dev"],
        help="Effort level",
    )
    parser.add_argument(
        "--server",
        default=os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999"),
        help="Server URL",
    )

    args = parser.parse_args()

    # Set default vector store if none provided
    if args.vec_id is None:
        args.vec_id = ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]

    # Set server URL if provided
    if args.server != os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999"):
        os.environ["KNOWLEDGE_FORGE_URL"] = args.server
        print(f"🔗 Using server: {args.server}")

    await log_all_events(
        question=args.question,
        vec_ids=args.vec_id,
        model=args.model,
        effort=args.effort,
    )


if __name__ == "__main__":
    asyncio.run(main())
