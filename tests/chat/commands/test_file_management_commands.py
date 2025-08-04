"""Tests for file management commands (join/leave)."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from forge_cli.chat.commands.files.join_documents import JoinDocumentsCommand
from forge_cli.chat.commands.files.leave_documents import LeaveDocumentsCommand, LeftFileCommand


class TestJoinDocumentsCommand:
    """Test cases for JoinDocumentsCommand."""

    @pytest.fixture
    def command(self):
        """Create JoinDocumentsCommand instance."""
        return JoinDocumentsCommand()

    @pytest.fixture
    def mock_controller(self):
        """Create mock controller."""
        controller = MagicMock()
        controller.display = MagicMock()
        controller.conversation = MagicMock()
        controller.conversation.get_uploaded_documents.return_value = [
            {"id": "doc_123", "filename": "test1.pdf"},
            {"id": "doc_456", "filename": "test2.pdf"}
        ]
        controller.conversation.get_current_vector_store_ids.return_value = []
        return controller

    def test_command_properties(self, command):
        """Test command properties."""
        assert command.name == "join-documents"
        assert command.description == "Join uploaded documents to a vector store collection"
        assert "join-docs" in command.aliases
        assert "join-file" in command.aliases
        assert "join" in command.aliases

    @pytest.mark.asyncio
    async def test_execute_no_args(self, command, mock_controller):
        """Test execute with no arguments."""
        result = await command.execute("", mock_controller)
        
        assert result is True
        # Should show usage when no args provided

    @pytest.mark.asyncio
    async def test_execute_no_uploaded_docs(self, command, mock_controller):
        """Test execute when no documents are uploaded."""
        mock_controller.conversation.get_uploaded_documents.return_value = []
        
        result = await command.execute("vs_123", mock_controller)
        
        assert result is True
        mock_controller.display.show_error.assert_called_with("❌ No uploaded documents found")

    @pytest.mark.asyncio
    async def test_execute_join_all_docs(self, command, mock_controller):
        """Test joining all uploaded documents."""
        # Mock the SDK function
        with pytest.mock.patch('forge_cli.sdk.async_join_files_to_vectorstore') as mock_join:
            mock_join.return_value = True
            
            result = await command.execute("vs_123", mock_controller)
            
            assert result is True
            mock_join.assert_called_once_with(
                vector_store_id="vs_123",
                file_ids=["doc_123", "doc_456"]
            )

    @pytest.mark.asyncio
    async def test_execute_join_specific_docs(self, command, mock_controller):
        """Test joining specific documents."""
        with pytest.mock.patch('forge_cli.sdk.async_join_files_to_vectorstore') as mock_join:
            mock_join.return_value = True
            
            result = await command.execute("vs_123 doc_123", mock_controller)
            
            assert result is True
            mock_join.assert_called_once_with(
                vector_store_id="vs_123",
                file_ids=["doc_123"]
            )

    @pytest.mark.asyncio
    async def test_execute_invalid_doc_id(self, command, mock_controller):
        """Test with invalid document ID."""
        result = await command.execute("vs_123 invalid_doc", mock_controller)
        
        assert result is True
        mock_controller.display.show_error.assert_called_with("❌ Document ID not found: invalid_doc")


class TestLeaveDocumentsCommand:
    """Test cases for LeaveDocumentsCommand."""

    @pytest.fixture
    def command(self):
        """Create LeaveDocumentsCommand instance."""
        return LeaveDocumentsCommand()

    @pytest.fixture
    def mock_controller(self):
        """Create mock controller."""
        controller = MagicMock()
        controller.display = MagicMock()
        return controller

    def test_command_properties(self, command):
        """Test command properties."""
        assert command.name == "leave-documents"
        assert command.description == "Remove documents from a vector store collection"
        assert "leave-docs" in command.aliases
        assert "left-file" in command.aliases
        assert "remove-from-collection" in command.aliases

    @pytest.mark.asyncio
    async def test_execute_no_args(self, command, mock_controller):
        """Test execute with no arguments."""
        result = await command.execute("", mock_controller)
        
        assert result is True
        # Should show usage when no args provided

    @pytest.mark.asyncio
    async def test_execute_missing_file_id(self, command, mock_controller):
        """Test execute with missing file ID."""
        result = await command.execute("vs_123", mock_controller)
        
        assert result is True
        mock_controller.display.show_error.assert_called_with(
            "❌ Both vector store ID and file ID(s) are required"
        )

    @pytest.mark.asyncio
    async def test_execute_remove_single_file(self, command, mock_controller):
        """Test removing a single file."""
        # Mock the SDK function
        with pytest.mock.patch('forge_cli.sdk.async_modify_vectorstore') as mock_modify:
            mock_result = MagicMock()
            mock_result.metadata = {"files": ["doc_456", "doc_789"]}  # Remaining files
            mock_modify.return_value = mock_result
            
            result = await command.execute("vs_123 doc_123", mock_controller)
            
            assert result is True
            mock_modify.assert_called_once_with(
                vector_store_id="vs_123",
                left_file_ids=["doc_123"]
            )

    @pytest.mark.asyncio
    async def test_execute_remove_multiple_files(self, command, mock_controller):
        """Test removing multiple files."""
        with pytest.mock.patch('forge_cli.sdk.async_modify_vectorstore') as mock_modify:
            mock_result = MagicMock()
            mock_result.metadata = {"files": ["doc_789"]}  # Remaining files
            mock_modify.return_value = mock_result
            
            result = await command.execute("vs_123 doc_123 doc_456", mock_controller)
            
            assert result is True
            mock_modify.assert_called_once_with(
                vector_store_id="vs_123",
                left_file_ids=["doc_123", "doc_456"]
            )

    @pytest.mark.asyncio
    async def test_execute_remove_failed(self, command, mock_controller):
        """Test when removal fails."""
        with pytest.mock.patch('forge_cli.sdk.async_modify_vectorstore') as mock_modify:
            mock_modify.return_value = None  # Indicates failure
            
            result = await command.execute("vs_123 doc_123", mock_controller)
            
            assert result is True
            mock_controller.display.show_error.assert_called_with(
                "❌ Failed to remove files from vector store"
            )


class TestLeftFileCommand:
    """Test cases for LeftFileCommand."""

    @pytest.fixture
    def command(self):
        """Create LeftFileCommand instance."""
        return LeftFileCommand()

    @pytest.fixture
    def mock_controller(self):
        """Create mock controller."""
        controller = MagicMock()
        controller.display = MagicMock()
        return controller

    def test_command_properties(self, command):
        """Test command properties."""
        assert command.name == "left-file"
        assert command.description == "Remove a file from a vector store collection"
        assert "leave-file" in command.aliases
        assert "remove-file" in command.aliases

    @pytest.mark.asyncio
    async def test_execute_delegates_to_leave_command(self, command, mock_controller):
        """Test that LeftFileCommand delegates to LeaveDocumentsCommand."""
        with pytest.mock.patch('forge_cli.sdk.async_modify_vectorstore') as mock_modify:
            mock_result = MagicMock()
            mock_result.metadata = {"files": ["doc_456"]}
            mock_modify.return_value = mock_result
            
            result = await command.execute("vs_123 doc_123", mock_controller)
            
            assert result is True
            mock_modify.assert_called_once_with(
                vector_store_id="vs_123",
                left_file_ids=["doc_123"]
            )


class TestFileManagementWorkflow:
    """Test complete file management workflows."""

    @pytest.fixture
    def join_command(self):
        return JoinDocumentsCommand()

    @pytest.fixture
    def leave_command(self):
        return LeaveDocumentsCommand()

    @pytest.fixture
    def mock_controller(self):
        controller = MagicMock()
        controller.display = MagicMock()
        controller.conversation = MagicMock()
        controller.conversation.get_uploaded_documents.return_value = [
            {"id": "doc_123", "filename": "test1.pdf"},
            {"id": "doc_456", "filename": "test2.pdf"}
        ]
        controller.conversation.get_current_vector_store_ids.return_value = []
        return controller

    @pytest.mark.asyncio
    async def test_join_then_leave_workflow(self, join_command, leave_command, mock_controller):
        """Test a complete join then leave workflow."""
        with pytest.mock.patch('forge_cli.sdk.async_join_files_to_vectorstore') as mock_join, \
             pytest.mock.patch('forge_cli.sdk.async_modify_vectorstore') as mock_modify:
            
            # Setup mocks
            mock_join.return_value = True
            mock_result = MagicMock()
            mock_result.metadata = {"files": ["doc_456"]}
            mock_modify.return_value = mock_result
            
            # Join files
            result1 = await join_command.execute("vs_123", mock_controller)
            assert result1 is True
            
            # Leave one file
            result2 = await leave_command.execute("vs_123 doc_123", mock_controller)
            assert result2 is True
            
            # Verify calls
            mock_join.assert_called_once_with(
                vector_store_id="vs_123",
                file_ids=["doc_123", "doc_456"]
            )
            mock_modify.assert_called_once_with(
                vector_store_id="vs_123",
                left_file_ids=["doc_123"]
            )


if __name__ == "__main__":
    pytest.main([__file__])
