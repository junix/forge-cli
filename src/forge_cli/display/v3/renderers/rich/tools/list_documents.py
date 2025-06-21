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
        self._execution_trace = None
    
    def with_queries(self, queries: list[str]) -> "ListDocumentsToolRender":
        """Add search queries to the render.
        
        Args:
            queries: List of search queries
            
        Returns:
            Self for method chaining
        """
        if queries:
            self._queries = queries
            # Use pack_queries for consistent display (it handles shortening internally)
            packed = pack_queries(*[f"{q}" for q in queries])
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
        """Add execution trace for later inclusion in complete render.
        
        Args:
            execution_trace: Execution trace string
            
        Returns:
            Self for method chaining
        """
        self._execution_trace = execution_trace
        return self
    
    def render(self) -> list[str]:
        """Build and return the complete rendered content including tool line and trace.
        
        Returns:
            List of markdown parts (tool line and optional trace block)
        """
        parts = []
        
        # Get tool icon and name
        tool_icon = ICONS.get("list_documents_call", ICONS["processing"])
        tool_name = "Documents"
        
        # Get status icon
        from ....style import STATUS_ICONS
        status_icon = STATUS_ICONS.get(self._status, STATUS_ICONS["default"])
        
        # Build result summary
        result_summary = ""
        if self._parts:
            result_summary = f" {ICONS['bullet']} ".join(self._parts)
        elif self._status == "searching":
            result_summary = f"{ICONS['searching']} init"
        else:
            result_summary = f"{ICONS['processing']}listing documents..."
        
        # Create complete tool line
        tool_line = f"{tool_icon} _{tool_name}_ • {status_icon}_{self._status}_"
        if result_summary:
            tool_line += f" {ICONS['bullet']} {result_summary}"
        
        parts.append(tool_line)
        
        # Add execution trace if available
        if self._execution_trace:
            from ....builder import TextBuilder
            trace_block = TextBuilder.from_text(self._execution_trace).with_slide(max_lines=3, format_type="text").build()
            if trace_block:
                parts.extend(trace_block)
        
        return parts
    
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
        
        # Add execution trace if available
        execution_trace = getattr(tool_item, "execution_trace", None)
        if execution_trace:
            renderer.with_execution_trace(execution_trace)
        
        return renderer 