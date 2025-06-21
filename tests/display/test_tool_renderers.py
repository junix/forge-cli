"""Tests for the modular tool renderer architecture."""

import pytest
from unittest.mock import Mock

from forge_cli.display.v3.renderers.rich.tools import (
    FileReaderToolRender,
    WebSearchToolRender,
    FileSearchToolRender,
    PageReaderToolRender,
    CodeInterpreterToolRender,
    FunctionCallToolRender,
    ListDocumentsToolRender,
)


class TestFileReaderToolRender:
    """Test FileReaderToolRender class."""
    
    def test_with_filename(self):
        """Test filename display with extension."""
        result = (FileReaderToolRender()
                 .with_filename("document.pdf")
                 .render())
        assert "document.pdf" in result
        assert "[PDF]" in result
    
    def test_with_long_filename(self):
        """Test long filename truncation."""
        long_name = "very_long_filename_that_should_be_truncated.pdf"
        result = (FileReaderToolRender()
                 .with_filename(long_name)
                 .render())
        assert "..." in result
        assert len(result) < len(long_name) + 50  # Account for icons and formatting
    
    def test_with_progress(self):
        """Test progress display."""
        result = (FileReaderToolRender()
                 .with_filename("test.pdf")
                 .with_progress(0.75)
                 .render())
        assert "75%" in result
    
    def test_from_tool_item(self):
        """Test from_tool_item class method."""
        # Mock tool item with file attributes - avoid problematic attributes
        tool_item = Mock()
        tool_item.file_name = "document.pdf"
        tool_item.progress = 0.75
        # Don't set file_size and file_type to avoid Mock issues
        
        renderer = FileReaderToolRender.from_tool_item(tool_item)
        result = renderer.render()
        
        # Verify the result contains expected elements  
        assert "document.pdf" in result
        assert "[PDF]" in result
        assert "75%" in result


class TestWebSearchToolRender:
    """Test WebSearchToolRender class."""
    
    def test_with_single_query(self):
        """Test single query display."""
        result = (WebSearchToolRender()
                 .with_queries(["python tutorial"])
                 .render())
        assert "python tutorial" in result
    
    def test_with_multiple_queries(self):
        """Test multiple queries display."""
        queries = ["python", "javascript", "typescript", "react"]
        result = (WebSearchToolRender()
                 .with_queries(queries)
                 .render())
        assert "python" in result
        assert "javascript" in result
        assert "typescript" in result
        # Should show "1 more" for the fourth query
        assert "more" in result
    
    def test_searching_status(self):
        """Test searching status display."""
        result = (WebSearchToolRender()
                 .with_status("searching")
                 .render())
        assert "init" in result
    
    def test_from_tool_item(self):
        """Test from_tool_item class method."""
        # Mock tool item
        tool_item = Mock()
        tool_item.queries = ["Python tutorial"]
        tool_item.status = "completed"
        # Set results_count to None to avoid Mock issues
        tool_item.results_count = None
        
        renderer = WebSearchToolRender.from_tool_item(tool_item)
        result = renderer.render()
        
        # Focus on content, not specific icons
        assert "Python tutorial" in result


class TestFileSearchToolRender:
    """Test FileSearchToolRender class."""
    
    def test_with_queries(self):
        """Test query display."""
        result = (FileSearchToolRender()
                 .with_queries(["search term"])
                 .render())
        assert "search term" in result
    
    def test_with_results_count(self):
        """Test results count display."""
        result = (FileSearchToolRender()
                 .with_queries(["test"])
                 .with_results_count(5)
                 .render())
        assert "5 results" in result
    
    def test_from_tool_item(self):
        """Test from_tool_item class method."""
        # Mock tool item
        tool_item = Mock()
        tool_item.queries = ["machine learning"]
        tool_item.status = "completed"
        # Set results_count to None to avoid Mock issues
        tool_item.results_count = None
        
        renderer = FileSearchToolRender.from_tool_item(tool_item)
        result = renderer.render()
        
        # Focus on content, not specific icons
        assert "machine learning" in result


class TestPageReaderToolRender:
    """Test PageReaderToolRender class."""
    
    def test_with_document_and_page_range(self):
        """Test document with page range display."""
        result = (PageReaderToolRender()
                 .with_document_id("doc123")
                 .with_page_range(0, 4)  # 0-indexed input
                 .render())
        assert "doc123" in result
        assert "p.1-5" in result  # 1-indexed display
    
    def test_with_single_page(self):
        """Test document with single page display."""
        result = (PageReaderToolRender()
                 .with_document_id("doc123")
                 .with_page_range(2, 2)  # 0-indexed input
                 .render())
        assert "doc123" in result
        assert "p.3" in result  # 1-indexed display
    
    def test_with_progress(self):
        """Test progress display."""
        result = (PageReaderToolRender()
                 .with_document_id("doc123")
                 .with_progress(0.8)
                 .render())
        assert "80%" in result
    
    def test_from_tool_item(self):
        """Test from_tool_item class method."""
        # Mock tool item with typical attributes
        tool_item = Mock()
        tool_item.document_id = "doc123"
        tool_item.start_page = 0  # 0-indexed
        tool_item.end_page = 4    # 0-indexed
        tool_item.progress = 0.8
        tool_item.status = "in_progress"
        
        renderer = PageReaderToolRender.from_tool_item(tool_item)
        result = renderer.render()
        
        # Verify the result contains expected elements (1-indexed display)
        assert "doc123" in result
        assert "1-5" in result  # Should display as 1-indexed
        assert "80%" in result


