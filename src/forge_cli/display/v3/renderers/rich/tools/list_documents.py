"""List documents tool renderer for Rich display system."""

from rich.markdown import Markdown
from forge_cli.response._types.response_list_documents_tool_call import ResponseListDocumentsToolCall
from ....style import ICONS, STATUS_ICONS, pack_queries
from ....builder import TextBuilder
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
        self._execution_trace = None
    
    def with_query(self, query: str | None) -> "ListDocumentsToolRender":
        """Add search query display to the render using consistent styling.
        
        Args:
            query: The search query for filtering documents
            
        Returns:
            Self for method chaining
        """
        if query:
            # Use pack_queries for consistent display style
            packed = pack_queries(f'"{query}"')
            self._parts.append(packed)
        return self
    
    def with_document_count(self, document_count: int | None) -> "ListDocumentsToolRender":
        """Add document count display to the render.
        
        Args:
            document_count: Number of documents found
            
        Returns:
            Self for method chaining
        """
        if document_count is not None:
            doc_word = "document" if document_count == 1 else "documents"
            self._parts.append(f"{ICONS['list_documents_call']}{document_count} {doc_word}")
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
    
    def with_progress(self, progress: float | None) -> "ListDocumentsToolRender":
        """Add progress display to the render.
        
        Args:
            progress: Progress as a float between 0 and 1
            
        Returns:
            Self for method chaining
        """
        if progress is not None:
            progress_percent = int(progress * 100)
            self._parts.append(f"{ICONS['processing']}{progress_percent}%")
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
    
    def render(self) -> list[Markdown]:
        """Build and return the complete rendered content including tool line and trace.
        
        Returns:
            List of Markdown objects (tool line and optional trace block)
        """
        parts = []
        
        # Get tool icon and name
        tool_icon = ICONS.get("list_documents_call", ICONS["processing"])
        tool_name = "ListDocs"
        
        # Get status icon
        status_icon = STATUS_ICONS.get(self._status, STATUS_ICONS["default"])
        
        # Build result summary
        result_summary = ""
        if self._parts:
            result_summary = f" {ICONS['bullet']} ".join(self._parts)
        else:
            result_summary = f"{ICONS['processing']}listing documents..."
        
        # Create complete tool line
        tool_line = f"{tool_icon} _{tool_name}_ • {status_icon}_{self._status}_"
        if result_summary:
            tool_line += f" {ICONS['bullet']} {result_summary}"
        
        parts.append(Markdown(tool_line))
        
        # Add execution trace if available
        if self._execution_trace:
            trace_block = TextBuilder.from_text(self._execution_trace).with_slide(max_lines=3, format_type="text").build()
            if trace_block:
                # Convert trace block strings to Markdown objects
                for trace_line in trace_block:
                    parts.append(Markdown(trace_line))
        
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
        
        # Add query if available
        if hasattr(tool_item, 'query') and tool_item.query:
            renderer.with_query(tool_item.query)
        
        # Add document count if available
        if hasattr(tool_item, 'document_count') and tool_item.document_count is not None:
            renderer.with_document_count(tool_item.document_count)
        
        # Add progress if available
        if hasattr(tool_item, 'progress') and tool_item.progress is not None:
            renderer.with_progress(tool_item.progress)
        
        # Add status
        renderer.with_status(tool_item.status)
        
        # Add execution trace if available
        execution_trace = getattr(tool_item, "execution_trace", None)
        if execution_trace:
            renderer.with_execution_trace(execution_trace)
        
        return renderer 