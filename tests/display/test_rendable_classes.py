"""Tests for the Rendable-based renderer classes."""

import pytest
from unittest.mock import Mock

from forge_cli.display.v3.renderers.rich.reason import ReasoningRenderer
from forge_cli.display.v3.renderers.rich.message_content import MessageContentRenderer
from forge_cli.display.v3.renderers.rich.citations import CitationsRenderer
from forge_cli.display.v3.renderers.rich.tools import FileReaderToolRender
from forge_cli.display.v3.renderers.rendable import Rendable


class TestRendableInheritance:
    """Test that all renderers properly inherit from Rendable."""
    
    def test_reasoning_renderer_inheritance(self):
        """Test ReasoningRenderer inherits from Rendable."""
        reasoning_item = Mock()
        reasoning_item.text = "Test reasoning"
        
        renderer = ReasoningRenderer(reasoning_item)
        assert isinstance(renderer, Rendable)
        assert hasattr(renderer, 'render')
        
        result = renderer.render()
        assert isinstance(result, str)
        assert "Test reasoning" in result
    
    def test_message_content_renderer_inheritance(self):
        """Test MessageContentRenderer inherits from Rendable."""
        content = Mock()
        content.type = "output_text"
        content.text = "Hello world"
        
        renderer = MessageContentRenderer(content)
        assert isinstance(renderer, Rendable)
        assert hasattr(renderer, 'render')
        
        result = renderer.render()
        assert isinstance(result, str)
        assert "Hello world" in result
    
    def test_citations_renderer_inheritance(self):
        """Test CitationsRenderer inherits from Rendable."""
        citation = Mock()
        citation.type = "file_citation"
        citation.filename = "test.pdf"
        citation.file_id = "file123"
        citation.index = 5
        
        renderer = CitationsRenderer([citation])
        assert isinstance(renderer, Rendable)
        assert hasattr(renderer, 'render')
        
        result = renderer.render()
        assert isinstance(result, str)
        assert "References" in result
        assert "test.pdf" in result
    
    def test_tool_renderer_inheritance(self):
        """Test tool renderers inherit from Rendable."""
        renderer = FileReaderToolRender()
        assert isinstance(renderer, Rendable)
        assert hasattr(renderer, 'render')
        
        result = renderer.render()
        assert isinstance(result, str)
        assert len(result) > 0


class TestReasoningRenderer:
    """Test ReasoningRenderer class."""
    
    def test_render_with_text(self):
        """Test rendering with reasoning text."""
        reasoning_item = Mock()
        reasoning_item.text = "This is the reasoning behind the decision."
        
        renderer = ReasoningRenderer(reasoning_item)
        result = renderer.render()
        
        assert "This is the reasoning behind the decision." in result
        assert result.startswith("> ")  # Should be formatted as blockquote
    
    def test_render_without_text(self):
        """Test rendering without reasoning text."""
        reasoning_item = Mock()
        reasoning_item.text = None
        
        renderer = ReasoningRenderer(reasoning_item)
        result = renderer.render()
        
        assert result == ""
    
    def test_render_empty_text(self):
        """Test rendering with empty reasoning text."""
        reasoning_item = Mock()
        reasoning_item.text = ""
        
        renderer = ReasoningRenderer(reasoning_item)
        result = renderer.render()
        
        assert result == ""


class TestMessageContentRenderer:
    """Test MessageContentRenderer class."""
    
    def test_render_output_text(self):
        """Test rendering output text content."""
        content = Mock()
        content.type = "output_text"
        content.text = "This is the response text."
        
        renderer = MessageContentRenderer(content)
        result = renderer.render()
        
        assert "This is the response text." in result
    
    def test_render_output_refusal(self):
        """Test rendering output refusal content."""
        content = Mock()
        content.type = "output_refusal"
        content.refusal = "Cannot provide this information."
        
        renderer = MessageContentRenderer(content)
        result = renderer.render()
        
        assert "Response refused" in result
        assert "Cannot provide this information." in result
        assert "⚠️" in result
    
    def test_render_unknown_type(self):
        """Test rendering unknown content type."""
        content = Mock()
        content.type = "unknown_type"
        
        renderer = MessageContentRenderer(content)
        result = renderer.render()
        
        assert result == ""


class TestCitationsRenderer:
    """Test CitationsRenderer class."""
    
    def test_render_file_citation(self):
        """Test rendering file citation."""
        citation = Mock()
        citation.type = "file_citation"
        citation.filename = "document.pdf"
        citation.file_id = "file123"
        citation.index = 10
        
        renderer = CitationsRenderer([citation])
        result = renderer.render()
        
        assert "### References" in result
        assert "1. document.pdf" in result
        assert "p.10" in result
    
    def test_render_url_citation(self):
        """Test rendering URL citation."""
        citation = Mock()
        citation.type = "url_citation"
        citation.url = "https://example.com"
        citation.title = "Example Website"
        
        renderer = CitationsRenderer([citation])
        result = renderer.render()
        
        assert "### References" in result
        assert "[Example Website](https://example.com)" in result
    
    def test_render_file_path_citation(self):
        """Test rendering file path citation."""
        citation = Mock()
        citation.type = "file_path"
        citation.file_id = "path/to/file.txt"
        
        renderer = CitationsRenderer([citation])
        result = renderer.render()
        
        assert "### References" in result
        assert "path/to/file.txt" in result
    
    def test_render_empty_citations(self):
        """Test rendering with no citations."""
        renderer = CitationsRenderer([])
        result = renderer.render()
        
        assert result == ""
    
    def test_render_multiple_citations(self):
        """Test rendering multiple citations."""
        citation1 = Mock()
        citation1.type = "file_citation"
        citation1.filename = "doc1.pdf"
        citation1.file_id = "file1"
        citation1.index = 5
        
        citation2 = Mock()
        citation2.type = "url_citation"
        citation2.url = "https://example.com"
        citation2.title = "Example"
        
        renderer = CitationsRenderer([citation1, citation2])
        result = renderer.render()
        
        assert "### References" in result
        assert "1. doc1.pdf" in result
        assert "2. [Example](https://example.com)" in result


class TestLegacyCompatibility:
    """Test that legacy functions still work."""
    
    def test_legacy_reasoning_function(self):
        """Test legacy render_reasoning_item function."""
        from forge_cli.display.v3.renderers.rich.reason import render_reasoning_item
        
        reasoning_item = Mock()
        reasoning_item.text = "Legacy test"
        
        result = render_reasoning_item(reasoning_item)
        assert "Legacy test" in result
    
    def test_legacy_content_function(self):
        """Test legacy render_message_content function."""
        from forge_cli.display.v3.renderers.rich.message_content import render_message_content
        
        content = Mock()
        content.type = "output_text"
        content.text = "Legacy content test"
        
        result = render_message_content(content)
        assert "Legacy content test" in result
    
    def test_legacy_citations_function(self):
        """Test legacy render_citations function."""
        from forge_cli.display.v3.renderers.rich.citations import render_citations
        
        citation = Mock()
        citation.type = "file_citation"
        citation.filename = "legacy.pdf"
        citation.file_id = "legacy123"
        citation.index = 1
        
        result = render_citations([citation])
        assert "References" in result
        assert "legacy.pdf" in result 