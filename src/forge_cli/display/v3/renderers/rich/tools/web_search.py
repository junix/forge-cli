"""Web search tool renderer for Rich display system."""

from ....style import ICONS, pack_queries
from ...rendable import Rendable


class WebSearchToolRender(Rendable):
    """Specialized renderer for web search tool calls.
    
    This class handles the rendering of web search tool calls with consistent styling
    and support for all web search tool properties.
    """
    
    def __init__(self):
        """Initialize the web search tool renderer."""
        self._parts = []
        self._status = "in_progress"
        self._queries = []
    
    def with_queries(self, queries: list[str]) -> "WebSearchToolRender":
        """Add search queries to the render.
        
        Args:
            queries: List of search queries
            
        Returns:
            Self for method chaining
        """
        if queries:
            self._queries = queries
            # Use pack_queries for beautiful display
            shortened_queries = [q[:30] + "..." if len(q) > 30 else q for q in queries]
            packed = pack_queries(*[f"{q}" for q in shortened_queries])
            self._parts.append(packed)
        return self
    
    def with_status(self, status: str) -> "WebSearchToolRender":
        """Add status display to the render.
        
        Args:
            status: Current status of the web search call
            
        Returns:
            Self for method chaining
        """
        self._status = status
        return self
    
    def with_results_count(self, count: int | None) -> "WebSearchToolRender":
        """Add results count to the render.
        
        Args:
            count: Number of search results found
            
        Returns:
            Self for method chaining
        """
        if count is not None:
            self._parts.append(f"{ICONS['check']}{count} results")
        return self
    
    def with_execution_trace(self, execution_trace: str | None) -> "WebSearchToolRender":
        """Add execution trace to the render (handled separately in trace blocks).
        
        Args:
            execution_trace: Execution trace string
            
        Returns:
            Self for method chaining
        """
        # Execution trace is handled separately in trace blocks
        return self
    
    def render(self) -> str:
        """Build and return the final rendered string.
        
        Returns:
            The formatted display string for the web search tool
        """
        if self._parts:
            return f" {ICONS['bullet']} ".join(self._parts)
        
        if self._status == "searching":
            return f"{ICONS['searching']} init"
        
        return f"{ICONS['processing']}preparing web search..."
    
    @classmethod
    def from_tool_item(cls, tool_item) -> str:
        """Create a web search tool render from a tool item and return the formatted string.
        
        Args:
            tool_item: The web search tool item to render
            
        Returns:
            Formatted display string
        """
        renderer = cls()
        
        # Add queries if available
        if hasattr(tool_item, 'queries') and tool_item.queries:
            renderer.with_queries(tool_item.queries)
        
        # Add status
        if hasattr(tool_item, 'status'):
            renderer.with_status(tool_item.status)
        
        # Add results count if available
        results_count = getattr(tool_item, 'results_count', None)
        if results_count is not None:
            renderer.with_results_count(results_count)
        
        return renderer.render() 