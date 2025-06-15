#!/usr/bin/env python3
"""Example script demonstrating the typed API for Knowledge Forge.

This script shows how to use the new typed API with full type safety
and better IDE support compared to the dict-based API.
"""

import asyncio
from typing import List
from forge_cli.response._types import (
    Request,
    InputMessage,
    FileSearchTool,
    WebSearchTool,
    Response,
    ResponseOutputMessage,
    ResponseFileSearchToolCall,
    ResponseWebSearchToolCall,
)
from forge_cli.response.migration_helpers import MigrationHelper
from forge_cli.sdk import astream_typed_response


async def basic_example():
    """Basic example with simple text query."""
    print("=== Basic Typed API Example ===\n")
    
    # Create a typed request
    request = Request(
        input=[InputMessage(role="user", content="What is machine learning?")],
        model="qwen-max-latest",
        temperature=0.7,
        max_output_tokens=500,
    )
    
    # Stream the response
    complete_text = []
    async for event_type, response in astream_typed_response(request):
        # Handle text streaming
        if event_type == "response.output_text.delta" and response:
            # Extract text safely using migration helper
            text = MigrationHelper.safe_get_text(response)
            print(text, end="", flush=True)
            complete_text.append(text)
        
        # Handle completion
        elif event_type == "response.completed" and isinstance(response, Response):
            print(f"\n\nModel: {response.model}")
            print(f"Response ID: {response.id}")
            if response.usage:
                print(f"Tokens: {response.usage.total_tokens}")
    
    print("\n" + "="*50 + "\n")


async def tool_example():
    """Example using file search and web search tools."""
    print("=== Typed API with Tools Example ===\n")
    
    # Create tools with typed API
    tools = [
        FileSearchTool(
            type="file_search",
            vector_store_ids=["vs_example123"],
            max_num_results=5,
        ),
        WebSearchTool(
            type="web_search",
            country="US",
            city="San Francisco",
        ),
    ]
    
    # Create request with tools
    request = Request(
        input=[InputMessage(role="user", content="Find information about RAG systems")],
        model="qwen-max-latest",
        tools=tools,
        temperature=0.5,
    )
    
    # Track tool executions
    tool_results = {}
    
    async for event_type, response in astream_typed_response(request):
        # Handle tool execution events
        if "searching" in event_type:
            print(f"🔍 Tool searching: {event_type}")
        
        elif "completed" in event_type and response:
            # Extract tool results from response
            if isinstance(response, Response):
                for item in response.output:
                    if isinstance(item, ResponseFileSearchToolCall):
                        results = MigrationHelper.safe_get_results(item)
                        tool_results["file_search"] = len(results)
                        print(f"📄 File search found {len(results)} results")
                    
                    elif isinstance(item, ResponseWebSearchToolCall):
                        results = MigrationHelper.safe_get_results(item)
                        tool_results["web_search"] = len(results)
                        print(f"🌐 Web search found {len(results)} results")
        
        # Handle final response
        elif event_type == "response.completed" and isinstance(response, Response):
            print("\n📊 Summary:")
            print(f"  - Tools used: {len(tool_results)}")
            for tool, count in tool_results.items():
                print(f"  - {tool}: {count} results")
    
    print("\n" + "="*50 + "\n")


async def conversation_example():
    """Example with multi-turn conversation."""
    print("=== Typed API Conversation Example ===\n")
    
    # Build conversation history
    messages = [
        InputMessage(role="system", content="You are a helpful AI assistant."),
        InputMessage(role="user", content="What is Python?"),
        InputMessage(role="assistant", content="Python is a high-level, interpreted programming language..."),
        InputMessage(role="user", content="What are its main use cases?"),
    ]
    
    # Create request with conversation
    request = Request(
        input=messages,
        model="qwen-max-latest",
        temperature=0.7,
    )
    
    # Process response
    async for event_type, response in astream_typed_response(request):
        if event_type == "response.output_text.delta" and response:
            text = MigrationHelper.safe_get_text(response)
            print(text, end="", flush=True)
        
        elif event_type == "response.completed":
            print("\n")
    
    print("\n" + "="*50 + "\n")


async def advanced_example():
    """Advanced example showing response processing."""
    print("=== Advanced Typed API Example ===\n")
    
    request = Request(
        input=[InputMessage(
            role="user", 
            content="Analyze the benefits of using typed APIs over dict-based APIs"
        )],
        model="qwen-max-latest",
        effort="high",  # Use high effort for detailed analysis
    )
    
    # Collect response data
    reasoning_text = []
    message_text = []
    
    async for event_type, response in astream_typed_response(request):
        if isinstance(response, Response):
            # Process different output types
            for item in response.output:
                # Check if it's reasoning
                if MigrationHelper.is_reasoning_item(item):
                    if hasattr(item, "summary"):
                        for summary_item in item.summary:
                            if hasattr(summary_item, "text"):
                                reasoning_text.append(summary_item.text)
                
                # Check if it's a message
                elif MigrationHelper.is_message_item(item):
                    if isinstance(item, ResponseOutputMessage):
                        # Extract text from content
                        text = MigrationHelper.extract_text_from_typed_response(response)
                        if text:
                            message_text.append(text)
    
    # Display collected information
    if reasoning_text:
        print("💭 Reasoning Process:")
        print("  " + " ".join(reasoning_text)[:200] + "...")
        print()
    
    if message_text:
        print("📝 Final Response:")
        print("  " + " ".join(message_text))
    
    print("\n" + "="*50 + "\n")


async def main():
    """Run all examples."""
    print("\n🚀 Knowledge Forge Typed API Examples\n")
    print("This demonstrates the new typed API with full type safety.\n")
    
    # Run examples
    await basic_example()
    await tool_example()
    await conversation_example()
    await advanced_example()
    
    print("✅ All examples completed!\n")


if __name__ == "__main__":
    asyncio.run(main())