#!/usr/bin/env python3
"""Test script to verify v1/v2 display parity."""

import asyncio
from rich.console import Console
from rich.table import Table

from forge_cli.display.v1.rich_display import RichDisplay  # v1
from forge_cli.display.v2.renderers.rich import RichRenderer  # v2
from forge_cli.display.v2.base import Display
from forge_cli.display.v2.adapter import V1ToV2Adapter


async def test_v1_display():
    """Test v1 RichDisplay behavior."""
    print("\n" + "="*60)
    print("Testing v1 RichDisplay")
    print("="*60 + "\n")
    
    console = Console()
    display = RichDisplay(console)
    
    # Test request info
    await display.show_request_info({
        "question": "What is the meaning of life?",
        "vec_ids": ["vs_123", "vs_456"],
        "model": "qwen-max-latest",
        "effort": "medium",
        "tools": ["file-search", "web-search"]
    })
    
    await asyncio.sleep(1)
    
    # Test content updates
    metadata = {
        "event_count": 42,
        "event_type": "response.output_text.delta",
        "usage": {
            "input_tokens": 100,
            "output_tokens": 50,
            "total_tokens": 150
        }
    }
    
    await display.update_content("# Analyzing your question\n\nThe meaning of life is...", metadata)
    await asyncio.sleep(1)
    
    # Test status
    await display.show_status("Processing file search...")
    await asyncio.sleep(1)
    
    # Test rich content
    table = Table(title="Search Results")
    table.add_column("File", style="cyan")
    table.add_column("Score", style="green")
    table.add_row("document1.pdf", "0.95")
    table.add_row("document2.md", "0.87")
    
    await display.show_status_rich(table)
    await asyncio.sleep(1)
    
    # Test error
    await display.show_error("Connection timeout")
    await asyncio.sleep(1)
    
    # Update with final content
    await display.update_content(
        "# The Answer\n\nThe meaning of life is 42, according to Douglas Adams.\n\n"
        "This comes from *The Hitchhiker's Guide to the Galaxy*.",
        metadata
    )
    await asyncio.sleep(1)
    
    # Finalize
    response = {
        "id": "resp_12345",
        "model": "qwen-max-latest",
        "usage": metadata["usage"]
    }
    
    await display.finalize(response, None)


async def test_v2_display():
    """Test v2 RichRenderer with v1 adapter."""
    print("\n" + "="*60)
    print("Testing v2 RichRenderer (via V1ToV2Adapter)")
    print("="*60 + "\n")
    
    console = Console()
    renderer = RichRenderer(console, show_reasoning=True)
    display_v2 = Display(renderer)
    display = V1ToV2Adapter(display_v2)
    
    # Test request info
    await display.show_request_info({
        "question": "What is the meaning of life?",
        "vec_ids": ["vs_123", "vs_456"],
        "model": "qwen-max-latest",
        "effort": "medium",
        "tools": ["file-search", "web-search"]
    })
    
    await asyncio.sleep(1)
    
    # Test content updates
    metadata = {
        "event_count": 42,
        "event_type": "response.output_text.delta",
        "usage": {
            "input_tokens": 100,
            "output_tokens": 50,
            "total_tokens": 150
        }
    }
    
    await display.update_content("# Analyzing your question\n\nThe meaning of life is...", metadata)
    await asyncio.sleep(1)
    
    # Test status
    await display.show_status("Processing file search...")
    await asyncio.sleep(1)
    
    # Test rich content
    table = Table(title="Search Results")
    table.add_column("File", style="cyan")
    table.add_column("Score", style="green")
    table.add_row("document1.pdf", "0.95")
    table.add_row("document2.md", "0.87")
    
    await display.show_status_rich(table)
    await asyncio.sleep(1)
    
    # Test error
    await display.show_error("Connection timeout")
    await asyncio.sleep(1)
    
    # Update with final content
    await display.update_content(
        "# The Answer\n\nThe meaning of life is 42, according to Douglas Adams.\n\n"
        "This comes from *The Hitchhiker's Guide to the Galaxy*.",
        metadata
    )
    await asyncio.sleep(1)
    
    # Finalize
    response = {
        "id": "resp_12345",
        "model": "qwen-max-latest",
        "usage": metadata["usage"]
    }
    
    await display.finalize(response, None)


async def test_chat_mode_v1():
    """Test v1 chat mode features."""
    print("\n" + "="*60)
    print("Testing v1 Chat Mode")
    print("="*60 + "\n")
    
    console = Console()
    display = RichDisplay(console)
    display._in_chat_mode = True
    
    # Mock config
    class MockConfig:
        model = "qwen-max-latest"
        enabled_tools = ["file-search", "web-search"]
    
    config = MockConfig()
    
    # Show welcome
    await display.show_welcome(config)
    await asyncio.sleep(2)
    
    # Simulate conversation
    await display.update_content("Hello! How can I help you today?", None)
    await asyncio.sleep(1)
    
    # Finalize in chat mode (should not show completion info)
    await display.finalize({}, None)


async def test_chat_mode_v2():
    """Test v2 chat mode features."""
    print("\n" + "="*60)
    print("Testing v2 Chat Mode")
    print("="*60 + "\n")
    
    console = Console()
    renderer = RichRenderer(console, show_reasoning=True, in_chat_mode=True)
    display_v2 = Display(renderer, mode="chat")
    display = V1ToV2Adapter(display_v2)
    
    # Mock config
    class MockConfig:
        model = "qwen-max-latest"
        enabled_tools = ["file-search", "web-search"]
    
    config = MockConfig()
    
    # Show welcome
    await display.show_welcome(config)
    await asyncio.sleep(2)
    
    # Simulate conversation
    await display.update_content("Hello! How can I help you today?", None)
    await asyncio.sleep(1)
    
    # Finalize in chat mode (should not show completion info)
    await display.finalize({}, None)


async def main():
    """Run all tests."""
    print("Testing v1/v2 Display Parity")
    print("This will show visual output from both v1 and v2 displays.")
    print("They should look identical.\n")
    
    # Test standard mode
    await test_v1_display()
    await asyncio.sleep(2)
    await test_v2_display()
    
    # Test chat mode
    await asyncio.sleep(2)
    await test_chat_mode_v1()
    await asyncio.sleep(2)
    await test_chat_mode_v2()
    
    print("\n" + "="*60)
    print("Test completed!")
    print("Compare the outputs above - they should be visually identical.")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())