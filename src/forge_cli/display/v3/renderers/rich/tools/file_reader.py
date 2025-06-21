"""File reader tool renderer for Rich display system."""

from forge_cli.response._types.response_function_file_reader import ResponseFunctionFileReader
from ....style import ICONS
from ...rendable import ToolRendable


class FileReaderToolRender(ToolRendable):
    """Specialized renderer for file reader tool calls.
    
    This class handles the rendering of file reader tool calls with consistent styling
    and support for all file reader tool properties.
    """
    
    def __init__(self):
        """Initialize the file reader tool renderer."""
        super().__init__()
        self._parts = []
        self._doc_ids = []
    
    def get_tool_metadata(self) -> tuple[str, str]:
        """Get tool icon and display name for file reader.
        
        Returns:
            Tuple of (tool_icon, tool_name)
        """
        return ICONS.get("file_reader_call", ICONS["processing"]), "Reader"
    
    def with_filename(self, filename: str | None) -> "FileReaderToolRender":
        """Add filename display to the render.
        
        Args:
            filename: The name of the file being read
            
        Returns:
            Self for method chaining
        """
        if filename:
            # Truncate very long filenames
            if len(filename) > 25:
                display_name = filename[:22] + "..."
            else:
                display_name = filename
            self._parts.append(f"{ICONS['file_reader_call']}{display_name}")
        return self
    
    def with_doc_ids(self, doc_ids: list[str]) -> "FileReaderToolRender":
        """Add document IDs to the render.
        
        Args:
            doc_ids: List of document IDs
            
        Returns:
            Self for method chaining
        """
        if doc_ids:
            self._doc_ids = doc_ids
            # Only show if no filename was already added
            if not any(ICONS['file_reader_call'] in part for part in self._parts):
                # Use first doc_id as fallback, shortened
                first_doc = doc_ids[0][:8] if len(doc_ids[0]) > 8 else doc_ids[0]
                self._parts.append(f"{ICONS['file_reader_call']}{first_doc}")
        return self
    
    def with_progress(self, progress: float | None) -> "FileReaderToolRender":
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
    
    def with_status(self, status: str) -> "FileReaderToolRender":
        """Add status display to the render.
        
        Args:
            status: Current status of the file reader call
            
        Returns:
            Self for method chaining
        """
        self._status = status
        return self
    
    def with_query(self, query: str | None) -> "FileReaderToolRender":
        """Add query display to the render.
        
        Args:
            query: The search query within the file
            
        Returns:
            Self for method chaining
        """
        if query:
            # Truncate long queries
            if len(query) > 20:
                display_query = query[:17] + "..."
            else:
                display_query = query
            self._parts.append(f"{ICONS['search']}'{display_query}'")
        return self
    
    def with_file_size(self, file_size: str | None) -> "FileReaderToolRender":
        """Add file size display to the render.
        
        Args:
            file_size: Human-readable file size
            
        Returns:
            Self for method chaining
        """
        if file_size:
            self._parts.append(f"{ICONS['info']}{file_size}")
        return self
    
    def with_file_type(self, file_type: str | None) -> "FileReaderToolRender":
        """Add file type display to the render.
        
        Args:
            file_type: MIME type or file extension
            
        Returns:
            Self for method chaining
        """
        if file_type:
            self._parts.append(f"{ICONS['file']}{file_type}")
        return self
    
    def with_page_count(self, page_count: int | None) -> "FileReaderToolRender":
        """Add page count display to the render.
        
        Args:
            page_count: Number of pages in the document
            
        Returns:
            Self for method chaining
        """
        if page_count is not None:
            self._parts.append(f"{ICONS['pages']}{page_count}p")
        return self
    
    def with_execution_trace(self, execution_trace: str | None) -> "FileReaderToolRender":
        """Add execution trace preview to the render.
        
        Args:
            execution_trace: Execution trace string
            
        Returns:
            Self for method chaining
        """
        if execution_trace:
            # Show last trace line as a preview
            trace_lines = execution_trace.strip().split("\n")
            if trace_lines:
                last_line = trace_lines[-1]
                # Extract just the message part (remove timestamp and step name)
                if "] " in last_line:
                    message = last_line.split("] ")[-1][:30]
                    if len(message) > 27:
                        message = message[:27] + "..."
                    self._parts.append(f"{ICONS['check']}{message}")
        return self
    
    def render(self) -> str:
        """Build and return the final rendered string for result summary only.
        
        Returns:
            The formatted display string for the file reader tool results
        """
        if self._parts:
            return f" {ICONS['bullet']} ".join(self._parts)
        
        # Default fallback if no parts
        if self._doc_ids:
            first_doc = self._doc_ids[0][:8] if len(self._doc_ids[0]) > 8 else self._doc_ids[0]
            return f"{ICONS['file_reader_call']}{first_doc}"
        
        return f"{ICONS['processing']}reading file..."
    
    @classmethod
    def from_tool_item(cls, tool_item: ResponseFunctionFileReader) -> "FileReaderToolRender":
        """Create a file reader tool renderer from a tool item.
        
        Args:
            tool_item: The file reader tool item to render
            
        Returns:
            FileReaderToolRender instance configured with the tool item data
        """
        renderer = cls()
        
        # Add filename if available (custom attribute)
        file_name = getattr(tool_item, "file_name", None)
        if file_name:
            renderer.with_filename(file_name)
        
        # Add doc_ids if available
        if tool_item.doc_ids:
            renderer.with_doc_ids(tool_item.doc_ids)
        
        # Add progress if available (inherited from TraceableToolCall)
        progress = getattr(tool_item, "progress", None)
        if progress is not None:
            renderer.with_progress(progress)
        
        # Add status
        renderer.with_status(tool_item.status)
        
        # Add execution trace if available (for traceable tools)
        execution_trace = getattr(tool_item, "execution_trace", None)
        if execution_trace:
            renderer.with_execution_trace(execution_trace)
        
        return renderer 