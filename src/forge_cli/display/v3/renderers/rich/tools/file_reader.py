"""File reader tool renderer for Rich display system."""

from ....style import ICONS
from ...rendable import Rendable


class FileReaderToolRender(Rendable):
    """Specialized renderer for file reader tool calls.
    
    This class handles the rendering of file reader tool calls with consistent styling
    and support for all file reader tool properties.
    """
    
    def __init__(self):
        """Initialize the file reader tool renderer."""
        self._parts = []
        self._status = "in_progress"
        self._execution_trace = None
    
    def with_filename(self, filename: str | None) -> "FileReaderToolRender":
        """Add filename display to the render.
        
        Args:
            filename: The filename to display, or None if not available
            
        Returns:
            Self for method chaining
        """
        if filename:
            # Show file extension
            ext = filename.split(".")[-1].lower() if "." in filename else "file"
            name_short = filename[:30] + "..." if len(filename) > 30 else filename
            self._parts.append(f'{ICONS["file_reader_call"]}"{name_short}" [{ext.upper()}]')
        return self
    
    def with_doc_ids(self, doc_ids: list[str]) -> "FileReaderToolRender":
        """Add document ID display to the render.
        
        Args:
            doc_ids: List of document IDs
            
        Returns:
            Self for method chaining
        """
        if doc_ids and len(doc_ids) > 0:
            self._parts.append(f"{ICONS['file_reader_call']}file:{doc_ids[0][:12]}...")
        return self
    
    def with_progress(self, progress: float | None) -> "FileReaderToolRender":
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
    
    def with_status(self, status: str) -> "FileReaderToolRender":
        """Add status display to the render.
        
        Args:
            status: Current status of the file reader call
            
        Returns:
            Self for method chaining
        """
        self._status = status
        return self
    
    def with_query(self, query: str) -> "FileReaderToolRender":
        """Add query display to the render.
        
        Args:
            query: The query being processed by the file reader
            
        Returns:
            Self for method chaining
        """
        if query and query.strip():
            query_short = query[:40] + "..." if len(query) > 40 else query
            self._parts.append(f'{ICONS["query"]}query: "{query_short}"')
        return self
    
    def with_execution_trace(self, execution_trace: str | None) -> "FileReaderToolRender":
        """Add execution trace to the render (handled separately in trace blocks).
        
        Args:
            execution_trace: Execution trace string
            
        Returns:
            Self for method chaining
        """
        self._execution_trace = execution_trace
        return self
    
    def with_file_size(self, file_size: int | None) -> "FileReaderToolRender":
        """Add file size display to the render.
        
        Args:
            file_size: File size in bytes, or None if not available
            
        Returns:
            Self for method chaining
        """
        if file_size is not None:
            if file_size < 1024:
                size_str = f"{file_size}B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size // 1024}KB"
            else:
                size_str = f"{file_size // (1024 * 1024)}MB"
            self._parts.append(f"{ICONS['file_reader_call']}{size_str}")
        return self
    
    def with_file_type(self, file_type: str | None) -> "FileReaderToolRender":
        """Add file type display to the render.
        
        Args:
            file_type: MIME type or file type string
            
        Returns:
            Self for method chaining
        """
        if file_type:
            # Extract main type from MIME type
            main_type = file_type.split('/')[0] if '/' in file_type else file_type
            self._parts.append(f"{ICONS['file_reader_call']}type:{main_type}")
        return self
    
    def with_page_count(self, page_count: int | None) -> "FileReaderToolRender":
        """Add page count display to the render.
        
        Args:
            page_count: Number of pages in the document
            
        Returns:
            Self for method chaining
        """
        if page_count is not None and page_count > 0:
            self._parts.append(f"{ICONS['page_reader_call']}{page_count} pages")
        return self
    
    def render(self) -> str:
        """Build and return the final rendered string.
        
        Returns:
            The formatted display string for the file reader tool
        """
        if self._parts:
            return f" {ICONS['bullet']} ".join(self._parts)
        return f"{ICONS['processing']}loading file..."
    
    @classmethod
    def from_tool_item(cls, tool_item) -> str:
        """Create a file reader tool render from a tool item and return the formatted string.
        
        This is a convenience method that matches the current rendering style exactly.
        
        Args:
            tool_item: The file reader tool item to render
            
        Returns:
            Formatted display string
        """
        renderer = cls()
        parts = []
        
        # File identification - matches current logic exactly
        file_name = getattr(tool_item, "file_name", None)
        if file_name:
            # Show file extension
            ext = file_name.split(".")[-1].lower() if "." in file_name else "file"
            name_short = file_name[:30] + "..." if len(file_name) > 30 else file_name
            parts.append(f'{ICONS["file_reader_call"]}"{name_short}" [{ext.upper()}]')
        elif tool_item.doc_ids and len(tool_item.doc_ids) > 0:
            parts.append(f"{ICONS['file_reader_call']}file:{tool_item.doc_ids[0][:12]}...")
        
        # Show progress if available (inherited from TraceableToolCall)
        progress = getattr(tool_item, "progress", None)
        if progress is not None:
            progress_percent = int(progress * 100)
            parts.append(f"{ICONS['processing']}{progress_percent}%")
        
        # Note: execution trace is now handled separately in trace block
        
        if parts:
            return f" {ICONS['bullet']} ".join(parts)
        return f"{ICONS['processing']}loading file..." 