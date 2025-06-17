#!/usr/bin/env python3
"""
Debug script to reproduce consecutive tool call display issue.

This script will test consecutive tool calls (like list documents -> file reader)
to see if they're being rendered properly in the Rich display.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from forge_cli.display.v3.base import Display
from forge_cli.display.v3.renderers.rich import RichRenderer
from forge_cli.sdk.typed_api import astream_typed_response, create_typed_request


async def test_consecutive_tool_calls():
    """Test consecutive tool calls and observe the display behavior."""

    print("🔬 Testing consecutive tool calls display...")
    print("=" * 60)

    # Create a renderer with debug info enabled
    renderer = RichRenderer(show_tool_details=True)
    display = Display(renderer)

    # Create a typed request that should trigger consecutive tool calls
    # This simulates a scenario where list documents -> file reader might be called
    request = create_typed_request(
        input_messages="Find and read documents about machine learning",
        tools=[{"type": "list_documents", "vector_store_ids": ["vs_123"]}, {"type": "file_reader"}],
        model="qwen-max-latest",
    )

    print(f"📝 Request created with tools: {[tool['type'] for tool in request.tools]}")
    print("🚀 Starting stream...")
    print("=" * 60)

    tool_call_count = 0
    tool_calls_seen = set()

    try:
        async for event_type, response in astream_typed_response(request, debug=True):
            print(f"📨 Event: {event_type}")

            if response and hasattr(response, "output"):
                # Count tool calls in current snapshot
                current_tool_calls = []
                for item in response.output:
                    if hasattr(item, "type") and item.type.endswith("_call"):
                        current_tool_calls.append(item.type)
                        tool_calls_seen.add(f"{item.type}:{getattr(item, 'id', 'no-id')}")

                if current_tool_calls:
                    print(f"  🔧 Tool calls in snapshot: {current_tool_calls}")
                    print(f"  📊 Total unique tool calls seen: {len(tool_calls_seen)}")

                # Render the response
                display.handle_response(response)

            if event_type == "response.completed":
                print("\n✅ Response completed")
                break
            elif event_type.endswith("_call.completed"):
                tool_call_count += 1
                print(f"  ✓ Tool call #{tool_call_count} completed: {event_type}")

    except Exception as e:
        print(f"❌ Error during streaming: {e}")
        import traceback

        traceback.print_exc()

    finally:
        display.complete()
        print("\n📈 Summary:")
        print(f"  - Total tool calls completed: {tool_call_count}")
        print(f"  - Unique tool calls seen: {len(tool_calls_seen)}")
        print(f"  - Tool call IDs: {list(tool_calls_seen)}")


async def test_mock_consecutive_responses():
    """Test with mock consecutive responses to isolate the display issue."""

    print("\n🧪 Testing with mock consecutive responses...")
    print("=" * 60)

    # Import response types
    from forge_cli.response._types.response import Response
    from forge_cli.response._types.response_function_file_reader import ResponseFunctionFileReader
    from forge_cli.response._types.response_list_documents_tool_call import ResponseListDocumentsToolCall
    from forge_cli.response._types.response_output_message import ResponseOutputMessage
    from forge_cli.response._types.response_output_text import ResponseOutputText

    renderer = RichRenderer(show_tool_details=True)
    display = Display(renderer)

    # Mock response 1: List documents call starts
    response1 = Response(
        id="resp_1",
        created_at=1234567890,
        object="response",
        model="qwen-max-latest",
        parallel_tool_calls=True,
        tool_choice="auto",
        tools=[],
        output=[
            ResponseListDocumentsToolCall(
                type="list_documents_call", id="list_123", queries=["machine learning"], count=0, status="in_progress"
            )
        ],
    )

    print("📊 Rendering Response 1: List documents in progress")
    display.handle_response(response1)
    await asyncio.sleep(1)  # Simulate time delay

    # Mock response 2: List documents completes, file reader starts
    response2 = Response(
        id="resp_1",
        created_at=1234567890,
        object="response",
        model="qwen-max-latest",
        parallel_tool_calls=True,
        tool_choice="auto",
        tools=[],
        output=[
            ResponseListDocumentsToolCall(
                type="list_documents_call", id="list_123", queries=["machine learning"], count=3, status="completed"
            ),
            ResponseFunctionFileReader(
                type="file_reader_call",
                id="reader_456",
                doc_ids=["doc_123"],
                query="machine learning",
                status="in_progress",
            ),
        ],
    )

    print("📊 Rendering Response 2: List completed + File reader in progress")
    display.handle_response(response2)
    await asyncio.sleep(1)  # Simulate time delay

    # Mock response 3: Both completed, final message
    response3 = Response(
        id="resp_1",
        created_at=1234567890,
        object="response",
        model="qwen-max-latest",
        parallel_tool_calls=True,
        tool_choice="auto",
        tools=[],
        output=[
            ResponseListDocumentsToolCall(
                type="list_documents_call", id="list_123", queries=["machine learning"], count=3, status="completed"
            ),
            ResponseFunctionFileReader(
                type="file_reader_call",
                id="reader_456",
                doc_ids=["doc_123"],
                query="machine learning",
                status="completed",
            ),
            ResponseOutputMessage(
                type="message",
                id="msg_123",
                role="assistant",
                status="completed",
                content=[
                    ResponseOutputText(
                        type="output_text",
                        text="Based on the documents found about machine learning...",
                        annotations=[],
                    )
                ],
            ),
        ],
    )

    print("📊 Rendering Response 3: All completed + Final message")
    display.handle_response(response3)

    display.complete()
    print("\n✅ Mock test completed")


async def main():
    """Main test function."""

    # Check if we can connect to the API
    forge_url = os.getenv("KNOWLEDGE_FORGE_URL")
    if not forge_url:
        print("⚠️  KNOWLEDGE_FORGE_URL not set, running mock tests only")
        await test_mock_consecutive_responses()
    else:
        print(f"🌐 Using Forge API at: {forge_url}")
        await test_consecutive_tool_calls()
        await test_mock_consecutive_responses()


if __name__ == "__main__":
    asyncio.run(main())
