"""Tests for response type guards."""

from unittest.mock import Mock

from forge_cli.response import type_guards
from forge_cli.response._types.response_reasoning_item import ResponseReasoningItem, Summary


class TestReasoningItemText:
    """Test ResponseReasoningItem text property."""

    def test_text_property_with_summary(self):
        """Test text property returns consolidated text from summaries."""
        # Create summary items
        summary1 = Summary(text="First reasoning part", type="summary_text")
        summary2 = Summary(text="Second reasoning part", type="summary_text")
        
        # Create reasoning item
        reasoning_item = ResponseReasoningItem(
            id="test-reasoning-1",
            summary=[summary1, summary2],
            type="reasoning"
        )
        
        # Test text property
        expected_text = "First reasoning part\n\nSecond reasoning part"
        assert reasoning_item.text == expected_text

    def test_text_property_empty_summary(self):
        """Test text property returns empty string when no summary."""
        reasoning_item = ResponseReasoningItem(
            id="test-reasoning-2",
            summary=[],
            type="reasoning"
        )
        
        assert reasoning_item.text == ""

    def test_text_property_with_empty_text(self):
        """Test text property ignores empty or whitespace-only summary text."""
        summary1 = Summary(text="Valid text", type="summary_text")
        summary2 = Summary(text="   ", type="summary_text")  # Whitespace only
        summary3 = Summary(text="", type="summary_text")     # Empty
        summary4 = Summary(text="Another valid text", type="summary_text")
        
        reasoning_item = ResponseReasoningItem(
            id="test-reasoning-3",
            summary=[summary1, summary2, summary3, summary4],
            type="reasoning"
        )
        
        expected_text = "Valid text\n\nAnother valid text"
        assert reasoning_item.text == expected_text


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
