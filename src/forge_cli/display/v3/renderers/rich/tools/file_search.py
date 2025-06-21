"""File search tool renderer for Rich display system."""

from forge_cli.response._types.response_file_search_tool_call import ResponseFileSearchToolCall
from ....style import ICONS, pack_queries
from ...rendable import Rendable


class FileSearchToolRender(Rendable):
    """Specialized renderer for file search tool calls.
    
    This class handles the rendering of file search tool calls with consistent styling
    and support for all file search tool properties.
    """
    
    def __init__(self):
        """Initialize the file search tool renderer."""
        super().__init__()
        self._parts = []
        self._queries = []
    
    def get_tool_metadata(self) -> tuple[str, str]:
        """Get tool icon and display name for file search.
        
        Returns:
            Tuple of (tool_icon, tool_name)
        """
        return ICONS.get("file_search_call", ICONS["processing"]), "Search"
    
    def with_queries(self, queries: list[str]) -> "FileSearchToolRender":
        """Add search queries to the render.
        
        Args:
            queries: List of search queries
            
        Returns:
            Self for method chaining
        """
        if queries:
            self._queries = queries
            # Use pack_queries for consistent display (it handles shortening internally)
            packed = pack_queries(*[f'"{q}"' for q in queries])
            self._parts.append(packed)
        return self
    
    def with_status(self, status: str) -> "FileSearchToolRender":
        """Add status display to the render.
        
        Args:
            status: Current status of the file search call
            
        Returns:
            Self for method chaining
        """
        self._status = status
        return self
    
    def with_results_count(self, count: int | None) -> "FileSearchToolRender":
        """Add results count to the render.
        
        Args:
            count: Number of search results found
            
        Returns:
            Self for method chaining
        """
        if count is not None:
            self._parts.append(f"{ICONS['check']}{count} results")
        return self
    
    def with_execution_trace(self, execution_trace: str | None) -> "FileSearchToolRender":
        """Add execution trace to the render (handled separately in trace blocks).
        
        Args:
            execution_trace: Execution trace string
            
        Returns:
            Self for method chaining
        """
        # Execution trace is handled separately in trace blocks
        return self
    
    def render(self) -> str:
        """Build and return the final rendered string for result summary only.
        
        Returns:
            The formatted display string for the file search tool results
        """
        if self._parts:
            return f" {ICONS['bullet']} ".join(self._parts)
        
        if self._status == "searching":
            return f"{ICONS['searching']} init"
        
        return f"{ICONS['processing']}searching files..."
    
    @classmethod
    def from_tool_item(cls, tool_item: ResponseFileSearchToolCall) -> "FileSearchToolRender":
        """Create a file search tool renderer from a tool item.
        
        Args:
            tool_item: The file search tool item to render
            
        Returns:
            FileSearchToolRender instance configured with the tool item data
        """
        renderer = cls()
        
        # Add queries if available
        if tool_item.queries:
            renderer.with_queries(tool_item.queries)
        
        # Add status
        renderer.with_status(tool_item.status)
        
        # Add results count if available
        if hasattr(tool_item, 'results_count') and tool_item.results_count is not None:
            renderer.with_results_count(tool_item.results_count)
        
        return renderer 