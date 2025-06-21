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
        """Test factory method with mock tool item."""
        tool_item = Mock()
        tool_item.file_name = "test.pdf"
        tool_item.doc_ids = ["doc123"]
        tool_item.progress = 0.5
        
        result = FileReaderToolRender.from_tool_item(tool_item)
        assert "test.pdf" in result
        assert "50%" in result


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
        """Test factory method with mock tool item."""
        tool_item = Mock()
        tool_item.queries = ["test query"]
        tool_item.status = "completed"
        
        result = WebSearchToolRender.from_tool_item(tool_item)
        assert "test query" in result


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
        """Test factory method with mock tool item."""
        tool_item = Mock()
        tool_item.queries = ["file search"]
        tool_item.status = "completed"
        
        result = FileSearchToolRender.from_tool_item(tool_item)
        assert "file search" in result


class TestPageReaderToolRender:
    """Test PageReaderToolRender class."""
    
    def test_with_document_and_page_range(self):
        """Test document with page range display."""
        result = (PageReaderToolRender()
                 .with_document_id("doc123")
                 .with_page_range(1, 5)
                 .render())
        assert "doc123" in result
        assert "p.1-5" in result
    
    def test_with_single_page(self):
        """Test document with single page display."""
        result = (PageReaderToolRender()
                 .with_document_id("doc123")
                 .with_page_range(3, 3)
                 .render())
        assert "doc123" in result
        assert "p.3" in result
    
    def test_with_progress(self):
        """Test progress display."""
        result = (PageReaderToolRender()
                 .with_document_id("doc123")
                 .with_progress(0.8)
                 .render())
        assert "80%" in result
    
    def test_from_tool_item(self):
        """Test factory method with mock tool item."""
        tool_item = Mock()
        tool_item.document_id = "test_doc"
        tool_item.start_page = 1
        tool_item.end_page = 3
        tool_item.progress = 0.6
        
        result = PageReaderToolRender.from_tool_item(tool_item)
        assert "test_doc" in result
        assert "p.1-3" in result
        assert "60%" in result


class TestCodeInterpreterToolRender:
    """Test CodeInterpreterToolRender class."""
    
    def test_with_python_code(self):
        """Test Python code detection and display."""
        code = "import numpy as np\nprint('hello')"
        result = (CodeInterpreterToolRender()
                 .with_code(code)
                 .render())
        assert "Python" in result
        assert "import numpy as np" in result
    
    def test_with_javascript_code(self):
        """Test JavaScript code detection."""
        code = "const x = 5;\nfunction test() { return x; }"
        result = (CodeInterpreterToolRender()
                 .with_code(code)
                 .render())
        assert "JavaScript" in result
    
    def test_with_long_code(self):
        """Test line count display for long code."""
        code = "\n".join([f"line_{i} = {i}" for i in range(10)])
        result = (CodeInterpreterToolRender()
                 .with_code(code)
                 .render())
        assert "10 lines" in result
    
    def test_with_output(self):
        """Test output display."""
        result = (CodeInterpreterToolRender()
                 .with_code("print('hello')")
                 .with_output("hello")
                 .render())
        assert "output: hello" in result
    
    def test_from_tool_item(self):
        """Test factory method with mock tool item."""
        tool_item = Mock()
        tool_item.code = "import os\nprint('test')"
        tool_item.output = "test"
        tool_item.status = "completed"
        
        result = CodeInterpreterToolRender.from_tool_item(tool_item)
        assert "Python" in result
        assert "output: test" in result


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
        """Test factory method with mock tool item."""
        tool_item = Mock()
        tool_item.function = "test_function"
        tool_item.arguments = {"param": "value"}
        tool_item.output = "result"
        tool_item.status = "completed"
        
        result = FunctionCallToolRender.from_tool_item(tool_item)
        assert "test_function" in result
        assert "param=value" in result
        assert "result" in result


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
        """Test factory method with mock tool item."""
        tool_item = Mock()
        tool_item.queries = ["list all"]
        tool_item.status = "completed"
        tool_item.document_count = 7
        
        result = ListDocumentsToolRender.from_tool_item(tool_item)
        assert "list all" in result
        assert "7 documents" in result


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