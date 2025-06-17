"""Tests for response type guards."""

from unittest.mock import Mock

from forge_cli.response import type_guards


class TestToolCallTypeGuards:
    """Test tool call type guards."""

    def test_is_message_item(self):
        """Test message item type guard."""
        mock_item = Mock()
        mock_item.type = "message"
        assert type_guards.is_message_item(mock_item)

        mock_item.type = "file_search_call"
        assert not type_guards.is_message_item(mock_item)

    def test_is_reasoning_item(self):
        """Test reasoning item type guard."""
        mock_item = Mock()
        mock_item.type = "reasoning"
        assert type_guards.is_reasoning_item(mock_item)

        mock_item.type = "message"
        assert not type_guards.is_reasoning_item(mock_item)

    def test_is_file_search_call(self):
        """Test file search call type guard."""
        mock_item = Mock()
        mock_item.type = "file_search_call"
        assert type_guards.is_file_search_call(mock_item)

        mock_item.type = "web_search_call"
        assert not type_guards.is_file_search_call(mock_item)

    def test_is_web_search_call(self):
        """Test web search call type guard."""
        mock_item = Mock()
        mock_item.type = "web_search_call"
        assert type_guards.is_web_search_call(mock_item)

        mock_item.type = "file_search_call"
        assert not type_guards.is_web_search_call(mock_item)

    def test_is_list_documents_call(self):
        """Test list documents call type guard."""
        mock_item = Mock()
        mock_item.type = "list_documents_call"
        assert type_guards.is_list_documents_call(mock_item)

        mock_item.type = "file_search_call"
        assert not type_guards.is_list_documents_call(mock_item)

    def test_is_file_reader_call(self):
        """Test file reader call type guard."""
        mock_item = Mock()
        mock_item.type = "file_reader_call"
        assert type_guards.is_file_reader_call(mock_item)

        mock_item.type = "file_search_call"
        assert not type_guards.is_file_reader_call(mock_item)

    def test_is_page_reader_call(self):
        """Test page reader call type guard."""
        mock_item = Mock()
        mock_item.type = "page_reader_call"
        assert type_guards.is_page_reader_call(mock_item)

        mock_item.type = "file_reader_call"
        assert not type_guards.is_page_reader_call(mock_item)

    def test_is_computer_tool_call(self):
        """Test computer tool call type guard."""
        mock_item = Mock()
        mock_item.type = "computer_call"
        assert type_guards.is_computer_tool_call(mock_item)

        mock_item.type = "function_call"
        assert not type_guards.is_computer_tool_call(mock_item)

    def test_is_function_call(self):
        """Test function call type guard."""
        mock_item = Mock()
        mock_item.type = "function_call"
        assert type_guards.is_function_call(mock_item)

        mock_item.type = "computer_call"
        assert not type_guards.is_function_call(mock_item)

    def test_is_code_interpreter_call(self):
        """Test code interpreter call type guard."""
        mock_item = Mock()
        mock_item.type = "code_interpreter_call"
        assert type_guards.is_code_interpreter_call(mock_item)

        mock_item.type = "function_call"
        assert not type_guards.is_code_interpreter_call(mock_item)


class TestAnnotationTypeGuards:
    """Test annotation type guards."""

    def test_is_file_citation(self):
        """Test file citation type guard."""
        mock_annotation = Mock()
        mock_annotation.type = "file_citation"
        assert type_guards.is_file_citation(mock_annotation)

        mock_annotation.type = "url_citation"
        assert not type_guards.is_file_citation(mock_annotation)

        # Test with object without type attribute
        mock_no_type = Mock(spec=[])
        assert not type_guards.is_file_citation(mock_no_type)

    def test_is_url_citation(self):
        """Test URL citation type guard."""
        mock_annotation = Mock()
        mock_annotation.type = "url_citation"
        assert type_guards.is_url_citation(mock_annotation)

        mock_annotation.type = "file_citation"
        assert not type_guards.is_url_citation(mock_annotation)

        # Test with object without type attribute
        mock_no_type = Mock(spec=[])
        assert not type_guards.is_url_citation(mock_no_type)

    def test_is_file_path(self):
        """Test file path type guard."""
        mock_annotation = Mock()
        mock_annotation.type = "file_path"
        assert type_guards.is_file_path(mock_annotation)

        mock_annotation.type = "file_citation"
        assert not type_guards.is_file_path(mock_annotation)

        # Test with object without type attribute
        mock_no_type = Mock(spec=[])
        assert not type_guards.is_file_path(mock_no_type)


