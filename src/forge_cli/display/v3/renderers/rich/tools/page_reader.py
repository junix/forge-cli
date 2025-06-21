"""Page reader tool renderer for Rich display system."""

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
        self._document_id = None
        self._start_page = None
        self._end_page = None
    
    def with_document_id(self, document_id: str | None) -> "PageReaderToolRender":
        """Add document ID display to the render.
        
        Args:
            document_id: The document ID to display
            
        Returns:
            Self for method chaining
        """
        if document_id:
            self._document_id = document_id
        return self
    
    def with_page_range(self, start_page: int | None, end_page: int | None) -> "PageReaderToolRender":
        """Add page range display to the render.
        
        Args:
            start_page: Starting page number
            end_page: Ending page number
            
        Returns:
            Self for method chaining
        """
        self._start_page = start_page
        self._end_page = end_page
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
        parts = []
        
        # Document identification with page range
        if self._document_id:
            doc_short = self._document_id
            if self._start_page is not None:
                if self._end_page is not None and self._end_page != self._start_page:
                    page_info = f"p.{self._start_page}-{self._end_page}"
                else:
                    page_info = f"p.{self._start_page}"
                parts.append(f"{ICONS['page_reader_call']} 󰈙 {doc_short} 󰕅 [{page_info}]")
            else:
                parts.append(f"{ICONS['page_reader_call']} 󰈙 {doc_short}")
        
        # Add additional parts from builder methods
        parts.extend(self._parts)
        
        if parts:
            return f" {ICONS['bullet']} ".join(parts)
        return f"{ICONS['processing']}loading pages..."
    
    @classmethod
    def from_tool_item(cls, tool_item) -> str:
        """Create a page reader tool render from a tool item and return the formatted string.
        
        Args:
            tool_item: The page reader tool item to render
            
        Returns:
            Formatted display string
        """
        renderer = cls()
        
        # Add document ID
        if hasattr(tool_item, 'document_id'):
            renderer.with_document_id(tool_item.document_id)
        
        # Add page range
        start_page = getattr(tool_item, 'start_page', None)
        end_page = getattr(tool_item, 'end_page', None)
        if start_page is not None or end_page is not None:
            renderer.with_page_range(start_page, end_page)
        
        # Add progress if available
        progress = getattr(tool_item, 'progress', None)
        if progress is not None:
            renderer.with_progress(progress)
        
        # Add status
        if hasattr(tool_item, 'status'):
            renderer.with_status(tool_item.status)
        
        return renderer.render() 