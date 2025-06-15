"""Tests for API compatibility between dict-based and typed APIs."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

from forge_cli.response._types import (
    Request,
    InputMessage,
    Response,
    ResponseOutputMessage,
    ResponseTextDeltaEvent,
    FileSearchTool,
    WebSearchTool,
)
from forge_cli.response.migration_helpers import MigrationHelper
from forge_cli.processors.registry_typed import TypedProcessorRegistry
from forge_cli.stream.handler_typed import TypedStreamHandler, StreamState


class TestMigrationHelpers:
    """Test migration helper utilities."""
    
    def test_is_typed_response(self):
        """Test response type detection."""
        # Dict response
        dict_response = {"id": "123", "output": []}
        assert not MigrationHelper.is_typed_response(dict_response)
        
        # Typed response
        typed_response = Response(id="123", output=[])
        assert MigrationHelper.is_typed_response(typed_response)
    
    def test_safe_get_text(self):
        """Test text extraction from both formats."""
        # Dict format
        dict_event = {"text": "Hello world"}
        assert MigrationHelper.safe_get_text(dict_event) == "Hello world"
        
        # Typed format
        typed_event = ResponseTextDeltaEvent(text="Hello typed")
        assert MigrationHelper.safe_get_text(typed_event) == "Hello typed"
        
        # Missing text
        assert MigrationHelper.safe_get_text({}) == ""
        assert MigrationHelper.safe_get_text(None) == ""
    
    def test_safe_get_type(self):
        """Test type extraction."""
        # Dict format
        assert MigrationHelper.safe_get_type({"type": "message"}) == "message"
        
        # Typed format with type attribute
        typed_item = MagicMock()
        typed_item.type = "reasoning"
        assert MigrationHelper.safe_get_type(typed_item) == "reasoning"
        
        # Missing type
        assert MigrationHelper.safe_get_type({}) is None
    
    def test_convert_tool_to_typed(self):
        """Test tool conversion."""
        # File search tool
        dict_tool = {
            "type": "file_search",
            "vector_store_ids": ["vs_123"],
            "max_num_results": 10
        }
        typed_tool = MigrationHelper.convert_tool_to_typed(dict_tool)
        assert isinstance(typed_tool, FileSearchTool)
        assert typed_tool.vector_store_ids == ["vs_123"]
        assert typed_tool.max_num_results == 10
        
        # Web search tool
        dict_tool = {
            "type": "web_search",
            "country": "US",
            "city": "NYC"
        }
        typed_tool = MigrationHelper.convert_tool_to_typed(dict_tool)
        assert isinstance(typed_tool, WebSearchTool)
        assert typed_tool.country == "US"
        assert typed_tool.city == "NYC"
    
    def test_convert_message_to_typed(self):
        """Test message conversion."""
        dict_msg = {"role": "user", "content": "Hello"}
        typed_msg = MigrationHelper.convert_message_to_typed(dict_msg)
        assert isinstance(typed_msg, InputMessage)
        assert typed_msg.role == "user"
        assert typed_msg.content == "Hello"


class TestProcessorCompatibility:
    """Test that processors work with both dict and typed items."""
    
    @pytest.fixture
    def registry(self):
        """Create initialized registry."""
        from forge_cli.processors.registry_typed import initialize_typed_registry
        initialize_typed_registry()
        return TypedProcessorRegistry()
    
    def test_reasoning_processor_compatibility(self, registry):
        """Test reasoning processor with both formats."""
        processor = registry.get_processor("reasoning")
        assert processor is not None
        
        # Mock state and display
        state = MagicMock()
        display = MagicMock()
        
        # Dict format
        dict_item = {
            "type": "reasoning",
            "summary": [{"text": "Thinking..."}]
        }
        processor.process(dict_item, state, display)
        
        # Typed format
        typed_item = MagicMock()
        typed_item.type = "reasoning"
        typed_item.summary = [MagicMock(text="Typed thinking...")]
        processor.process(typed_item, state, display)
    
    def test_message_processor_compatibility(self, registry):
        """Test message processor with both formats."""
        processor = registry.get_processor("message")
        assert processor is not None
        
        state = MagicMock()
        display = MagicMock()
        
        # Dict format
        dict_item = {
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "Hello"}]
        }
        processor.process(dict_item, state, display)
        
        # Typed format
        typed_item = ResponseOutputMessage(
            type="message",
            role="assistant",
            content=[MagicMock(type="text", text="Typed hello")]
        )
        processor.process(typed_item, state, display)


class TestStreamHandlerCompatibility:
    """Test stream handler with both APIs."""
    
    @pytest.mark.asyncio
    async def test_typed_stream_handler(self):
        """Test TypedStreamHandler with typed responses."""
        display = MagicMock()
        handler = TypedStreamHandler(display)
        
        # Create mock typed stream
        async def mock_stream():
            response = Response(
                id="test_123",
                output=[ResponseOutputMessage(
                    type="message",
                    role="assistant",
                    content=[]
                )]
            )
            yield "response.created", response
            yield "response.completed", response
            yield "done", None
        
        # Process stream
        state = await handler.handle_stream(mock_stream(), "test query")
        
        # Verify state
        assert state.response_id == "test_123"
        assert len(state.output_items) == 1
        assert display.handle_response.called
    
    @pytest.mark.asyncio
    async def test_stream_state_compatibility(self):
        """Test StreamState with both dict and typed items."""
        state = StreamState()
        
        # Add dict item
        dict_item = {"type": "message", "content": "Hello"}
        state.output_items.append(dict_item)
        
        # Add typed item
        typed_item = ResponseOutputMessage(
            type="message",
            role="assistant",
            content=[]
        )
        state.output_items.append(typed_item)
        
        # Both should coexist
        assert len(state.output_items) == 2
        assert MigrationHelper.safe_get_type(state.output_items[0]) == "message"
        assert MigrationHelper.safe_get_type(state.output_items[1]) == "message"


class TestChatControllerCompatibility:
    """Test chat controller with typed API."""
    
    @pytest.mark.asyncio
    async def test_prepare_typed_tools(self):
        """Test typed tool preparation."""
        from forge_cli.chat.controller import ChatController
        from forge_cli.config import SearchConfig
        
        config = SearchConfig(
            vec_ids=["vs_123"],
            enabled_tools=["file-search", "web-search"]
        )
        display = MagicMock()
        controller = ChatController(config, display)
        
        # Get typed tools
        typed_tools = controller.prepare_typed_tools()
        
        # Verify tools
        assert len(typed_tools) == 2
        assert isinstance(typed_tools[0], FileSearchTool)
        assert isinstance(typed_tools[1], WebSearchTool)
        assert typed_tools[0].vector_store_ids == ["vs_123"]
    
    def test_extract_text_from_typed_response(self):
        """Test text extraction from typed responses."""
        from forge_cli.chat.controller import ChatController
        
        controller = ChatController(MagicMock(), MagicMock())
        
        # Create mock typed response
        response = MagicMock()
        response.output = [
            MagicMock(
                type="message",
                content=[
                    MagicMock(type="text", text="Hello from typed API")
                ]
            )
        ]
        
        # Extract text
        text = controller.extract_text_from_typed_response(response)
        assert text == "Hello from typed API"


class TestEndToEndCompatibility:
    """Test end-to-end compatibility scenarios."""
    
    @pytest.mark.asyncio
    async def test_mixed_processor_handling(self):
        """Test handling mixed dict and typed items in same stream."""
        display = MagicMock()
        handler = TypedStreamHandler(display)
        
        # Create mixed stream
        async def mixed_stream():
            # Start with typed response
            response1 = Response(id="test_1", output=[])
            yield "response.created", response1
            
            # Mix in dict-based event
            yield "response.output_text.delta", {"text": "Hello "}
            
            # Back to typed
            response2 = Response(
                id="test_1",
                output=[ResponseOutputMessage(
                    type="message",
                    role="assistant",
                    content=[MagicMock(type="text", text="Hello world")]
                )]
            )
            yield "response.completed", response2
            yield "done", None
        
        # Should handle gracefully
        state = await handler.handle_stream(mixed_stream(), "test")
        assert state.response_id == "test_1"


# Integration test example
@pytest.mark.asyncio
async def test_full_migration_compatibility():
    """Test that migrated code produces equivalent results."""
    from forge_cli.sdk import astream_response, astream_typed_response
    
    query = "Test query"
    model = "qwen-max-latest"
    
    # Mock the actual API calls
    with patch('forge_cli.sdk.astream_response') as mock_dict_api:
        with patch('forge_cli.sdk.astream_typed_response') as mock_typed_api:
            # Set up mock responses
            async def dict_stream():
                yield "response.output_text.delta", {"text": "Result"}
                yield "response.completed", {"id": "123"}
            
            async def typed_stream():
                yield "response.output_text.delta", MagicMock(text="Result")
                yield "response.completed", Response(id="123", output=[])
            
            mock_dict_api.return_value = dict_stream()
            mock_typed_api.return_value = typed_stream()
            
            # Collect results from both APIs
            dict_results = []
            async for event_type, data in await mock_dict_api(
                input_messages=query,
                model=model
            ):
                if "text.delta" in event_type:
                    dict_results.append(data.get("text", ""))
            
            typed_results = []
            request = Request(
                input=[InputMessage(role="user", content=query)],
                model=model
            )
            async for event_type, data in await mock_typed_api(request):
                if "text.delta" in event_type:
                    typed_results.append(MigrationHelper.safe_get_text(data))
            
            # Results should be equivalent
            assert dict_results == typed_results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])