#!/usr/bin/env python3
"""Test script for chat mode functionality."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from hello_file_search_refactored.config import SearchConfig
from hello_file_search_refactored.display.plain_display import PlainDisplay
from hello_file_search_refactored.chat.controller import ChatController
from hello_file_search_refactored.processors.registry import initialize_default_registry


async def test_basic_chat():
    """Test basic chat functionality."""
    print("=== Testing Basic Chat ===")
    
    # Initialize registry
    initialize_default_registry()
    
    # Create config
    config = SearchConfig()
    config.enabled_tools = ["web-search"]
    config.model = "qwen-max-latest"
    
    # Create display
    display = PlainDisplay()
    
    # Create controller
    controller = ChatController(config, display)
    
    # Test sending a message
    print("\nSending test message...")
    await controller.send_message("Hello, can you help me?")
    
    print("\n✅ Basic chat test completed")


async def test_command_parsing():
    """Test command parsing."""
    print("\n=== Testing Command Parsing ===")
    
    from hello_file_search_refactored.chat.commands import CommandRegistry
    
    registry = CommandRegistry()
    
    # Test various inputs
    test_cases = [
        ("/help", ("help", "")),
        ("/save my_file.json", ("save", "my_file.json")),
        ("/tools add web-search", ("tools", "add web-search")),
        ("//help", (None, "/help")),  # Escaped command
        ("Hello world", (None, "Hello world")),  # Regular message
    ]
    
    for input_text, expected in test_cases:
        result = registry.parse_command(input_text)
        print(f"Input: '{input_text}' -> {result}")
        assert result == expected, f"Expected {expected}, got {result}"
    
    print("✅ Command parsing test completed")


async def test_conversation_state():
    """Test conversation state management."""
    print("\n=== Testing Conversation State ===")
    
    from hello_file_search_refactored.models.conversation import ConversationState
    
    # Create conversation
    conv = ConversationState(model="test-model")
    
    # Add messages
    conv.add_user_message("Hello")
    conv.add_assistant_message("Hi there!")
    conv.add_user_message("How are you?")
    
    # Test message count
    assert conv.get_message_count() == 3
    print(f"Message count: {conv.get_message_count()}")
    
    # Test API format
    api_format = conv.to_api_format()
    assert len(api_format) == 3
    assert api_format[0]["role"] == "user"
    assert api_format[0]["content"] == "Hello"
    print("API format conversion: ✅")
    
    # Test save/load
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        temp_path = Path(f.name)
    
    conv.save(temp_path)
    loaded_conv = ConversationState.load(temp_path)
    
    assert loaded_conv.get_message_count() == 3
    assert loaded_conv.model == "test-model"
    print("Save/load: ✅")
    
    # Clean up
    temp_path.unlink()
    
    print("✅ Conversation state test completed")


async def main():
    """Run all tests."""
    print("Running chat mode tests...\n")
    
    await test_command_parsing()
    await test_conversation_state()
    
    # Note: test_basic_chat() requires API connection
    # Uncomment to test with actual API
    # await test_basic_chat()
    
    print("\n✅ All tests completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())