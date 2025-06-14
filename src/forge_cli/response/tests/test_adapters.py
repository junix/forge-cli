import unittest
from unittest.mock import MagicMock, patch

# Assuming the types are Pydantic models or similar,
# we might need to mock them or use actual instances for testing.
# For simplicity, we'll use dicts where possible and mock complex objects.
from forge_cli.response._types import (
    FileSearchTool as ActualFileSearchTool,
    InputMessage as ActualInputMessage,
    Request as ActualRequest,
    Response as ActualResponse,
    ResponseStreamEvent as ActualResponseStreamEvent,
    WebSearchTool as ActualWebSearchTool,
    ResponseCreatedEvent,  # Assuming this and other specific events exist
    ResponseTextDeltaEvent,
)
from forge_cli.response.adapters import (
    ResponseAdapter,
    StreamEventAdapter,
    ToolAdapter,
)

# Mock Pydantic models for testing purposes if they are complex to instantiate directly
# For this example, we'll assume they can be instantiated with kwargs or have simple fields.


class MockPydanticModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def model_dump(self, by_alias=False, exclude_none=False):
        # Simplified mock, real Pydantic model_dump is more complex
        d = self.__dict__.copy()
        if exclude_none:
            d = {k: v for k, v in d.items() if v is not None}
        # `by_alias` is not easily mocked here without field alias info
        return d

    def as_openai_chat_request(self):
        # Simplified mock for Request's method
        return {"messages": self.input, "model": self.model, "tools": self.tools}


class TestResponseAdapter(unittest.TestCase):
    def test_from_dict_to_response(self):
        response_dict = {"id": "res_123", "status": "completed", "model": "test-model", "output": []}
        # Patching 'Response' from the _types module where it's defined and imported by adapters
        with patch("forge_cli.response.adapters.Response", new=MockPydanticModel) as MockResponse:
            MockResponse.return_value = MockPydanticModel(**response_dict)
            response_obj = ResponseAdapter.from_dict(response_dict)
            self.assertIsInstance(response_obj, MockPydanticModel)
            self.assertEqual(response_obj.id, "res_123")

    def test_to_dict_from_response(self):
        # Using the actual Response type if it's simple enough, or mock it
        mock_response_obj = MockPydanticModel(id="res_123", status="completed", model="test-model", output=[])

        response_dict = ResponseAdapter.to_dict(mock_response_obj)
        self.assertEqual(response_dict["id"], "res_123")
        self.assertEqual(response_dict["status"], "completed")

    def test_create_request_with_string_input(self):
        with patch("forge_cli.response.adapters.Request", new=MockPydanticModel) as MockRequest:
            MockRequest.return_value = MockPydanticModel(
                input=[{"role": "user", "content": "Hello"}], model="test-model", tools=[]
            )
            request_obj = ResponseAdapter.create_request("Hello", model="test-model")
            self.assertIsInstance(request_obj, MockPydanticModel)
            self.assertEqual(request_obj.input[0]["content"], "Hello")
            self.assertEqual(request_obj.model, "test-model")

    def test_create_request_with_list_of_dicts(self):
        messages = [{"role": "user", "content": "Test message"}]
        with patch("forge_cli.response.adapters.Request", new=MockPydanticModel) as MockRequest:
            MockRequest.return_value = MockPydanticModel(input=messages, model="gpt-4", tools=[])
            request_obj = ResponseAdapter.create_request(messages, model="gpt-4")
            self.assertIsInstance(request_obj, MockPydanticModel)
            self.assertEqual(request_obj.input[0]["content"], "Test message")

    def test_create_request_with_input_message_objects(self):
        # Assuming InputMessage can be instantiated or is a dict-like structure
        messages = [ActualInputMessage(role="user", content="Test InputMessage")]
        with patch("forge_cli.response.adapters.Request", new=MockPydanticModel) as MockRequest:
            # The actual Request model would convert InputMessage objects to dicts if needed.
            # Our mock needs to simulate this if the input to MockPydanticModel expects dicts.
            # For simplicity, assume MockPydanticModel can take InputMessage objects or they are dict-like.
            input_as_dicts = [{"role": m.role, "content": m.content} for m in messages]
            MockRequest.return_value = MockPydanticModel(input=input_as_dicts, model="claude-2", tools=[])

            request_obj = ResponseAdapter.create_request(messages, model="claude-2")
            self.assertIsInstance(request_obj, MockPydanticModel)
            self.assertEqual(request_obj.input[0]["content"], "Test InputMessage")

    def test_create_request_with_tools(self):
        tools = [{"type": "function", "function": {"name": "get_weather"}}]
        with patch("forge_cli.response.adapters.Request", new=MockPydanticModel) as MockRequest:
            MockRequest.return_value = MockPydanticModel(
                input=[{"role": "user", "content": "hi"}], model="test", tools=tools
            )
            request_obj = ResponseAdapter.create_request("hi", model="test", tools=tools)
            self.assertIsInstance(request_obj, MockPydanticModel)
            self.assertEqual(len(request_obj.tools), 1)
            self.assertEqual(request_obj.tools[0]["function"]["name"], "get_weather")

    def test_request_to_openai_format(self):
        # Assume Request object has an 'as_openai_chat_request' method
        mock_request_obj = MockPydanticModel(input=[{"role": "user", "content": "Test"}], model="gpt-3.5", tools=[])

        openai_dict = ResponseAdapter.request_to_openai_format(mock_request_obj)
        self.assertIn("messages", openai_dict)
        self.assertEqual(openai_dict["messages"][0]["content"], "Test")
        self.assertEqual(openai_dict["model"], "gpt-3.5")


