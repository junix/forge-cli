"""List documents tool renderer for Rich display system."""

from forge_cli.response._types.response_list_documents_tool_call import ResponseListDocumentsToolCall
from ....style import ICONS, pack_queries
from ...rendable import Rendable


class ListDocumentsToolRender(Rendable):
    """Specialized renderer for list documents tool calls.
    
    This class handles the rendering of list documents tool calls with consistent styling
    and support for all list documents tool properties.
    """
    
    def __init__(self):
        """Initialize the list documents tool renderer."""
        self._parts = []
        self._status = "in_progress"
        self._queries = []
    
    def with_queries(self, queries: list[str]) -> "ListDocumentsToolRender":
        """Add search queries to the render.
        
        Args:
            queries: List of search queries
            
        Returns:
            Self for method chaining
        """
        if queries:
            self._queries = queries
            # Use pack_queries for consistent display
            shortened_queries = [q[:25] + "..." if len(q) > 25 else q for q in queries]
            packed = pack_queries(*[f"{q}" for q in shortened_queries])
            self._parts.append(packed)
        return self
    
    def with_status(self, status: str) -> "ListDocumentsToolRender":
        """Add status display to the render.
        
        Args:
            status: Current status of the list documents call
            
        Returns:
            Self for method chaining
        """
        self._status = status
        return self
    
    def with_document_count(self, count: int | None) -> "ListDocumentsToolRender":
        """Add document count to the render.
        
        Args:
            count: Number of documents found
            
        Returns:
            Self for method chaining
        """
        if count is not None:
            self._parts.append(f"{ICONS['check']}{count} documents")
        return self
    
    def with_execution_trace(self, execution_trace: str | None) -> "ListDocumentsToolRender":
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
            The formatted display string for the list documents tool
        """
        if self._parts:
            return f" {ICONS['bullet']} ".join(self._parts)
        
        if self._status == "searching":
            return f"{ICONS['searching']} init"
        
        return f"{ICONS['processing']}listing documents..."
    
    @classmethod
    def from_tool_item(cls, tool_item: ResponseListDocumentsToolCall) -> "ListDocumentsToolRender":
        """Create a list documents tool renderer from a tool item.
        
        Args:
            tool_item: The list documents tool item to render
            
        Returns:
            ListDocumentsToolRender instance configured with the tool item data
        """
        renderer = cls()
        
        # Add queries if available
        if tool_item.queries:
            renderer.with_queries(tool_item.queries)
        
        # Add status
        renderer.with_status(tool_item.status)
        
        # Add document count if available
        if hasattr(tool_item, 'document_count') and tool_item.document_count is not None:
            renderer.with_document_count(tool_item.document_count)
        
        return renderer 