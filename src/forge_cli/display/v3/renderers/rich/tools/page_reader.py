"""Page reader tool renderer for Rich display system."""

from rich.markdown import Markdown
from forge_cli.response._types.response_function_page_reader import ResponseFunctionPageReader
from ....style import ICONS, STATUS_ICONS, pack_queries
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
    
    def with_document_title(self, document_title: str | None) -> "PageReaderToolRender":
        """Add document title display to the render.
        
        Args:
            document_title: The title of the document being read
            
        Returns:
            Self for method chaining
        """
        if document_title:
            # Truncate very long titles for readability
            if len(document_title) > 30:
                display_title = document_title[:27] + "..."
            else:
                display_title = document_title
            self._parts.append(f'{ICONS["page_reader_call"]}"{display_title}"')
        return self
    
    def with_page_range(self, start_page: int | None, end_page: int | None) -> "PageReaderToolRender":
        """Add page range display to the render.
        
        Args:
            start_page: Starting page number
            end_page: Ending page number
            
        Returns:
            Self for method chaining
        """
        if start_page is not None:
            if end_page is not None and end_page != start_page:
                page_range = f"pp.{start_page}-{end_page}"
            else:
                page_range = f"p.{start_page}"
            self._parts.append(f"{ICONS['pages']}{page_range}")
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
    
    def with_query(self, query: str | None) -> "PageReaderToolRender":
        """Add query display to the render using consistent styling.
        
        Args:
            query: The search query within the pages
            
        Returns:
            Self for method chaining
        """
        if query:
            # Use pack_queries for consistent display style
            packed = pack_queries(f'"{query}"')
            self._parts.append(packed)
        return self
    
    def render(self) -> Markdown:
        """Build and return the complete rendered content as Markdown.
        
        Returns:
            Markdown object with formatted tool line
        """
        # Get tool icon and name
        tool_icon = ICONS.get("page_reader_call", ICONS["processing"])
        tool_name = "PageReader"
        
        # Get status icon
        status_icon = STATUS_ICONS.get(self._status, STATUS_ICONS["default"])
        
        # Build result summary
        result_summary = ""
        if self._parts:
            result_summary = f" {ICONS['bullet']} ".join(self._parts)
        else:
            result_summary = f"{ICONS['processing']}reading pages..."
        
        # Create complete tool line
        tool_line = f"{tool_icon} _{tool_name}_ • {status_icon}_{self._status}_"
        if result_summary:
            tool_line += f" {ICONS['bullet']} {result_summary}"
        
        return Markdown(tool_line)
    
    @classmethod
    def from_tool_item(cls, tool_item: ResponseFunctionPageReader) -> "PageReaderToolRender":
        """Create a page reader tool renderer from a tool item.
        
        Args:
            tool_item: The page reader tool item to render
            
        Returns:
            PageReaderToolRender instance configured with the tool item data
        """
        renderer = cls()
        
        # Add document title if available
        if tool_item.document_title:
            renderer.with_document_title(tool_item.document_title)
        
        # Add page range if available
        if tool_item.start_page is not None:
            renderer.with_page_range(tool_item.start_page, tool_item.end_page)
        
        # Add status
        renderer.with_status(tool_item.status)
        
        # Add query if available
        if hasattr(tool_item, 'query') and tool_item.query:
            renderer.with_query(tool_item.query)
        
        return renderer 