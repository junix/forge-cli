#!/usr/bin/env python3
"""
Example showing migration from dict-based API to typed API.

This demonstrates how to gradually adopt the new typed system
while maintaining backward compatibility.
"""

import asyncio
from typing import Dict, Any
from forge_cli.sdk import (
    astream_response,
    async_create_response,
    async_create_typed_response,
    create_typed_request,
)
from forge_cli.response.adapters import ResponseAdapter
from forge_cli.response._types import Request, Response


async def old_style_example():
    """Example using the old dict-based API."""
    print("\n=== Old Style (Dict-based) API ===\n")
    
    # Old style with dicts
    response = await async_create_response(
        input_messages="What is machine learning?",
        model="qwen-max-latest",
        temperature=0.7,
    )
    
    if response:
        # Manual dict navigation
        output = response.get("output", [])
        for item in output:
            if item.get("type") == "message":
                content = item.get("content", [])
                for c in content:
                    if c.get("type") == "output_text":
                        print(f"Response: {c.get('text', '')}")


async def new_style_example():
    """Example using the new typed API."""
    print("\n=== New Style (Typed) API ===\n")
    
    # New style with types
    request = create_typed_request(
        input_messages="What is machine learning?",
        model="qwen-max-latest",
        temperature=0.7,
    )
    
    response = await async_create_typed_response(request)
    
    # Type-safe navigation with IDE support
    for item in response.output or []:
        if item.type == "message" and hasattr(item, 'content'):
            for content in item.content:
                if hasattr(content, 'text'):
                    print(f"Response: {content.text}")


async def migration_wrapper_example():
    """Example showing how to wrap old code with types."""
    print("\n=== Migration Wrapper Example ===\n")
    
    # Existing dict-based response from old code
    old_response_dict = await async_create_response(
        input_messages="Explain neural networks",
        model="qwen-max-latest",
    )
    
    if old_response_dict:
        # Convert to typed response
        typed_response = ResponseAdapter.from_dict(old_response_dict)
        
        # Now use with type safety
        print(f"Response ID: {typed_response.id}")
        print(f"Model: {typed_response.model}")
        
        # Can convert back if needed
        dict_again = ResponseAdapter.to_dict(typed_response)
        print(f"Converted back to dict: {type(dict_again)}")


async def gradual_migration_example():
    """Example showing gradual migration in streaming."""
    print("\n=== Gradual Migration in Streaming ===\n")
    
    # Start with dict-based streaming
    print("Dict-based streaming:")
    async for event_type, event_data in astream_response(
        input_messages="Count to 5",
        model="qwen-max-latest",
        typed=False,  # Explicitly use dict mode
    ):
        if event_type == "response.output_text.delta" and event_data:
            print(event_data.get("text", ""), end="", flush=True)
        elif event_type == "done":
            break
    
    print("\n\nTyped streaming:")
    # Same code, but with typed=True
    async for event_type, event_data in astream_response(
        input_messages="Count to 5 again",
        model="qwen-max-latest",
        typed=True,  # Use typed mode
    ):
        if event_type == "response.output_text.delta" and event_data:
            # event_data is now a typed ResponseTextDeltaEvent
            print(event_data.text, end="", flush=True)
        elif event_type == "done":
            break


async def compatibility_layer_example():
    """Example showing how to maintain compatibility."""
    print("\n\n=== Compatibility Layer Example ===\n")
    
    class CompatibleAPI:
        """API that accepts both old and new style calls."""
        
        async def create_response(
            self,
            input_data: Any,
            **kwargs
        ) -> Response:
            """Accept various input formats."""
            
            # Handle different input types
            if isinstance(input_data, Request):
                # Already typed
                request = input_data
            elif isinstance(input_data, str):
                # Simple string input
                request = create_typed_request(input_data, **kwargs)
            elif isinstance(input_data, list):
                # List of messages
                request = create_typed_request(input_data, **kwargs)
            elif isinstance(input_data, dict):
                # Full request dict
                request = Request(**input_data)
            else:
                raise ValueError(f"Unsupported input type: {type(input_data)}")
            
            # Always return typed response
            return await async_create_typed_response(request)
    
    # Use the compatible API
    api = CompatibleAPI()
    
    # Works with string
    response1 = await api.create_response("Hello")
    print(f"String input: {response1.id}")
    
    # Works with typed request
    typed_req = create_typed_request("Hello again")
    response2 = await api.create_response(typed_req)
    print(f"Typed input: {response2.id}")
    
    # Works with dict
    response3 = await api.create_response(
        {"input": [{"role": "user", "content": "Hello dict"}], "model": "qwen-max-latest"}
    )
    print(f"Dict input: {response3.id}")


async def type_checking_benefits():
    """Show benefits of type checking."""
    print("\n=== Type Checking Benefits ===\n")
    
    # With types, IDEs can catch errors
    request = create_typed_request(
        input_messages="Show me type safety",
        model="qwen-max-latest",
    )
    
    # IDE knows all available fields
    print("Available request fields:")
    print(f"  - model: {request.model}")
    print(f"  - temperature: {request.temperature}")
    print(f"  - effort: {request.effort}")
    print(f"  - tools: {len(request.tools or [])} tools")
    
    # Type errors are caught early
    # This would be flagged by type checker:
    # request.model = 123  # Type error!
    # request.tools = "not a list"  # Type error!
    
    # Correct usage is clear
    request.temperature = 0.5  # OK
    request.effort = "high"    # OK


async def main():
    """Run all migration examples."""
    print("Migration from Dict-based to Typed API")
    print("======================================")
    
    await old_style_example()
    await new_style_example()
    await migration_wrapper_example()
    await gradual_migration_example()
    await compatibility_layer_example()
    await type_checking_benefits()
    
    print("\n\nMigration examples completed!")
    print("\nKey takeaways:")
    print("1. Old dict-based code continues to work")
    print("2. New typed API provides better IDE support")
    print("3. Gradual migration is possible")
    print("4. Adapters help bridge old and new code")
    print("5. Type safety catches errors early")


if __name__ == "__main__":
    asyncio.run(main())