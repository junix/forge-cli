"""Tests for the FileReaderToolRender class."""

import pytest
from src.forge_cli.display.v3.renderers.rich import FileReaderToolRender
from src.forge_cli.response._types.response_function_file_reader import ResponseFunctionFileReader


class TestFileReaderToolRender:
    """Test cases for FileReaderToolRender class."""

    def test_basic_initialization(self):
        """Test basic FileReaderToolRender initialization."""
        renderer = FileReaderToolRender()
        result = renderer.render()
        assert "loading file..." in result

    def test_with_filename(self):
        """Test filename display."""
        renderer = FileReaderToolRender()
        result = renderer.with_filename("document.pdf").render()
        assert '"document.pdf"' in result
        assert "[PDF]" in result

    def test_with_filename_long(self):
        """Test long filename truncation."""
        long_filename = "a" * 40 + ".txt"
        renderer = FileReaderToolRender()
        result = renderer.with_filename(long_filename).render()
        assert "..." in result
        assert "[TXT]" in result

    def test_with_doc_ids(self):
        """Test document ID display."""
        renderer = FileReaderToolRender()
        result = renderer.with_doc_ids(["doc_12345678901234567890"]).render()
        assert "file:doc_12345678" in result

    def test_with_progress(self):
        """Test progress display."""
        renderer = FileReaderToolRender()
        result = renderer.with_progress(0.75).render()
        assert "75%" in result

    def test_with_status(self):
        """Test status handling."""
        renderer = FileReaderToolRender()
        result = renderer.with_status("completed").render()
        # Status is stored but doesn't directly affect basic render output
        assert isinstance(result, str)

    def test_with_query(self):
        """Test query display."""
        renderer = FileReaderToolRender()
        result = renderer.with_query("What is the main topic?").render()
        assert 'query: "What is the main topic?"' in result

    def test_with_query_long(self):
        """Test long query truncation."""
        long_query = "What is the main topic of this very long document that contains a lot of information?"
        renderer = FileReaderToolRender()
        result = renderer.with_query(long_query).render()
        assert "..." in result
        assert 'query:' in result

    def test_with_file_size(self):
        """Test file size display."""
        renderer = FileReaderToolRender()
        
        # Test bytes
        result_bytes = renderer.with_file_size(512).render()
        assert "512B" in result_bytes
        
        # Reset and test KB
        renderer = FileReaderToolRender()
        result_kb = renderer.with_file_size(2048).render()
        assert "2KB" in result_kb
        
        # Reset and test MB
        renderer = FileReaderToolRender()
        result_mb = renderer.with_file_size(2 * 1024 * 1024).render()
        assert "2MB" in result_mb

    def test_with_file_type(self):
        """Test file type display."""
        renderer = FileReaderToolRender()
        result = renderer.with_file_type("application/pdf").render()
        assert "type:application" in result

    def test_with_page_count(self):
        """Test page count display."""
        renderer = FileReaderToolRender()
        result = renderer.with_page_count(25).render()
        assert "25 pages" in result

    def test_method_chaining(self):
        """Test method chaining with multiple properties."""
        renderer = FileReaderToolRender()
        result = (renderer
                 .with_filename("report.pdf")
                 .with_progress(0.5)
                 .with_query("Summarize findings")
                 .with_file_size(1024)
                 .render())
        
        assert '"report.pdf"' in result
        assert "50%" in result
        assert 'query: "Summarize findings"' in result
        assert "1KB" in result

    def test_from_tool_item_with_filename(self):
        """Test from_tool_item class method with filename."""
        # Create a mock tool item
        class MockToolItem:
            def __init__(self):
                self.doc_ids = ["doc123"]
                self.query = "test query"
                
        tool_item = MockToolItem()
        setattr(tool_item, "file_name", "test.pdf")
        setattr(tool_item, "progress", 0.8)
        
        result = FileReaderToolRender.from_tool_item(tool_item)
        assert '"test.pdf"' in result
        assert "[PDF]" in result
        assert "80%" in result

    def test_from_tool_item_with_doc_ids_only(self):
        """Test from_tool_item class method with doc IDs only."""
        # Create a mock tool item
        class MockToolItem:
            def __init__(self):
                self.doc_ids = ["document_id_12345678901234567890"]
                self.query = "test query"
                
        tool_item = MockToolItem()
        # No file_name attribute
        setattr(tool_item, "progress", None)
        
        result = FileReaderToolRender.from_tool_item(tool_item)
        assert "file:document_id" in result

    def test_from_tool_item_minimal(self):
        """Test from_tool_item class method with minimal data."""
        # Create a mock tool item with minimal data
        class MockToolItem:
            def __init__(self):
                self.doc_ids = []
                self.query = ""
                
        tool_item = MockToolItem()
        setattr(tool_item, "progress", None)
        
        result = FileReaderToolRender.from_tool_item(tool_item)
        assert "loading file..." in result

    def test_from_tool_item_with_real_model(self):
        """Test from_tool_item with actual ResponseFunctionFileReader model."""
        tool_item = ResponseFunctionFileReader(
            id="test_123",
            type="file_reader_call",
            status="in_progress",
            doc_ids=["doc_abc123"],
            query="What are the key findings?",
            progress=0.6
        )
        
        result = FileReaderToolRender.from_tool_item(tool_item)
        assert "file:doc_abc123" in result
        assert "60%" in result

    def test_empty_values_handling(self):
        """Test handling of None and empty values."""
        renderer = FileReaderToolRender()
        result = (renderer
                 .with_filename(None)
                 .with_doc_ids([])
                 .with_progress(None)
                 .with_query("")
                 .with_file_size(None)
                 .with_file_type(None)
                 .with_page_count(None)
                 .render())
        
        assert "loading file..." in result

    def test_edge_cases(self):
        """Test edge cases for various inputs."""
        renderer = FileReaderToolRender()
        
        # Test filename without extension
        result1 = renderer.with_filename("README").render()
        assert '"README"' in result1
        assert "[FILE]" in result1
        
        # Reset and test zero progress
        renderer = FileReaderToolRender()
        result2 = renderer.with_progress(0.0).render()
        assert "0%" in result2
        
        # Reset and test zero file size
        renderer = FileReaderToolRender()
        result3 = renderer.with_file_size(0).render()
        assert "0B" in result3

    def test_icon_usage(self):
        """Test that appropriate icons are used."""
        renderer = FileReaderToolRender()
        result = (renderer
                 .with_filename("test.pdf")
                 .with_progress(0.5)
                 .with_query("test")
                 .render())
        
        # Should contain bullet separators between parts
        bullet_count = result.count(" • ")  # ICONS['bullet'] should be bullet
        assert bullet_count >= 2  # At least filename, progress, and query parts

    def test_consistent_formatting(self):
        """Test that formatting is consistent with existing style."""
        renderer = FileReaderToolRender()
        result = renderer.with_filename("document.xlsx").render()
        
        # Should follow the pattern: icon + "filename" + [EXT]
        assert '"document.xlsx"' in result
        assert "[XLSX]" in result
        
        # Should use the file_reader_call icon from ICONS
        # The exact icon will depend on the ICONS configuration 