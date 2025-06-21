"""Tests for WebSearchToolRender class."""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from forge_cli.display.v3.renderers.rich.tools.web_search import WebSearchToolRender


class MockWebSearchItem:
    """Mock web search tool item for testing."""
    
    def __init__(self, queries=None, status="in_progress", results_count=None):
        self.queries = queries or []
        self.status = status
        self.results_count = results_count


def test_web_search_basic():
    """Test basic web search rendering."""
    renderer = WebSearchToolRender()
    result = (renderer
              .with_queries(["machine learning", "AI development"])
              .with_status("completed")
              .render())
    
    print(f"Basic test result: {result}")
    assert "machine learning" in result
    assert "AI development" in result


def test_web_search_empty_queries():
    """Test web search with empty queries."""
    renderer = WebSearchToolRender()
    result = renderer.with_queries([]).render()
    
    print(f"Empty queries result: {result}")
    assert "searching web..." in result


def test_web_search_searching_status():
    """Test web search with searching status."""
    renderer = WebSearchToolRender()
    result = renderer.with_status("searching").render()
    
    print(f"Searching status result: {result}")
    assert "init" in result


def test_web_search_long_query():
    """Test web search with long query."""
    renderer = WebSearchToolRender()
    long_query = "This is a very long search query that should be truncated because it's too long"
    result = renderer.with_queries([long_query]).render()
    
    print(f"Long query result: {result}")
    assert "..." in result


def test_web_search_factory_method():
    """Test web search factory method."""
    tool_item = MockWebSearchItem(
        queries=["Python programming"], 
        status="searching"
    )
    renderer = WebSearchToolRender.from_tool_item(tool_item)
    result = renderer.render()
    
    print(f"Factory test result: {result}")
    assert "Python programming" in result


def test_web_search_with_results_count():
    """Test web search with results count."""
    renderer = WebSearchToolRender()
    result = (renderer
              .with_queries(["test query"])
              .with_results_count(5)
              .render())
    
    print(f"Results count test: {result}")
    assert "5 results" in result


def test_web_search_chain_methods():
    """Test method chaining."""
    renderer = WebSearchToolRender()
    result = (renderer
              .with_queries(["test"])
              .with_status("completed")
              .with_results_count(3)
              .render())
    
    print(f"Chain methods test: {result}")
    assert "test" in result
    assert "3 results" in result


if __name__ == "__main__":
    print("Running WebSearchToolRender tests...")
    
    test_web_search_basic()
    test_web_search_empty_queries()
    test_web_search_searching_status()
    test_web_search_long_query()
    test_web_search_factory_method()
    test_web_search_with_results_count()
    test_web_search_chain_methods()
    
    print("✅ All tests passed!") 