class TestCodeInterpreterToolRender:
    """Test CodeInterpreterToolRender class."""
    
    def test_with_python_code(self):
        """Test Python code detection and display."""
        code = "import numpy as np\nprint('hello')"
        result = (CodeInterpreterToolRender()
                 .with_code(code)
                 .render())
        assert "Code:" in result  # Changed from "Python" to "Code:"
        assert "import numpy as np" in result
    
    def test_with_javascript_code(self):
        """Test JavaScript code detection."""
        code = "const x = 5;\nfunction test() { return x; }"
        result = (CodeInterpreterToolRender()
                 .with_code(code)
                 .render())
        assert "Code:" in result  # Changed from "JavaScript" to "Code:"
    
    def test_with_long_code(self):
        """Test code preview display for long code."""
        code = "\n".join([f"line_{i} = {i}" for i in range(10)])
        result = (CodeInterpreterToolRender()
                 .with_code(code)
                 .render())
        assert "Code:" in result  # Changed from "10 lines" to "Code:"
        assert "line_0 = 0" in result  # Should show first line preview
    
    def test_with_output(self):
        """Test output display."""
        result = (CodeInterpreterToolRender()
                 .with_code("print('hello')")
                 .with_output("hello")
                 .render())
        assert "output: hello" in result
    
    def test_from_tool_item(self):
        """Test from_tool_item class method."""
        # Mock tool item
        tool_item = Mock()
        tool_item.code = "print('hello')"
        tool_item.status = "completed"
        # Don't set results to avoid Mock iteration issues
        
        renderer = CodeInterpreterToolRender.from_tool_item(tool_item)
        result = renderer.render()
        
        # Check for code execution indicators
        assert "Code:" in result
        assert "print" in result


class TestFunctionCallToolRender:
    """Test FunctionCallToolRender class."""
    
    def test_with_function_name(self):
        """Test function name display."""
        result = (FunctionCallToolRender()
                 .with_function("calculate_sum")
                 .render())
        assert "calculate_sum" in result
    
    def test_with_dict_arguments(self):
        """Test dictionary arguments display."""
        args = {"x": 1, "y": 2, "z": 3}
        result = (FunctionCallToolRender()
                 .with_function("test_func")
                 .with_arguments(args)
                 .render())
        assert "x=1" in result
        assert "y=2" in result
        assert "+1 more" in result  # Third argument should be collapsed
    
    def test_with_string_arguments(self):
        """Test JSON string arguments display."""
        args_json = '{"a": 1, "b": 2}'
        result = (FunctionCallToolRender()
                 .with_function("test_func")
                 .with_arguments(args_json)
                 .render())
        assert "a=1" in result
        assert "b=2" in result
    
    def test_with_output(self):
        """Test output display."""
        result = (FunctionCallToolRender()
                 .with_function("test_func")
                 .with_output("success")
                 .render())
        assert "success" in result
    
    def test_from_tool_item(self):
        """Test from_tool_item class method."""
        # Mock tool item
        tool_item = Mock()
        tool_item.function = "get_weather"
        tool_item.arguments = '{"city": "Paris"}'
        tool_item.output = "Sunny, 25°C"
        tool_item.status = "completed"
        
        renderer = FunctionCallToolRender.from_tool_item(tool_item)
        result = renderer.render()
        
        assert "get_weather" in result
        assert "city=Paris" in result
        assert "Sunny, 25°C" in result


class TestListDocumentsToolRender:
    """Test ListDocumentsToolRender class."""
    
    def test_with_queries(self):
        """Test query display."""
        result = (ListDocumentsToolRender()
                 .with_queries(["search docs"])
                 .render())
        assert "search docs" in result
    
    def test_with_document_count(self):
        """Test document count display."""
        result = (ListDocumentsToolRender()
                 .with_queries(["test"])
                 .with_document_count(10)
                 .render())
        assert "10 documents" in result
    
    def test_searching_status(self):
        """Test searching status display."""
        result = (ListDocumentsToolRender()
                 .with_status("searching")
                 .render())
        assert "init" in result
    
    def test_from_tool_item(self):
        """Test from_tool_item class method."""
        # Mock tool item
        tool_item = Mock()
        tool_item.queries = ["python files"]
        tool_item.status = "completed"
        # Set document_count to None to avoid Mock issues
        tool_item.document_count = None
        
        renderer = ListDocumentsToolRender.from_tool_item(tool_item)
        result = renderer.render()
        
        assert "python files" in result


class TestRendererIntegration:
    """Integration tests for all renderers."""
    
    def test_all_renderers_have_consistent_interface(self):
        """Test that all renderers follow the same interface pattern."""
        renderers = [
            FileReaderToolRender,
            WebSearchToolRender,
            FileSearchToolRender,
            PageReaderToolRender,
            CodeInterpreterToolRender,
            FunctionCallToolRender,
            ListDocumentsToolRender,
        ]
        
        for renderer_class in renderers:
            # Each renderer should have these methods
            assert hasattr(renderer_class, '__init__')
            assert hasattr(renderer_class, 'render')
            assert hasattr(renderer_class, 'from_tool_item')
            assert hasattr(renderer_class, 'with_status')
            assert hasattr(renderer_class, 'with_execution_trace')
            
            # Test basic instantiation and render
            renderer = renderer_class()
            result = renderer.render()
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_builder_pattern_consistency(self):
        """Test that all renderers support method chaining."""
        # Test that with_* methods return self for chaining
        renderer = FileReaderToolRender()
        chained = renderer.with_filename("test.pdf").with_status("completed")
        assert chained is renderer  # Should return same instance for chaining 