class TestStreamEventAdapter(unittest.TestCase):
    @patch("forge_cli.response._types.ResponseCreatedEvent", new=MockPydanticModel)
    def test_parse_event_response_created(self):
        event_data = {"type": "response.created", "id": "evt_1"}
        parsed_event = StreamEventAdapter.parse_event(event_data)
        self.assertIsInstance(parsed_event, MockPydanticModel)
        self.assertEqual(parsed_event.id, "evt_1")
        # Check if it was instantiated with the correct class (mocked)
        self.assertTrue(hasattr(parsed_event, "type") and parsed_event.type == "response.created")

    @patch("forge_cli.response._types.ResponseTextDeltaEvent", new=MockPydanticModel)
    def test_parse_event_text_delta(self):
        event_data = {"type": "response.output_text.delta", "delta": {"text": "hello"}}
        parsed_event = StreamEventAdapter.parse_event(event_data)
        self.assertIsInstance(parsed_event, MockPydanticModel)
        self.assertTrue(hasattr(parsed_event, "delta"))
        self.assertEqual(parsed_event.delta["text"], "hello")

    # Test fallback to generic ResponseStreamEvent
    @patch("forge_cli.response.adapters.ResponseStreamEvent", new=MockPydanticModel)  # Patch generic
    def test_parse_event_unknown_type(self):
        event_data = {"type": "unknown.event", "custom_field": "value"}
        # We need to ensure _types does not have 'UnknownEvent' to test fallback
        with patch("forge_cli.response.adapters.getattr") as mock_getattr:
            # Make getattr raise AttributeError for "UnknownEvent" to simulate it not being in _types
            def side_effect(module, name):
                if name == "UnknownEvent":  # Assuming event_map would generate this
                    raise AttributeError
                return MagicMock()  # Return a mock for other getattr calls if any

            mock_getattr.side_effect = side_effect

            parsed_event = StreamEventAdapter.parse_event(event_data)
            self.assertIsInstance(parsed_event, MockPydanticModel)  # Falls back to generic ResponseStreamEvent
            self.assertEqual(parsed_event.custom_field, "value")


class TestToolAdapter(unittest.TestCase):
    def test_create_file_search_tool(self):
        # Assuming FileSearchTool can be instantiated or is a dict-like structure
        # For Pydantic models, they validate input.
        vector_store_ids = ["vs_123"]
        tool_obj = ToolAdapter.create_file_search_tool(vector_store_ids, max_search_results=5)
        # The actual FileSearchTool is a Pydantic model.
        # We are testing the adapter correctly constructs the input for it.
        self.assertIsInstance(tool_obj, ActualFileSearchTool)
        self.assertEqual(tool_obj.file_search.vector_store_ids, vector_store_ids)
        self.assertEqual(tool_obj.file_search.max_search_results, 5)

    def test_create_web_search_tool(self):
        # Similar to above, assuming WebSearchTool can be instantiated
        tool_obj = ToolAdapter.create_web_search_tool()
        self.assertIsInstance(tool_obj, ActualWebSearchTool)  # Actual type
        # WebSearchTool might be an empty model, or have default fields.
        # For example, if it's `class WebSearchTool(BaseModel): type: str = "web_search"`,
        # then this test is fine. If it's just `class WebSearchTool(Tool): pass` then also fine.

    def test_tools_to_openai_format(self):
        # This method currently returns the list as-is.
        # The name suggests it should format it, but the implementation does not.
        # Test should reflect current implementation.
        tools_list = [
            ActualFileSearchTool(file_search={"vector_store_ids": ["vs_1"], "max_search_results": 1}),
            ActualWebSearchTool(),
        ]
        # If tools are Pydantic models, they might need to be dicts for OpenAI
        # However, the current implementation of tools_to_openai_format is `return tools`
        # So, the test will pass if it returns the same list of Pydantic models.
        # If the intention is to convert them to dicts, the implementation and test need to change.

        formatted_tools = ToolAdapter.tools_to_openai_format(tools_list)
        self.assertEqual(formatted_tools, tools_list)
        self.assertIsInstance(formatted_tools[0], ActualFileSearchTool)


if __name__ == "__main__":
    unittest.main()
