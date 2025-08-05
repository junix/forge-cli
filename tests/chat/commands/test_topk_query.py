"""Tests for TopKQueryCommand."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from forge_cli.chat.commands.files.topk_query import TopKQueryCommand

# Configure pytest to use anyio for async tests
pytestmark = pytest.mark.anyio


class TestTopKQueryCommand:
    """Test cases for TopKQueryCommand."""

    @pytest.fixture
    def command(self):
        """Create TopKQueryCommand instance."""
        return TopKQueryCommand()

    @pytest.fixture
    def mock_controller(self):
        """Create mock controller."""
        controller = MagicMock()
        controller.display = MagicMock()
        controller.conversation = MagicMock()
        controller.conversation.get_current_vector_store_ids.return_value = ["current_vs_123"]
        return controller

    def test_command_properties(self, command):
        """Test command properties."""
        assert command.name == "topk"
        assert command.description == "Query a collection with top-k results"
        assert "query" in command.aliases
        assert "search" in command.aliases

    async def test_execute_no_args(self, command, mock_controller):
        """Test execute with no arguments."""
        result = await command.execute("", mock_controller)

        assert result is True
        mock_controller.display.show_error.assert_called_once()
        error_call = mock_controller.display.show_error.call_args[0][0]
        assert "Usage:" in error_call

        # Check that both formats are shown in the status messages
        status_calls = [call[0][0] for call in mock_controller.display.show_status.call_args_list]
        assert any("simple format" in call for call in status_calls)
        assert any("flag format" in call for call in status_calls)

    async def test_execute_with_collection_and_query(self, command, mock_controller):
        """Test execute with collection and query."""
        with patch("forge_cli.sdk.vectorstore.async_query_vectorstore") as mock_query:
            # Mock successful query result
            mock_result = MagicMock()
            mock_result.data = [
                MagicMock(
                    id="chunk_1",
                    score=0.95,
                    text="Machine learning is a subset of AI",
                    file_id="file_123",
                    metadata={"source": "ml_paper.pdf"},
                )
            ]
            mock_query.return_value = mock_result

            result = await command.execute('--collection=my_collection --query="machine learning"', mock_controller)

            assert result is True
            mock_query.assert_called_once_with(
                vector_store_id="my_collection",
                query="machine learning",
                top_k=5,  # default value
                filters=None,
            )

    async def test_execute_with_current_collection(self, command, mock_controller):
        """Test execute using current collection (no --collection flag)."""
        with patch("forge_cli.sdk.vectorstore.async_query_vectorstore") as mock_query:
            mock_result = MagicMock()
            mock_result.data = []
            mock_query.return_value = mock_result

            result = await command.execute('--query="test query"', mock_controller)

            assert result is True
            mock_query.assert_called_once_with(
                vector_store_id="current_vs_123",  # from mock_controller
                query="test query",
                top_k=5,
                filters=None,
            )

    async def test_execute_with_custom_top_k(self, command, mock_controller):
        """Test execute with custom top-k value."""
        with patch("forge_cli.sdk.vectorstore.async_query_vectorstore") as mock_query:
            mock_result = MagicMock()
            mock_result.data = []
            mock_query.return_value = mock_result

            result = await command.execute('--collection=test_vs --query="test" --top-k=10', mock_controller)

            assert result is True
            mock_query.assert_called_once_with(vector_store_id="test_vs", query="test", top_k=10, filters=None)

    async def test_execute_no_current_collection(self, command, mock_controller):
        """Test execute with no collection flag and no current collection."""
        mock_controller.conversation.get_current_vector_store_ids.return_value = []

        result = await command.execute('--query="test query"', mock_controller)

        assert result is True
        # Check that the error message contains the expected text
        error_call = mock_controller.display.show_error.call_args[0][0]
        assert "--collection parameter is required (no current collection set)" in error_call
        assert "Use '/use-collection <collection-id>' to set an active collection" in error_call

    def test_parse_flag_parameters_basic(self, command):
        """Test parsing basic flag parameters."""
        args = '--collection=test_vs --query="machine learning" --top-k=5'
        params = command._parse_flag_parameters(args)

        assert params["collection"] == "test_vs"
        assert params["query"] == "machine learning"
        assert params["top-k"] == "5"

    def test_parse_flag_parameters_quoted_values(self, command):
        """Test parsing with quoted values."""
        args = '--collection="my collection" --query="complex query with spaces"'
        params = command._parse_flag_parameters(args)

        assert params["collection"] == "my collection"
        assert params["query"] == "complex query with spaces"

    def test_parse_flag_parameters_unquoted_values(self, command):
        """Test parsing with unquoted values."""
        args = "--collection=simple_vs --query=simple --top-k=3"
        params = command._parse_flag_parameters(args)

        assert params["collection"] == "simple_vs"
        assert params["query"] == "simple"
        assert params["top-k"] == "3"

    def test_parse_flag_parameters_no_flags(self, command):
        """Test parsing with no valid flags."""
        args = "invalid arguments without flags"

        with pytest.raises(ValueError, match="No valid --flag parameters found"):
            command._parse_flag_parameters(args)

    def test_parse_args_missing_query(self, command, mock_controller):
        """Test parsing args with missing query."""
        with pytest.raises(ValueError, match="--query parameter is required"):
            command._parse_args("--collection=test_vs", mock_controller)

    def test_parse_args_invalid_top_k(self, command, mock_controller):
        """Test parsing args with invalid top-k value."""
        with pytest.raises(ValueError, match="Invalid --top-k value"):
            command._parse_args("--collection=test_vs --query=test --top-k=invalid", mock_controller)

    def test_parse_args_negative_top_k(self, command, mock_controller):
        """Test parsing args with negative top-k value."""
        with pytest.raises(ValueError, match="Invalid --top-k value"):
            command._parse_args("--collection=test_vs --query=test --top-k=-1", mock_controller)

    # Tests for simple format
    def test_parse_simple_format_basic(self, command, mock_controller):
        """Test parsing simple format with basic query."""
        collection_id, query, top_k, json_output = command._parse_args("machine learning", mock_controller)

        assert collection_id == "current_vs_123"
        assert query == "machine learning"
        assert top_k == 5
        assert json_output is False

    def test_parse_simple_format_with_spaces(self, command, mock_controller):
        """Test parsing simple format with spaces in query."""
        collection_id, query, top_k, json_output = command._parse_args(
            "neural networks and deep learning", mock_controller
        )

        assert collection_id == "current_vs_123"
        assert query == "neural networks and deep learning"
        assert top_k == 5
        assert json_output is False

    def test_parse_simple_format_no_current_collection(self, command, mock_controller):
        """Test parsing simple format with no current collection."""
        mock_controller.conversation.get_current_vector_store_ids.return_value = []

        with pytest.raises(ValueError, match="No current collection set"):
            command._parse_args("test query", mock_controller)

    def test_parse_simple_format_multiple_collections(self, command, mock_controller):
        """Test parsing simple format with multiple current collections."""
        mock_controller.conversation.get_current_vector_store_ids.return_value = ["vs_1", "vs_2", "vs_3"]

        collection_id, query, top_k, json_output = command._parse_args("test query", mock_controller)

        assert collection_id == "vs_1"  # Uses first collection
        assert query == "test query"
        assert top_k == 5
        assert json_output is False

        # Check that informative message was displayed
        mock_controller.display.show_status.assert_any_call("ℹ️ Using first active collection: vs_1")

    async def test_execute_simple_format(self, command, mock_controller):
        """Test execute with simple format."""
        with patch("forge_cli.sdk.vectorstore.async_query_vectorstore") as mock_query:
            mock_result = MagicMock()
            mock_result.data = []
            mock_query.return_value = mock_result

            result = await command.execute("machine learning techniques", mock_controller)

            assert result is True
            mock_query.assert_called_once_with(
                vector_store_id="current_vs_123", query="machine learning techniques", top_k=5, filters=None
            )

    # Tests for JSON functionality
    def test_parse_flag_parameters_with_json(self, command):
        """Test parsing flag parameters with JSON flag."""
        args = '--collection=test_vs --query="machine learning" --top-k=5 --json'
        params = command._parse_flag_parameters(args)

        assert params["collection"] == "test_vs"
        assert params["query"] == "machine learning"
        assert params["top-k"] == "5"
        assert "json" in params
        assert params["json"] == "true"

    def test_parse_flag_format_with_json(self, command, mock_controller):
        """Test parsing flag format with JSON output."""
        collection_id, query, top_k, json_output = command._parse_args(
            '--collection=test_vs --query="test query" --json', mock_controller
        )

        assert collection_id == "test_vs"
        assert query == "test query"
        assert top_k == 5
        assert json_output is True

    def test_parse_flag_format_without_json(self, command, mock_controller):
        """Test parsing flag format without JSON output."""
        collection_id, query, top_k, json_output = command._parse_args(
            '--collection=test_vs --query="test query"', mock_controller
        )

        assert collection_id == "test_vs"
        assert query == "test query"
        assert top_k == 5
        assert json_output is False

    async def test_execute_with_json_output(self, command, mock_controller):
        """Test execute with JSON output flag."""
        with (
            patch("forge_cli.sdk.vectorstore.async_query_vectorstore") as mock_query,
            patch("builtins.print") as mock_print,
        ):
            # Mock successful query result
            mock_result = MagicMock()
            mock_result.data = [
                MagicMock(
                    file_id="file_123",
                    filename="test.pdf",
                    score=0.95,
                    attributes={"source": "test"},
                    content=[MagicMock(type="text", text="Test content")],
                )
            ]
            mock_result.model_dump.return_value = {
                "object": "vector_store.search_results.page",
                "search_query": "test query",
                "data": [
                    {
                        "file_id": "file_123",
                        "filename": "test.pdf",
                        "score": 0.95,
                        "attributes": {"source": "test"},
                        "content": [{"type": "text", "text": "Test content"}],
                    }
                ],
                "has_more": False,
                "next_page": None,
                "request_id": "req_123",
            }
            mock_query.return_value = mock_result

            result = await command.execute('--collection=test_vs --query="test query" --json', mock_controller)

            assert result is True
            mock_query.assert_called_once_with(
                vector_store_id="test_vs",
                query="test query",
                top_k=5,
                filters=None,
            )

            # Check that JSON was printed
            mock_print.assert_called()
            printed_output = mock_print.call_args[0][0]
            assert '"object": "vector_store.search_results.page"' in printed_output
            assert '"search_query": "test query"' in printed_output

    async def test_execute_with_json_no_results(self, command, mock_controller):
        """Test execute with JSON output when no results found."""
        with (
            patch("forge_cli.sdk.vectorstore.async_query_vectorstore") as mock_query,
            patch("builtins.print") as mock_print,
        ):
            mock_result = MagicMock()
            mock_result.data = []
            mock_query.return_value = mock_result

            result = await command.execute('--query="test query" --json', mock_controller)

            assert result is True

            # Check that JSON was printed for no results
            mock_print.assert_called()
            printed_output = mock_print.call_args[0][0]
            assert '"message": "No results found for the query"' in printed_output
            assert '"data": []' in printed_output

    async def test_execute_with_json_query_failed(self, command, mock_controller):
        """Test execute with JSON output when query fails."""
        with (
            patch("forge_cli.sdk.vectorstore.async_query_vectorstore") as mock_query,
            patch("builtins.print") as mock_print,
        ):
            mock_query.return_value = None

            result = await command.execute('--query="test query" --json', mock_controller)

            assert result is True

            # Check that JSON error was printed
            mock_print.assert_called()
            printed_output = mock_print.call_args[0][0]
            assert '"error": "Query failed - no results returned"' in printed_output
