"""Tests for update commands."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from forge_cli.chat.commands.files.update_collection import UpdateCollectionCommand
from forge_cli.chat.commands.files.update_document import UpdateDocumentCommand


class TestUpdateCollectionCommand:
    """Test cases for UpdateCollectionCommand."""

    @pytest.fixture
    def command(self):
        """Create UpdateCollectionCommand instance."""
        return UpdateCollectionCommand()

    @pytest.fixture
    def mock_controller(self):
        """Create mock controller."""
        controller = MagicMock()
        controller.display = MagicMock()
        return controller

    def test_command_properties(self, command):
        """Test command properties."""
        assert command.name == "update-collection"
        assert command.description == "Update an existing vector store collection"
        assert "update-vs" in command.aliases
        assert "modify-collection" in command.aliases

    def test_parse_args_basic(self, command):
        """Test basic argument parsing."""
        collection_id, params = command._parse_args('vs_123 --name="Test Collection"')
        
        assert collection_id == "vs_123"
        assert params["name"] == "Test Collection"

    def test_parse_args_multiple_params(self, command):
        """Test parsing multiple parameters."""
        args = 'vs_123 --name="Test" --description="Test desc" --expires-after=3600'
        collection_id, params = command._parse_args(args)
        
        assert collection_id == "vs_123"
        assert params["name"] == "Test"
        assert params["description"] == "Test desc"
        assert params["expires_after"] == "3600"

    def test_parse_args_file_operations(self, command):
        """Test parsing file operation parameters."""
        args = 'vs_123 --add-files="file1,file2" --remove-files="file3,file4"'
        collection_id, params = command._parse_args(args)
        
        assert collection_id == "vs_123"
        assert params["add_files"] == "file1,file2"
        assert params["remove_files"] == "file3,file4"

    def test_parse_metadata(self, command):
        """Test metadata parsing."""
        metadata = command._parse_metadata("key1:value1,key2:value2,key3:value3")
        
        assert metadata == {
            "key1": "value1",
            "key2": "value2", 
            "key3": "value3"
        }

    def test_parse_metadata_empty(self, command):
        """Test empty metadata parsing."""
        metadata = command._parse_metadata("")
        assert metadata == {}

    @pytest.mark.asyncio
    async def test_execute_no_args(self, command, mock_controller):
        """Test execute with no arguments."""
        result = await command.execute("", mock_controller)
        
        assert result is True
        mock_controller.display.show_error.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_missing_collection_id(self, command, mock_controller):
        """Test execute with missing collection ID."""
        result = await command.execute("--name=test", mock_controller)
        
        assert result is True
        mock_controller.display.show_error.assert_called()


class TestUpdateDocumentCommand:
    """Test cases for UpdateDocumentCommand."""

    @pytest.fixture
    def command(self):
        """Create UpdateDocumentCommand instance."""
        return UpdateDocumentCommand()

    @pytest.fixture
    def mock_controller(self):
        """Create mock controller."""
        controller = MagicMock()
        controller.display = MagicMock()
        return controller

    def test_command_properties(self, command):
        """Test command properties."""
        assert command.name == "update-document"
        assert command.description == "Update an existing document's metadata and properties"
        assert "update-doc" in command.aliases
        assert "modify-document" in command.aliases

    def test_parse_args_basic(self, command):
        """Test basic argument parsing."""
        document_id, params = command._parse_args('doc_123 --title="Test Document"')
        
        assert document_id == "doc_123"
        assert params["title"] == "Test Document"

    def test_parse_args_multiple_params(self, command):
        """Test parsing multiple parameters."""
        args = 'doc_123 --title="Test" --author="John Doe" --is-favorite=true'
        document_id, params = command._parse_args(args)
        
        assert document_id == "doc_123"
        assert params["title"] == "Test"
        assert params["author"] == "John Doe"
        assert params["is_favorite"] == "true"

    def test_parse_string_list(self, command):
        """Test string list parsing."""
        result = command._parse_string_list("item1,item2,item3")
        assert result == ["item1", "item2", "item3"]

    def test_parse_string_list_empty(self, command):
        """Test empty string list parsing."""
        result = command._parse_string_list("")
        assert result == []

    def test_parse_int_list(self, command):
        """Test integer list parsing."""
        result = command._parse_int_list("1,2,3,4")
        assert result == [1, 2, 3, 4]

    def test_parse_int_list_invalid(self, command):
        """Test invalid integer list parsing."""
        result = command._parse_int_list("1,invalid,3")
        assert result is None

    def test_parse_metadata(self, command):
        """Test metadata parsing."""
        metadata = command._parse_metadata("category:research,priority:high")
        
        assert metadata == {
            "category": "research",
            "priority": "high"
        }

    @pytest.mark.asyncio
    async def test_execute_no_args(self, command, mock_controller):
        """Test execute with no arguments."""
        result = await command.execute("", mock_controller)
        
        assert result is True
        mock_controller.display.show_error.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_missing_document_id(self, command, mock_controller):
        """Test execute with missing document ID."""
        result = await command.execute("--title=test", mock_controller)
        
        assert result is True
        mock_controller.display.show_error.assert_called()


class TestParameterParsing:
    """Test parameter parsing utilities."""

    def test_kebab_case_conversion(self):
        """Test kebab-case to snake_case conversion."""
        command = UpdateCollectionCommand()
        
        # Test the parameter parsing with kebab-case
        args = '--add-files="file1,file2" --remove-files="file3"'
        params = command._parse_parameters(args)
        
        assert "add_files" in params
        assert "remove_files" in params
        assert params["add_files"] == "file1,file2"
        assert params["remove_files"] == "file3"

    def test_quoted_values(self):
        """Test quoted value parsing."""
        command = UpdateDocumentCommand()
        
        args = '--title="Document with spaces" --author="John Doe"'
        params = command._parse_parameters(args)
        
        assert params["title"] == "Document with spaces"
        assert params["author"] == "John Doe"

    def test_unquoted_values(self):
        """Test unquoted value parsing."""
        command = UpdateDocumentCommand()
        
        args = '--title=SimpleTitle --is-favorite=true'
        params = command._parse_parameters(args)
        
        assert params["title"] == "SimpleTitle"
        assert params["is_favorite"] == "true"


if __name__ == "__main__":
    pytest.main([__file__])
