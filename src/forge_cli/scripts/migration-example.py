#!/usr/bin/env python3
"""Example showing migration from dict-based to typed API.

This script demonstrates how to migrate existing code from the legacy
dict-based API to the new typed API, with side-by-side comparisons.
"""

import asyncio
from typing import Dict, Any, List
from forge_cli.sdk import astream_response, astream_typed_response
from forge_cli.response._types import Request, InputMessage, FileSearchTool
from forge_cli.response.migration_helpers import MigrationHelper


async def dict_based_example():
    """Legacy dict-based API example."""
    print("=== Dict-based API (Legacy) ===\n")
    
    # Old way: using dicts
    messages = [{"role": "user", "content": "What is Python?"}]
    tools = [{
        "type": "file_search",
        "vector_store_ids": ["vs_123"],
        "max_num_results": 5
    }]
    
    complete_text = []
    
    async for event_type, event_data in astream_response(
        input_messages=messages,
        model="qwen-max-latest",
        tools=tools,
    ):
        # Old way: accessing dict keys
        if event_type == "response.output_text.delta":
            text = event_data.get("text", "")
            print(text, end="", flush=True)
            complete_text.append(text)
        
        elif event_type == "response.completed":
            # Extract info from dict
            response_id = event_data.get("id")
            usage = event_data.get("usage", {})
            print(f"\n\nResponse ID: {response_id}")
            print(f"Total tokens: {usage.get('total_tokens', 0)}")
    
    return "".join(complete_text)


async def typed_api_example():
    """New typed API example."""
    print("\n\n=== Typed API (New) ===\n")
    
    # New way: using typed objects
    messages = [InputMessage(role="user", content="What is Python?")]
    tools = [FileSearchTool(
        type="file_search",
        vector_store_ids=["vs_123"],
        max_num_results=5
    )]
    
    request = Request(
        input=messages,
        model="qwen-max-latest",
        tools=tools,
    )
    
    complete_text = []
    
    async for event_type, response in astream_typed_response(request):
        # New way: type-safe access
        if event_type == "response.output_text.delta":
            text = MigrationHelper.safe_get_text(response)
            print(text, end="", flush=True)
            complete_text.append(text)
        
        elif event_type == "response.completed" and response:
            # Direct attribute access with IDE support
            print(f"\n\nResponse ID: {response.id}")
            if response.usage:
                print(f"Total tokens: {response.usage.total_tokens}")
    
    return "".join(complete_text)


async def migration_helper_example():
    """Example using migration helpers for compatibility."""
    print("\n\n=== Using Migration Helpers ===\n")
    
    # Function that works with both APIs
    async def process_stream(stream, is_typed=False):
        """Process stream from either API."""
        tool_results = []
        
        async for event_type, data in stream:
            # Migration helper works with both dict and typed
            if MigrationHelper.is_tool_call_item(data):
                tool_id = MigrationHelper.extract_tool_id(data)
                tool_type = MigrationHelper.safe_get_type(data)
                status = MigrationHelper.safe_get_status(data)
                
                print(f"Tool: {tool_type}, ID: {tool_id}, Status: {status}")
                
                # Extract results safely
                results = MigrationHelper.safe_get_results(data)
                if results:
                    tool_results.extend(results)
            
            # Text extraction works for both
            elif "text.delta" in event_type:
                text = MigrationHelper.safe_get_text(data)
                print(text, end="", flush=True)
        
        return tool_results
    
    # Example with dict-based API
    print("Processing with dict-based API:")
    dict_stream = astream_response(
        input_messages="Test query",
        model="qwen-max-latest"
    )
    await process_stream(dict_stream, is_typed=False)
    
    # Example with typed API
    print("\n\nProcessing with typed API:")
    typed_request = Request(
        input=[InputMessage(role="user", content="Test query")],
        model="qwen-max-latest"
    )
    typed_stream = astream_typed_response(typed_request)
    await process_stream(typed_stream, is_typed=True)


async def gradual_migration_example():
    """Example showing gradual migration strategy."""
    print("\n\n=== Gradual Migration Strategy ===\n")
    
    # Step 1: Start with existing dict-based code
    def prepare_request_dict(query: str) -> Dict[str, Any]:
        """Legacy function returning dict."""
        return {
            "input_messages": [{"role": "user", "content": query}],
            "model": "qwen-max-latest",
            "tools": [{"type": "web_search"}]
        }
    
    # Step 2: Add typed wrapper
    def prepare_request_typed(query: str) -> Request:
        """New function returning typed Request."""
        # Reuse logic from dict version
        dict_req = prepare_request_dict(query)
        
        # Convert to typed
        messages = [MigrationHelper.convert_message_to_typed(msg) 
                   for msg in dict_req["input_messages"]]
        tools = [MigrationHelper.convert_tool_to_typed(tool) 
                for tool in dict_req.get("tools", [])]
        
        return Request(
            input=messages,
            model=dict_req["model"],
            tools=tools
        )
    
    # Step 3: Use based on feature flag
    USE_TYPED_API = True  # Feature flag
    
    query = "What are the benefits of static typing?"
    
    if USE_TYPED_API:
        print("Using typed API...")
        request = prepare_request_typed(query)
        stream = astream_typed_response(request)
    else:
        print("Using dict-based API...")
        req_dict = prepare_request_dict(query)
        stream = astream_response(**req_dict)
    
    # Process stream (works with both)
    async for event_type, data in stream:
        if "text.delta" in event_type:
            text = MigrationHelper.safe_get_text(data)
            print(text, end="", flush=True)
    
    print("\n")


async def benefits_comparison():
    """Show benefits of typed API."""
    print("\n\n=== Benefits of Typed API ===\n")
    
    print("1. Type Safety:")
    print("   - Dict API: response['usage']['total_tokens']  # KeyError risk")
    print("   - Typed API: response.usage.total_tokens      # IDE autocomplete")
    
    print("\n2. IDE Support:")
    print("   - Dict API: No autocomplete, no type hints")
    print("   - Typed API: Full autocomplete, inline docs")
    
    print("\n3. Validation:")
    print("   - Dict API: Runtime errors for invalid data")
    print("   - Typed API: Pydantic validation at creation")
    
    print("\n4. Code Example:")
    
    # Typed example with all the benefits
    request = Request(
        input=[
            InputMessage(role="system", content="You are helpful."),
            InputMessage(role="user", content="Hello!")
        ],
        model="qwen-max-latest",  # Autocomplete shows valid models
        temperature=0.7,          # Type hints show float expected
        max_output_tokens=1000,   # IDE shows this is optional
    )
    
    print(f"   Created typed request: {request.model}")
    print(f"   Input messages: {len(request.input)}")
    print(f"   Temperature: {request.temperature}")


async def main():
    """Run all migration examples."""
    print("\n📋 Dict-based to Typed API Migration Examples\n")
    
    # Run examples
    await dict_based_example()
    await typed_api_example()
    await migration_helper_example()
    await gradual_migration_example()
    await benefits_comparison()
    
    print("\n✅ Migration examples completed!")
    print("\nKey Takeaways:")
    print("- Use MigrationHelper for code that needs to support both APIs")
    print("- Gradually migrate by adding typed wrappers")
    print("- New code should use typed API exclusively")
    print("- Keep both APIs working during transition period\n")


if __name__ == "__main__":
    asyncio.run(main())