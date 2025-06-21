"""Page reader tool renderer for Rich display system."""

from forge_cli.response._types.response_function_page_reader import ResponseFunctionPageReader
from ....style import ICONS
from ...rendable import Rendable


class PageReaderToolRender(Rendable):
    """Specialized renderer for page reader tool calls.
    
    This class handles the rendering of page reader tool calls with consistent styling
    and support for all page reader tool properties.
    """
    
    def __init__(self):
        """Initialize the page reader tool renderer."""
        self._parts = []
        self._status = "in_progress"
    
    def with_document_id(self, document_id: str) -> "PageReaderToolRender":
        """Add document ID display to the render.
        
        Args:
            document_id: The document ID to read from
            
        Returns:
            Self for method chaining
        """
        if document_id:
            doc_short = document_id[:12] + "..." if len(document_id) > 12 else document_id
            self._parts.append(f"{ICONS['page_reader_call']}{doc_short}")
        return self
    
    def with_page_range(self, start_page: int | None, end_page: int | None) -> "PageReaderToolRender":
        """Add page range display to the render.
        
        Args:
            start_page: Starting page number (0-indexed)
            end_page: Ending page number (0-indexed), None means single page
            
        Returns:
            Self for method chaining
        """
        if start_page is not None:
            if end_page is not None and end_page != start_page:
                # Convert from 0-indexed to 1-indexed for display
                display_start = start_page + 1
                display_end = end_page + 1
                self._parts.append(f"{ICONS['page_reader_call']}[p.{display_start}-{display_end}]")
            else:
                # Single page
                display_page = start_page + 1
                self._parts.append(f"{ICONS['page_reader_call']}[p.{display_page}]")
        return self
    
    def with_progress(self, progress: float | None) -> "PageReaderToolRender":
        """Add progress display to the render.
        
        Args:
            progress: Progress value from 0.0 to 1.0, or None if not available
            
        Returns:
            Self for method chaining
        """
        if progress is not None:
            progress_percent = int(progress * 100)
            self._parts.append(f"{ICONS['processing']}{progress_percent}%")
        return self
    
    def with_status(self, status: str) -> "PageReaderToolRender":
        """Add status display to the render.
        
        Args:
            status: Current status of the page reader call
            
        Returns:
            Self for method chaining
        """
        self._status = status
        return self
    
    def with_execution_trace(self, execution_trace: str | None) -> "PageReaderToolRender":
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
            The formatted display string for the page reader tool
        """
        if self._parts:
            return f" {ICONS['bullet']} ".join(self._parts)
        return f"{ICONS['processing']}reading pages..."
    
    @classmethod
    def from_tool_item(cls, tool_item: ResponseFunctionPageReader) -> "PageReaderToolRender":
        """Create a page reader tool renderer from a tool item.
        
        Args:
            tool_item: The page reader tool item to render
            
        Returns:
            PageReaderToolRender instance configured with the tool item data
        """
        renderer = cls()
        
        # Add document ID
        renderer.with_document_id(tool_item.document_id)
        
        # Add page range
        renderer.with_page_range(tool_item.start_page, tool_item.end_page)
        
        # Add progress if available
        if hasattr(tool_item, 'progress') and tool_item.progress is not None:
            renderer.with_progress(tool_item.progress)
        
        # Add status
        renderer.with_status(tool_item.status)
        
        return renderer 