"""Test script for v2 Rich and JSON renderers."""

import asyncio
import json
import os
import sys
from io import StringIO

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from forge_cli.config import SearchConfig
from forge_cli.display.factory import create_compatible_display, create_display
from forge_cli.display.v2.base import Display
from forge_cli.display.v2.events import EventType
from forge_cli.display.v2.renderers.json import JsonRenderer
from forge_cli.display.v2.renderers.rich import RichRenderer


async def test_json_renderer():
    """Test JSON renderer output."""
    print("=== Testing JSON Renderer ===")

    # Create JSON renderer with output to string
    output = StringIO()
    renderer = JsonRenderer(file=output, include_events=True, pretty=True)
    display = Display(renderer)

    # Simulate a complete stream
    display.handle_event(
        EventType.STREAM_START.value,
        {"query": "What is machine learning?", "model": "qwen-max-latest", "effort": "low", "temperature": 0.7},
    )

    display.handle_event(EventType.REASONING_START.value, {})
    display.handle_event(EventType.REASONING_DELTA.value, {"text": "The user is asking about machine learning..."})
    display.handle_event(EventType.REASONING_COMPLETE.value, {})

    display.handle_event(
        EventType.TOOL_START.value,
        {"tool_id": "search_001", "tool_type": "web_search", "parameters": {"query": "machine learning definition"}},
    )

    display.handle_event(EventType.TOOL_COMPLETE.value, {"tool_id": "search_001", "results_count": 3})

    display.handle_event(
        EventType.TEXT_DELTA.value, {"text": "Machine learning is a subset of artificial intelligence "}
    )
    display.handle_event(EventType.TEXT_DELTA.value, {"text": "that enables systems to learn from data."})

    display.handle_event(
        EventType.CITATION_FOUND.value,
        {
            "citation_num": 1,
            "citation_text": "Machine learning is a method of data analysis",
            "source": "wikipedia.org",
            "url": "https://en.wikipedia.org/wiki/Machine_learning",
        },
    )

    display.handle_event(EventType.STREAM_END.value, {"usage": {"total_tokens": 150}})

    display.complete()

    # Parse and validate JSON output
    json_output = output.getvalue()
    try:
        data = json.loads(json_output)
        print("✅ JSON output is valid!")
        print(f"  - Response text: {len(data['response']['response_text'])} chars")
        print(f"  - Citations: {len(data['response']['citations'])}")
        print(f"  - Tools used: {len(data['response']['tools'])}")
        print(f"  - Events recorded: {len(data.get('events', []))}")

        # Show a sample of the output
        print("\nSample output structure:")
        print(
            json.dumps(
                {
                    "response": {
                        "status": data["response"]["status"],
                        "query": data["response"]["query"],
                        "response_text": data["response"]["response_text"][:50] + "...",
                        "tools": list(data["response"]["tools"].keys()),
                        "citations": [f"Citation {c['number']}" for c in data["response"]["citations"]],
                    },
                    "meta": data["meta"],
                },
                indent=2,
            )
        )

    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        print("Output:", json_output[:200])


async def test_rich_renderer():
    """Test Rich renderer (visual test)."""
    print("\n=== Testing Rich Renderer ===")
    print("(This is a visual test - check the output)")

    try:
        from rich.console import Console

        console = Console()

        # Test with captured output for validation
        renderer = RichRenderer(console=console, show_reasoning=True)
        display = Display(renderer)

        # Simulate a stream with various events
        display.handle_event(
            EventType.STREAM_START.value,
            {"query": "Explain quantum computing", "model": "qwen-max-latest", "effort": "high"},
        )

        # Add some delay for visual effect
        await asyncio.sleep(0.5)

        display.handle_event(EventType.REASONING_START.value, {})
        display.handle_event(
            EventType.REASONING_DELTA.value, {"text": "Quantum computing is a complex topic that involves..."}
        )

        await asyncio.sleep(0.5)

        display.handle_event(EventType.TOOL_START.value, {"tool_id": "file_001", "tool_type": "file_search"})

        await asyncio.sleep(1)

        display.handle_event(EventType.TOOL_COMPLETE.value, {"tool_id": "file_001", "results_count": 5})

        display.handle_event(
            EventType.TEXT_DELTA.value, {"text": "Quantum computing uses quantum mechanical phenomena "}
        )
        await asyncio.sleep(0.3)
        display.handle_event(EventType.TEXT_DELTA.value, {"text": "like superposition and entanglement "})
        await asyncio.sleep(0.3)
        display.handle_event(EventType.TEXT_DELTA.value, {"text": "to perform computations."})

        display.handle_event(
            EventType.CITATION_FOUND.value,
            {
                "citation_num": 1,
                "citation_text": "Quantum bits can exist in multiple states",
                "source": "quantum_basics.pdf",
                "file_name": "quantum_basics.pdf",
                "page_number": 12,
            },
        )

        await asyncio.sleep(0.5)

        display.complete()

        print("\n✅ Rich renderer test completed!")

    except ImportError:
        print("❌ Rich library not available - skipping visual test")


async def test_factory_with_new_renderers():
    """Test factory creates correct v2 renderers."""
    print("\n=== Testing Factory with New Renderers ===")

    # Test JSON renderer creation
    config = SearchConfig(json_output=True, use_new_display_api=True, debug=True)
    display = create_display(config)
    print(f"JSON config -> {display._renderer.__class__.__name__}")

    # Test Rich renderer creation
    config = SearchConfig(use_rich=True, use_new_display_api=True)
    display = create_display(config)
    print(f"Rich config -> {display._renderer.__class__.__name__}")

    # Test Plain renderer creation
    config = SearchConfig(use_rich=False, use_new_display_api=True)
    display = create_display(config)
    print(f"Plain config -> {display._renderer.__class__.__name__}")

    print("\n✅ Factory test completed!")


async def test_v1_compatibility_with_new_renderers():
    """Test v1 interface works with new v2 renderers."""
    print("\n=== Testing V1 Compatibility with New Renderers ===")

    # Test with JSON renderer
    output = StringIO()

    config = SearchConfig(json_output=True, use_new_display_api=True)

    # Monkey patch sys.stdout temporarily
    old_stdout = sys.stdout
    sys.stdout = output

    try:
        display = create_compatible_display(config)

        # Use v1 interface
        await display.show_request_info({"question": "Test question", "model": "test-model"})

        await display.update_content("Test response content")

        await display.finalize({}, None)

        # Check JSON output
        json_str = output.getvalue()
        data = json.loads(json_str)

        assert data["response"]["query"] == "Test question"
        assert data["response"]["response_text"] == "Test response content"

        print("✅ V1 compatibility test passed!")

    finally:
        sys.stdout = old_stdout


async def main():
    """Run all renderer tests."""
    print("Testing V2 Renderers\n")

    try:
        await test_json_renderer()
        await test_rich_renderer()
        await test_factory_with_new_renderers()
        await test_v1_compatibility_with_new_renderers()

        print("\n🎉 All renderer tests completed!")

    except Exception as e:
        print(f"❌ Test failed: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
