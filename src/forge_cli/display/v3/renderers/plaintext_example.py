#!/usr/bin/env python3
"""Example usage of the Plaintext renderer for v3 display system."""

from forge_cli.display.v3.renderers.plaintext import PlaintextRenderer, PlaintextDisplayConfig
from forge_cli.display.v3.base import Display


def demo_plaintext_renderer():
    """Demonstrate plaintext renderer with different configurations."""
    print("=== Plaintext Renderer v3 Demo ===\n")

    # Mock response data - in real usage this comes from the API
    from types import SimpleNamespace
    
    mock_response = SimpleNamespace(
        id="resp_plaintext_demo_12345",
        status="completed",
        model="claude-3-sonnet",
        output=[
            SimpleNamespace(
                type="message",
                content=[
                    SimpleNamespace(
                        type="output_text",
                        text="""# Welcome to Knowledge Forge!

This is a **demonstration** of the *plaintext renderer* with Rich Live and Text components.

## Features

- Beautiful colored output using Rich Text
- Live updating display
- Custom styling without panels or markdown components
- Support for `inline code` formatting

### Key Benefits

- Clean, readable output
- Customizable colors and styles
- Efficient live updates
- No complex nested components

Here's a list of features:
- Real-time streaming updates
- Tool execution tracking
- Citation management
- Usage statistics
- Reasoning display

1. First benefit: Simple and clean
2. Second benefit: Highly customizable
3. Third benefit: Performance optimized

This renderer is perfect for environments where you want rich formatting but prefer a simpler visual structure.""",
                        annotations=[
                            SimpleNamespace(
                                type="file_citation",
                                file_name="demo_document.pdf",
                                page_number=1,
                                text="This is a sample citation from the demo document"
                            )
                        ]
                    )
                ]
            ),
            SimpleNamespace(
                type="file_search_call",
                status="completed",
                queries=["knowledge forge", "plaintext renderer"],
                results=["Found 5 relevant documents", "Processed 3 citations"]
            ),
            SimpleNamespace(
                type="reasoning",
                summary=[
                    SimpleNamespace(
                        text="I need to demonstrate the plaintext renderer capabilities by showing various formatting options and features. The renderer should display headers, lists, inline formatting, and tool information in a clean, colorful way."
                    )
                ]
            )
        ],
        usage=SimpleNamespace(
            input_tokens=150,
            output_tokens=75,
            total_tokens=225
        )
    )

    # Example 1: Default configuration
    print("1. Default plaintext renderer:")
    config = PlaintextDisplayConfig()
    renderer = PlaintextRenderer(config=config)
    display = Display(renderer)

    display.handle_response(mock_response)
    display.complete()
    print("\n" + "="*60 + "\n")

    # Example 2: Customized configuration
    print("2. Customized plaintext renderer (minimal):")
    config = PlaintextDisplayConfig(
        show_reasoning=False,
        show_tool_details=False,
        show_status_header=False,
        separator_char="═",
        separator_length=40,
        indent_size=4
    )
    renderer = PlaintextRenderer(config=config)
    display = Display(renderer)

    display.handle_response(mock_response)
    display.complete()
    print("\n" + "="*60 + "\n")

    # Example 3: Chat mode demonstration
    print("3. Chat mode with welcome message:")
    config = PlaintextDisplayConfig(show_metadata=True)
    renderer = PlaintextRenderer(config=config, in_chat_mode=True)
    display = Display(renderer, mode="chat")

    # Show welcome message
    mock_config = SimpleNamespace(
        model="claude-3-sonnet",
        enabled_tools=["file_search", "web_search", "document_finder"]
    )
    renderer.render_welcome(mock_config)
    
    # Show request info
    renderer.render_request_info({
        "question": "How does the plaintext renderer work?",
        "model": "claude-3-sonnet",
        "tools": ["file_search", "web_search"]
    })
    
    # Show status
    renderer.render_status("Processing your request...")
    
    # Show response
    display.handle_response(mock_response)
    display.complete()
    print("\n" + "="*60 + "\n")

    # Example 4: Error handling demonstration
    print("4. Error handling:")
    renderer = PlaintextRenderer()
    renderer.render_error("This is a demonstration error message")
    print()

    print("=== Demo Complete ===")


def demo_style_customization():
    """Demonstrate style customization capabilities."""
    print("=== Style Customization Demo ===\n")
    
    # Create a custom renderer with modified styles
    renderer = PlaintextRenderer()
    
    # Override some styles for demonstration
    renderer._styles.update({
        "header": "bold magenta",
        "content": "bright_white",
        "separator": "dim cyan",
        "tool_icon": "bright_yellow",
        "citation_ref": "bold green",
    })
    
    # Mock simple response
    from types import SimpleNamespace
    
    simple_response = SimpleNamespace(
        id="style_demo_123",
        status="completed", 
        model="claude-3-sonnet",
        output=[
            SimpleNamespace(
                type="message",
                content=[
                    SimpleNamespace(
                        type="output_text",
                        text="# Custom Styled Output\n\nThis demonstrates **custom styling** with *different colors*!",
                        annotations=[]
                    )
                ]
            )
        ],
        usage=SimpleNamespace(input_tokens=20, output_tokens=10, total_tokens=30)
    )
    
    display = Display(renderer)
    display.handle_response(simple_response)
    display.complete()
    
    print("\n=== Style Demo Complete ===")


if __name__ == "__main__":
    demo_plaintext_renderer()
    print("\n" + "="*80 + "\n")
    demo_style_customization() 