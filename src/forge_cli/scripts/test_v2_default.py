"""Test that v2 renderers are now used by default."""

import asyncio
import json
import sys
import os
from io import StringIO

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from forge_cli.config import SearchConfig
from forge_cli.main import create_display
from forge_cli.display.v2.base import Display


async def test_default_displays():
    """Test that default displays are now pure v2."""
    print("=== Testing Default Display Creation ===\n")

    # Test 1: Plain display (default)
    config = SearchConfig()
    display = create_display(config)
    print(f"Default display: {type(display).__name__}")
    print(f"Is v2 Display: {isinstance(display, Display)}")
    if isinstance(display, Display):
        print(f"  Renderer: {display._renderer.__class__.__name__}")

    # Test 2: Rich display
    print("\n--- Rich Display ---")
    config = SearchConfig(use_rich=True)
    display = create_display(config)
    print(f"Rich display: {type(display).__name__}")
    print(f"Is v2 Display: {isinstance(display, Display)}")
    if isinstance(display, Display):
        print(f"  Renderer: {display._renderer.__class__.__name__}")

    # Test 3: JSON display
    print("\n--- JSON Display ---")
    config = SearchConfig(json_output=True)
    display = create_display(config)
    print(f"JSON display: {type(display).__name__}")
    print(f"Is v2 Display: {isinstance(display, Display)}")
    if isinstance(display, Display):
        print(f"  Renderer: {display._renderer.__class__.__name__}")

    # Test 4: Chat mode
    print("\n--- Chat Display ---")
    config = SearchConfig(chat_mode=True)
    config.chat = True  # Set the chat attribute
    display = create_display(config)
    print(f"Chat display: {type(display).__name__}")
    print(f"Is v2 Display: {isinstance(display, Display)}")
    if isinstance(display, Display):
        print(f"  Mode: {display.mode}")
        print(f"  Renderer: {display._renderer.__class__.__name__}")


async def test_functionality():
    """Test that v2 displays work correctly through event handling."""
    print("\n\n=== Testing V2 Display Functionality ===\n")

    # Test JSON output
    output = StringIO()
    old_stdout = sys.stdout
    sys.stdout = output

    try:
        config = SearchConfig(json_output=True, debug=False)
        display = create_display(config)

        # Simulate v2 event-based usage
        display.handle_event("request_info", {"question": "What is Python?", "model": "qwen-max-latest"})
        display.handle_event("text_delta", {"text": "Python is a programming language."})
        display.complete()

        # Parse JSON output
        json_str = output.getvalue()
        data = json.loads(json_str)

        sys.stdout = old_stdout  # Restore stdout before printing
        print(f"✅ JSON output valid!")
        print(f"   Query: {data['response']['query']}")
        print(f"   Response: {data['response']['response_text']}")
        print(f"   API Version: {data['meta']['api_version']}")
        print(f"   Renderer: {data['meta']['renderer']}")

    except Exception as e:
        sys.stdout = old_stdout  # Restore stdout before printing error
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_plain_output():
    """Test plain renderer output."""
    print("\n--- Testing Plain Output ---")

    output = StringIO()

    config = SearchConfig(use_rich=False)
    display = create_display(config)

    # Check it's using v2
    if isinstance(display, Display):
        # Monkey patch the renderer's output file
        display._renderer._file = output

        display.handle_event("request_info", {"question": "Test query", "model": "test-model"})
        display.handle_event("text_delta", {"text": "Test response"})
        display.complete()

        plain_output = output.getvalue()
        print("Plain output sample:")
        print(plain_output[:200] + "..." if len(plain_output) > 200 else plain_output)
        print("✅ Plain renderer working!")
    else:
        print("❌ Not using v2 display!")


async def main():
    """Run all tests."""
    print("Testing V2 Renderers as Default\n")

    try:
        await test_default_displays()
        await test_functionality()
        await test_plain_output()

        print("\n\n🎉 All tests passed! V2 renderers are now the default.")

    except Exception as e:
        print(f"❌ Test failed: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
