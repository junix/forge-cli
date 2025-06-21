"""File reader tool renderer for Rich display system."""

from rich.text import Text
from forge_cli.response._types.response_function_file_reader import ResponseFunctionFileReader
from ....style import ICONS, pack_queries, get_status_color
from ...rendable import Rendable


class FileReaderToolRender(Rendable):
    """Specialized renderer for file reader tool calls.
    
    This class handles the rendering of file reader tool calls with consistent styling
    and support for all file reader tool properties.
    """
    
    def __init__(self):
        """Initialize the file reader tool renderer."""
        self._parts = []
        self._doc_ids = []
        self._status = "in_progress"
        self._execution_trace = None
        self._progress = None
        self._query = None
    
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
            
            # Extract file extension for type label
            file_ext = ""
            if "." in filename:
                file_ext = filename.split(".")[-1].upper()
            else:
                file_ext = "FILE"
            
            self._parts.append(f'{ICONS["file_reader_call"]}"{display_name}" [{file_ext}]')
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
                # Use first doc_id as fallback with file: prefix, shortened to 12 chars (doc_12345678)
                first_doc = doc_ids[0][:12] if len(doc_ids[0]) > 12 else doc_ids[0]
                self._parts.append(f"{ICONS['file_reader_call']}file:{first_doc}")
        return self
    
    def with_progress(self, progress: float | None) -> "FileReaderToolRender":
        """Add progress display to the render.
        
        Args:
            progress: Progress as a float between 0 and 1
            
        Returns:
            Self for method chaining
        """
        if progress is not None:
            self._progress = progress
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
        """Add query display to the render using consistent styling.
        
        Args:
            query: The search query within the file
            
        Returns:
            Self for method chaining
        """
        if query:
            self._query = query
        return self
    
    def with_file_size(self, file_size: int | None) -> "FileReaderToolRender":
        """Add file size display to the render.
        
        Args:
            file_size: File size in bytes
            
        Returns:
            Self for method chaining
        """
        if file_size is not None:
            # Convert bytes to human-readable format
            if file_size < 1024:
                size_str = f"{file_size}B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size // 1024}KB"
            else:
                size_str = f"{file_size // (1024 * 1024)}MB"
            self._parts.append(f"{ICONS['info']}{size_str}")
        return self
    
    def with_file_type(self, file_type: str | None) -> "FileReaderToolRender":
        """Add file type display to the render.
        
        Args:
            file_type: MIME type or file extension
            
        Returns:
            Self for method chaining
        """
        if file_type:
            # Extract main type from MIME type like "application/pdf" -> "application"
            if "/" in file_type:
                main_type = file_type.split("/")[0]
            else:
                main_type = file_type
            self._parts.append(f"{ICONS['file']}type:{main_type}")
        return self
    
    def with_page_count(self, page_count: int | None) -> "FileReaderToolRender":
        """Add page count display to the render.
        
        Args:
            page_count: Number of pages in the document
            
        Returns:
            Self for method chaining
        """
        if page_count is not None:
            page_word = "page" if page_count == 1 else "pages"
            self._parts.append(f"{ICONS['pages']}{page_count} {page_word}")
        return self
    
    def with_execution_trace(self, execution_trace: str | None) -> "FileReaderToolRender":
        """Add execution trace for later inclusion in complete render.
        
        Args:
            execution_trace: Execution trace string
            
        Returns:
            Self for method chaining
        """
        self._execution_trace = execution_trace
        return self
    

    
    def render(self) -> list[Text]:
        """Build and return the complete rendered content including tool line and trace.
        
        Returns:
            List of Text objects (tool line and optional trace block)
        """
        parts = []
        
        # Get tool icon and name (keep original icons unchanged)
        tool_icon = ICONS.get("file_reader_call", ICONS["processing"])
        tool_name = "Reader"
        
        # Get status color using mood-based colors
        status_color = get_status_color(self._status)
        
        # Build the tool line with colors
        tool_line = Text()
        
        # Add tool icon and name - tool name in bright_white + bold
        tool_line.append(f"{tool_icon} ")
        tool_line.append(tool_name, style="bright_white bold italic")
        tool_line.append(" • ")
        
        # Add status with mood-based color
        from ....style import STATUS_ICONS
        status_icon = STATUS_ICONS.get(self._status, STATUS_ICONS["default"])
        tool_line.append(f"{status_icon}")
        tool_line.append(self._status, style=f"{status_color} italic")
        
        # Add progress if available - bright_cyan for active feeling
        if self._progress is not None:
            progress_percent = int(self._progress * 100)
            tool_line.append(f" {ICONS['bullet']} ")
            tool_line.append(f"{ICONS['processing']}")
            tool_line.append(f"{progress_percent}%", style="bright_cyan bold")
        
        # Add query if available - bright_yellow for attention
        if self._query:
            packed = pack_queries(f'"{self._query}"')
            tool_line.append(f" {ICONS['bullet']} ")
            tool_line.append(packed, style="bright_yellow")
        
        # Add other parts (file info, etc.) in default white
        if self._parts:
            result_summary = f" {ICONS['bullet']} ".join(self._parts)
            tool_line.append(f" {ICONS['bullet']} ")
            tool_line.append(result_summary)
        elif self._doc_ids and not self._parts:
            first_doc = self._doc_ids[0][:12] if len(self._doc_ids[0]) > 12 else self._doc_ids[0]
            tool_line.append(f" {ICONS['bullet']} ")
            tool_line.append(f"{ICONS['file_reader_call']}file:{first_doc}")
        elif not self._parts and not self._query and self._progress is None:
            tool_line.append(f" {ICONS['bullet']} ")
            tool_line.append(f"{ICONS['processing']}reading file...")
        
        parts.append(tool_line)
        
        # Add execution trace if available
        if self._execution_trace:
            from ....builder import TextBuilder
            trace_block = TextBuilder.from_text(self._execution_trace).with_slide(max_lines=3, format_type="text").build()
            if trace_block:
                # Convert trace block strings to Text objects
                for trace_line in trace_block:
                    if isinstance(trace_line, str):
                        parts.append(Text(trace_line))
                    else:
                        parts.append(trace_line)
        
        return parts
    
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