class TestToolUtilityFunctions:
    """Test tool utility functions."""

    def test_get_tool_queries(self):
        """Test getting queries from tool items."""
        # File search call
        mock_file_search = Mock()
        mock_file_search.type = "file_search_call"
        mock_file_search.queries = ["query1", "query2"]
        assert type_guards.get_tool_queries(mock_file_search) == ["query1", "query2"]

        # Web search call
        mock_web_search = Mock()
        mock_web_search.type = "web_search_call"
        mock_web_search.queries = ["web_query"]
        assert type_guards.get_tool_queries(mock_web_search) == ["web_query"]

        # Computer tool call (no queries)
        mock_computer = Mock()
        mock_computer.type = "computer_call"
        assert type_guards.get_tool_queries(mock_computer) == []

        # Unknown type
        mock_unknown = Mock()
        mock_unknown.type = "unknown_type"
        assert type_guards.get_tool_queries(mock_unknown) == []

    def test_get_tool_results(self):
        """Test getting results from tool items."""
        # File search call
        mock_file_search = Mock()
        mock_file_search.type = "file_search_call"
        mock_file_search.results = ["result1", "result2"]
        assert type_guards.get_tool_results(mock_file_search) == ["result1", "result2"]

        # Computer tool call (no results)
        mock_computer = Mock()
        mock_computer.type = "computer_call"
        assert type_guards.get_tool_results(mock_computer) == []

        # Unknown type
        mock_unknown = Mock()
        mock_unknown.type = "unknown_type"
        assert type_guards.get_tool_results(mock_unknown) == []

    def test_get_tool_content(self):
        """Test getting content from tool items."""
        # File reader call
        mock_file_reader = Mock()
        mock_file_reader.type = "file_reader_call"
        mock_file_reader.content = "file content"
        assert type_guards.get_tool_content(mock_file_reader) == "file content"

        # Code interpreter call
        mock_code_interpreter = Mock()
        mock_code_interpreter.type = "code_interpreter_call"
        mock_code_interpreter.code = "print('hello')"
        assert type_guards.get_tool_content(mock_code_interpreter) == "print('hello')"

        # Computer tool call (no content)
        mock_computer = Mock()
        mock_computer.type = "computer_call"
        assert type_guards.get_tool_content(mock_computer) is None

        # Unknown type
        mock_unknown = Mock()
        mock_unknown.type = "unknown_type"
        assert type_guards.get_tool_content(mock_unknown) is None

    def test_get_tool_function_name(self):
        """Test getting function name from tool items."""
        # Function call
        mock_function = Mock()
        mock_function.type = "function_call"
        mock_function.name = "test_function"
        assert type_guards.get_tool_function_name(mock_function) == "test_function"

        # Computer tool call (no function name)
        mock_computer = Mock()
        mock_computer.type = "computer_call"
        assert type_guards.get_tool_function_name(mock_computer) is None

    def test_get_tool_arguments(self):
        """Test getting arguments from tool items."""
        # Function call
        mock_function = Mock()
        mock_function.type = "function_call"
        mock_function.arguments = '{"param": "value"}'
        assert type_guards.get_tool_arguments(mock_function) == '{"param": "value"}'

        # Computer tool call (no arguments)
        mock_computer = Mock()
        mock_computer.type = "computer_call"
        assert type_guards.get_tool_arguments(mock_computer) is None


class TestContentTypeGuards:
    """Test content type guards."""

    def test_is_output_text(self):
        """Test output text type guard."""
        mock_content = Mock()
        mock_content.type = "output_text"
        assert type_guards.is_output_text(mock_content)

        mock_content.type = "refusal"
        assert not type_guards.is_output_text(mock_content)

        # Test with object without type attribute
        mock_no_type = Mock(spec=[])
        assert not type_guards.is_output_text(mock_no_type)

    def test_is_output_refusal(self):
        """Test output refusal type guard."""
        mock_content = Mock()
        mock_content.type = "refusal"
        assert type_guards.is_output_refusal(mock_content)

        mock_content.type = "output_text"
        assert not type_guards.is_output_refusal(mock_content)

    def test_is_input_text(self):
        """Test input text type guard."""
        mock_content = Mock()
        mock_content.type = "input_text"
        assert type_guards.is_input_text(mock_content)

        mock_content.type = "input_image"
        assert not type_guards.is_input_text(mock_content)

    def test_is_input_image(self):
        """Test input image type guard."""
        mock_content = Mock()
        mock_content.type = "input_image"
        assert type_guards.is_input_image(mock_content)

        mock_content.type = "input_text"
        assert not type_guards.is_input_image(mock_content)

    def test_is_input_file(self):
        """Test input file type guard."""
        mock_content = Mock()
        mock_content.type = "input_file"
        assert type_guards.is_input_file(mock_content)

        mock_content.type = "input_text"
        assert not type_guards.is_input_file(mock_content)


