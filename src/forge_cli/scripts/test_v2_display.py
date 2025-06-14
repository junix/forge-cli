"""Test script for v2 display system with backward compatibility."""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from forge_cli.config import SearchConfig
from forge_cli.display.factory import create_compatible_display, determine_display_api_version
from forge_cli.display.v2.events import EventType


async def test_v1_interface_with_v2_backend():
    """Test that v1 interface works with v2 backend via adapter."""
    print("=== Testing V1 Interface with V2 Backend ===")

    # Create config with v2 enabled
    config = SearchConfig()
    config.use_new_display_api = True
    config.display_api_debug = True
    config.use_rich = False  # Use plain renderer

    # Create display (should be V1ToV2Adapter wrapping v2 Display)
    display = create_compatible_display(config)
    print(f"Display type: {type(display).__name__}")

    # Test v1 interface methods
    await display.show_request_info(
        {"question": "What is the weather today?", "model": "qwen-max-latest", "effort": "low"}
    )

    await display.show_status("Searching for weather information...")

    await display.update_content("The weather today is ")
    await display.update_content("sunny with a high of 75°F.")

    await display.finalize({"id": "test_response_123", "usage": {"total_tokens": 42}}, None)

    print("\n✅ V1 interface test completed successfully!\n")


async def test_v2_interface_directly():
    """Test v2 interface directly without adapter."""
    print("=== Testing V2 Interface Directly ===")

    from forge_cli.display.v2.base import Display
    from forge_cli.display.v2.renderers.plain import PlainRenderer

    # Create v2 display directly
    renderer = PlainRenderer()
    display = Display(renderer)

    # Test v2 event-based interface
    display.handle_event(EventType.STREAM_START.value, {"query": "Tell me about Python programming"})

    display.handle_event(EventType.REASONING_START.value, {})
    display.handle_event(EventType.REASONING_DELTA.value, {"text": "The user is asking about Python programming..."})
    display.handle_event(EventType.REASONING_COMPLETE.value, {})

    display.handle_event(EventType.TOOL_START.value, {"tool_id": "search_001", "tool_type": "web_search"})

    display.handle_event(
        EventType.TOOL_COMPLETE.value, {"tool_id": "search_001", "tool_type": "web_search", "results_count": 5}
    )

    display.handle_event(
        EventType.TEXT_DELTA.value, {"text": "Python is a high-level, interpreted programming language "}
    )
    display.handle_event(EventType.TEXT_DELTA.value, {"text": "known for its simplicity and readability."})

    display.handle_event(
        EventType.CITATION_FOUND.value,
        {"citation_num": 1, "citation_text": "Python was created by Guido van Rossum", "source": "python.org"},
    )

    display.complete()

    print(f"\n✅ V2 interface test completed! Handled {display.event_count} events.\n")


async def test_auto_version_selection():
    """Test automatic version selection based on config."""
    print("=== Testing Auto Version Selection ===")

    configs = [
        (SearchConfig(use_rich=False, quiet=True), "Should use v2 for plain text"),
        (SearchConfig(json_output=True), "Should use v1 for JSON (not implemented in v2 yet)"),
        (SearchConfig(use_rich=True), "Should use v1 for Rich (not implemented in v2 yet)"),
    ]

    for config, description in configs:
        determine_display_api_version(config)
        print(f"{description}: v2={config.use_new_display_api}")

    print("\n✅ Auto version selection test completed!\n")


async def main():
    """Run all tests."""
    print("Testing V2 Display System\n")

    try:
        await test_v1_interface_with_v2_backend()
        await test_v2_interface_directly()
        await test_auto_version_selection()

        print("🎉 All tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
