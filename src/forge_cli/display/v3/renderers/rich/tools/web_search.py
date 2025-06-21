"""Web search tool renderer for Rich display system."""

from forge_cli.response._types.response_function_web_search import ResponseFunctionWebSearch
from ....style import ICONS, pack_queries
from ...rendable import Rendable


class WebSearchToolRender(Rendable):
    """Specialized renderer for web search tool calls.
    
    This class handles the rendering of web search tool calls with consistent styling
    and support for all web search tool properties.
    """
    
    def __init__(self):
        """Initialize the web search tool renderer."""
        self._parts = []
        self._queries = []
        self._status = "in_progress"
        self._execution_trace = None
    
    def with_queries(self, queries: list[str]) -> "WebSearchToolRender":
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
    
    def with_status(self, status: str) -> "WebSearchToolRender":
        """Add status display to the render.
        
        Args:
            status: Current status of the web search call
            
        Returns:
            Self for method chaining
        """
        self._status = status
        return self
    
    def with_results_count(self, count: int | None) -> "WebSearchToolRender":
        """Add results count to the render.
        
        Args:
            count: Number of search results found
            
        Returns:
            Self for method chaining
        """
        if count is not None:
            self._parts.append(f"{ICONS['check']}{count} results")
        return self
    
    def with_execution_trace(self, execution_trace: str | None) -> "WebSearchToolRender":
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
        tool_icon = ICONS.get("web_search_call", ICONS["processing"])
        tool_name = "Web"
        
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
            result_summary = f"{ICONS['processing']}searching web..."
        
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
    def from_tool_item(cls, tool_item: ResponseFunctionWebSearch) -> "WebSearchToolRender":
        """Create a web search tool renderer from a tool item.
        
        Args:
            tool_item: The web search tool item to render
            
        Returns:
            WebSearchToolRender instance configured with the tool item data
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
        
        # Add execution trace if available (for traceable tools)
        execution_trace = getattr(tool_item, "execution_trace", None)
        if execution_trace:
            renderer.with_execution_trace(execution_trace)
        
        return renderer 