class TestStreamEventTypeGuards:
    """Test stream event type guards."""

    def test_is_response_created_event(self):
        """Test response created event type guard."""
        mock_event = Mock()
        mock_event.type = "response.created"
        assert type_guards.is_response_created_event(mock_event)

        mock_event.type = "response.completed"
        assert not type_guards.is_response_created_event(mock_event)

    def test_is_response_completed_event(self):
        """Test response completed event type guard."""
        mock_event = Mock()
        mock_event.type = "response.completed"
        assert type_guards.is_response_completed_event(mock_event)

        mock_event.type = "response.created"
        assert not type_guards.is_response_completed_event(mock_event)

    def test_is_text_delta_event(self):
        """Test text delta event type guard."""
        mock_event = Mock()
        mock_event.type = "response.text.delta"
        assert type_guards.is_text_delta_event(mock_event)

        mock_event.type = "response.text.done"
        assert not type_guards.is_text_delta_event(mock_event)

    def test_is_code_interpreter_events(self):
        """Test code interpreter event type guards."""
        mock_event = Mock()

        mock_event.type = "response.code_interpreter_call.in_progress"
        assert type_guards.is_code_interpreter_call_in_progress_event(mock_event)

        mock_event.type = "response.code_interpreter_call.interpreting"
        assert type_guards.is_code_interpreter_call_interpreting_event(mock_event)

        mock_event.type = "response.code_interpreter_call.completed"
        assert type_guards.is_code_interpreter_call_completed_event(mock_event)

        mock_event.type = "response.code_interpreter_call.code.delta"
        assert type_guards.is_code_interpreter_call_code_delta_event(mock_event)

        mock_event.type = "response.code_interpreter_call.code.done"
        assert type_guards.is_code_interpreter_call_code_done_event(mock_event)


class TestStatusAndErrorGuards:
    """Test status and error type guards."""

    def test_status_guards(self):
        """Test status type guards."""
        assert type_guards.is_response_completed_status("completed")
        assert not type_guards.is_response_completed_status("failed")

        assert type_guards.is_response_failed_status("failed")
        assert not type_guards.is_response_failed_status("completed")

        assert type_guards.is_response_in_progress_status("in_progress")
        assert not type_guards.is_response_in_progress_status("completed")

        assert type_guards.is_response_incomplete_status("incomplete")
        assert not type_guards.is_response_incomplete_status("completed")

    def test_is_response_error(self):
        """Test response error type guard."""
        mock_error = Mock()
        mock_error.code = "error_code"
        mock_error.message = "error message"
        assert type_guards.is_response_error(mock_error)

        # Test with object missing attributes
        mock_incomplete = Mock(spec=["code"])  # Only has code, not message
        assert not type_guards.is_response_error(mock_incomplete)

    def test_tool_call_status_guards(self):
        """Test tool call status guards."""
        mock_tool = Mock()

        mock_tool.status = "completed"
        assert type_guards.is_tool_call_completed(mock_tool)
        assert not type_guards.is_tool_call_in_progress(mock_tool)
        assert not type_guards.is_tool_call_failed(mock_tool)

        mock_tool.status = "in_progress"
        assert type_guards.is_tool_call_in_progress(mock_tool)
        assert not type_guards.is_tool_call_completed(mock_tool)

        mock_tool.status = "failed"
        assert type_guards.is_tool_call_failed(mock_tool)
        assert not type_guards.is_tool_call_completed(mock_tool)

        mock_tool.status = "searching"
        assert type_guards.is_tool_call_searching(mock_tool)

        mock_tool.status = "interpreting"
        assert type_guards.is_tool_call_interpreting(mock_tool)

        # Test with object without status attribute
        mock_no_status = Mock(spec=[])
        assert not type_guards.is_tool_call_completed(mock_no_status)


