#!/usr/bin/env python3
"""Example usage of the v3 Rich renderer with the simplified display interface."""

import asyncio
from typing import List

from forge_cli.display.v3.base import Display
from forge_cli.display.v3.renderers.rich import RichRenderer, RichDisplayConfig
from forge_cli.response._types.response import Response
from forge_cli.response._types.response_output_message import ResponseOutputMessage
from forge_cli.response._types.response_output_text import ResponseOutputText
from forge_cli.response._types.response_usage import ResponseUsage


def create_sample_response() -> Response:
    """Create a sample response for demonstration."""

    # Create sample text content with annotations
    text_content = ResponseOutputText(
        text="""# Knowledge Retrieval Systems

Knowledge retrieval systems are designed to find and extract relevant information from large document collections. These systems typically use:

1. **Vector Embeddings**: Convert text to numerical representations
2. **Semantic Search**: Find documents based on meaning, not just keywords  
3. **Ranking Algorithms**: Order results by relevance

The integration of Large Language Models (LLMs) has revolutionized this field by enabling more sophisticated understanding of queries and context.

## Key Benefits

- **Improved Accuracy**: Better understanding of user intent
- **Contextual Results**: Consider broader context beyond keywords
- **Multi-modal Support**: Handle text, images, and other data types

These advances have made knowledge retrieval systems essential for enterprise search, research assistance, and intelligent document processing.""",
        annotations=[],
        type="output_text",
    )

    # Create message with the text content
    message = ResponseOutputMessage(
        id="msg_123456", content=[text_content], role="assistant", status="completed", type="message"
    )

    # Create usage statistics
    usage = ResponseUsage(input_tokens=150, output_tokens=320, total_tokens=470)

    # Create the complete response
    response = Response(
        id="resp_abcdef123456",
        created_at=1706825400.0,
        model="gpt-4o",
        object="response",
        output=[message],
        parallel_tool_calls=True,
        temperature=0.7,
        tool_choice="auto",
        tools=[],
        status="completed",
        usage=usage,
    )

    return response


async def demonstrate_v3_renderer():
    """Demonstrate the v3 rich renderer capabilities."""

    print("🚀 Knowledge Forge v3 Rich Renderer Demo")
    print("=" * 50)

    # Create renderer with custom configuration
    config = RichDisplayConfig(
        show_reasoning=True, show_citations=True, show_tool_details=True, show_usage=True, refresh_rate=8
    )

    renderer = RichRenderer(config=config, in_chat_mode=False)

    # Create display with the renderer
    display = Display(renderer, mode="default")

    # Create sample response
    response = create_sample_response()

    print("\n📋 Rendering sample response with v3 Rich renderer...")
    print("   Notice how everything is available in the single Response object!")

    # This is the beauty of v3 - just one simple method call!
    display.handle_response(response)

    # Simulate streaming updates (multiple snapshots)
    print("\n🔄 Simulating streaming updates...")
    await asyncio.sleep(1)

    # Update response status to show streaming
    response.status = "in_progress"
    display.handle_response(response)

    await asyncio.sleep(1)

    # Final completion
    response.status = "completed"
    display.handle_response(response)

    # Complete the display
    display.complete()

    print("\n✅ Demo completed!")
    print("\nKey v3 Advantages:")
    print("  • Single render_response() method")
    print("  • Complete Response object contains everything")
    print("  • No complex event routing or state management")
    print("  • Resilient to missed events (snapshot-based)")
    print("  • Easy to implement new renderers")


async def demonstrate_multiple_renderers():
    """Show how easy it is to switch renderers in v3."""

    print("\n" + "=" * 50)
    print("🔄 Demonstrating renderer flexibility")
    print("=" * 50)

    response = create_sample_response()

    # Rich renderer
    print("\n1️⃣ Rich Renderer:")
    rich_renderer = RichRenderer(config=RichDisplayConfig(show_usage=False))
    rich_display = Display(rich_renderer)
    rich_display.handle_response(response)
    rich_display.complete()

    # Could easily add other renderers:
    # plain_renderer = PlainRenderer()
    # json_renderer = JsonRenderer()
    # html_renderer = HtmlRenderer()

    print("\n💡 In v3, switching renderers is as simple as:")
    print("   Display(RichRenderer())     # Beautiful terminal UI")
    print("   Display(PlainRenderer())    # Simple text output")
    print("   Display(JsonRenderer())     # Structured JSON")
    print("   Display(HtmlRenderer())     # Web-ready HTML")


if __name__ == "__main__":
    asyncio.run(demonstrate_v3_renderer())
    asyncio.run(demonstrate_multiple_renderers())