class TestUtilityFunctions:
    """Test utility functions."""

    def test_safe_get_attr(self):
        """Test safe attribute getter."""

        # Create a real object instead of Mock to test proper attribute access
        class TestObj:
            existing_attr = "value"

        test_obj = TestObj()

        assert type_guards.safe_get_attr(test_obj, "existing_attr") == "value"
        assert type_guards.safe_get_attr(test_obj, "non_existing_attr") is None
        assert type_guards.safe_get_attr(test_obj, "non_existing_attr", "default") == "default"

    def test_get_content_text(self):
        """Test getting text from content."""
        mock_output_text = Mock()
        mock_output_text.type = "output_text"
        mock_output_text.text = "output text"
        assert type_guards.get_content_text(mock_output_text) == "output text"

        mock_input_text = Mock()
        mock_input_text.type = "input_text"
        mock_input_text.text = "input text"
        assert type_guards.get_content_text(mock_input_text) == "input text"

        mock_other = Mock()
        mock_other.type = "other"
        assert type_guards.get_content_text(mock_other) is None

    def test_get_content_refusal(self):
        """Test getting refusal from content."""
        mock_refusal = Mock()
        mock_refusal.type = "refusal"
        mock_refusal.refusal = "refusal text"
        assert type_guards.get_content_refusal(mock_refusal) == "refusal text"

        mock_other = Mock()
        mock_other.type = "output_text"
        assert type_guards.get_content_refusal(mock_other) is None

    def test_get_error_message_and_code(self):
        """Test getting error message and code."""
        mock_error = Mock()
        mock_error.code = "error_code"
        mock_error.message = "error message"

        assert type_guards.get_error_message(mock_error) == "error message"
        assert type_guards.get_error_code(mock_error) == "error_code"

        mock_non_error = Mock(spec=[])
        assert type_guards.get_error_message(mock_non_error) is None
        assert type_guards.get_error_code(mock_non_error) is None


class TestHighLevelTypeGuards:
    """Test high-level type guard functions."""

    def test_is_any_tool_call(self):
        """Test any tool call type guard."""
        mock_file_search = Mock()
        mock_file_search.type = "file_search_call"
        assert type_guards.is_any_tool_call(mock_file_search)

        mock_computer = Mock()
        mock_computer.type = "computer_call"
        assert type_guards.is_any_tool_call(mock_computer)

        mock_message = Mock()
        mock_message.type = "message"
        assert not type_guards.is_any_tool_call(mock_message)

    def test_is_search_related_tool_call(self):
        """Test search-related tool call type guard."""
        mock_file_search = Mock()
        mock_file_search.type = "file_search_call"
        assert type_guards.is_search_related_tool_call(mock_file_search)

        mock_web_search = Mock()
        mock_web_search.type = "web_search_call"
        assert type_guards.is_search_related_tool_call(mock_web_search)

        mock_computer = Mock()
        mock_computer.type = "computer_call"
        assert not type_guards.is_search_related_tool_call(mock_computer)

    def test_is_execution_tool_call(self):
        """Test execution tool call type guard."""
        mock_computer = Mock()
        mock_computer.type = "computer_call"
        assert type_guards.is_execution_tool_call(mock_computer)

        mock_code_interpreter = Mock()
        mock_code_interpreter.type = "code_interpreter_call"
        assert type_guards.is_execution_tool_call(mock_code_interpreter)

        mock_file_search = Mock()
        mock_file_search.type = "file_search_call"
        assert not type_guards.is_execution_tool_call(mock_file_search)


class TestComputerActionTypeGuards:
    """Test computer action type guards."""

    def test_computer_action_guards(self):
        """Test computer action type guards."""
        actions = [
            ("click", type_guards.is_computer_action_click),
            ("double_click", type_guards.is_computer_action_double_click),
            ("drag", type_guards.is_computer_action_drag),
            ("keypress", type_guards.is_computer_action_keypress),
            ("move", type_guards.is_computer_action_move),
            ("screenshot", type_guards.is_computer_action_screenshot),
            ("scroll", type_guards.is_computer_action_scroll),
            ("type", type_guards.is_computer_action_type),
            ("wait", type_guards.is_computer_action_wait),
        ]

        for action_type, guard_func in actions:
            mock_action = Mock()
            mock_action.type = action_type
            assert guard_func(mock_action), f"Failed for {action_type}"

            # Test with different type
            mock_action.type = "different_type"
            assert not guard_func(mock_action), f"False positive for {action_type}"


class TestComprehensiveGetters:
    """Test comprehensive getter functions."""

    def test_get_event_type(self):
        """Test getting event type."""
        mock_event = Mock()
        mock_event.type = "response.created"
        assert type_guards.get_event_type(mock_event) == "response.created"

        mock_no_type = Mock(spec=[])
        assert type_guards.get_event_type(mock_no_type) is None

    def test_get_tool_call_info(self):
        """Test getting tool call information."""
        mock_tool = Mock()
        mock_tool.id = "tool_id"
        mock_tool.status = "completed"
        mock_tool.type = "file_search_call"

        assert type_guards.get_tool_call_id(mock_tool) == "tool_id"
        assert type_guards.get_tool_call_status(mock_tool) == "completed"
        assert type_guards.get_tool_call_type(mock_tool) == "file_search_call"

        mock_incomplete = Mock(spec=[])
        assert type_guards.get_tool_call_id(mock_incomplete) is None
        assert type_guards.get_tool_call_status(mock_incomplete) is None
        assert type_guards.get_tool_call_type(mock_incomplete) is None
