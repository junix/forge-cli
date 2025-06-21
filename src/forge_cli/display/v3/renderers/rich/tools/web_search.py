"""Web search tool renderer for Rich display system."""

from rich.markdown import Markdown
from forge_cli.response._types.response_function_web_search import ResponseFunctionWebSearch
from ....style import ICONS, STATUS_ICONS, pack_queries
from ....builder import TextBuilder
from ...rendable import Rendable


class WebSearchToolRender(Rendable):
    """Specialized renderer for web search tool calls.
    
    This class handles the rendering of web search tool calls with consistent styling
    and support for all web search tool properties.
    """
    
    def __init__(self):
        """Initialize the web search tool renderer."""
        self._parts = []
        self._status = "in_progress"
        self._execution_trace = None
    
    def with_queries(self, *queries: str) -> "WebSearchToolRender":
        """Add search queries display to the render using consistent styling.
        
        Args:
            *queries: Variable number of search queries
            
        Returns:
            Self for method chaining
        """
        if queries:
            # Use pack_queries for consistent display style with multiple queries
            formatted_queries = [f'"{q}"' for q in queries]
            packed = pack_queries(*formatted_queries)
            self._parts.append(packed)
        return self
    
    def with_result_count(self, result_count: int | None) -> "WebSearchToolRender":
        """Add result count display to the render.
        
        Args:
            result_count: Number of search results found
            
        Returns:
            Self for method chaining
        """
        if result_count is not None:
            result_word = "result" if result_count == 1 else "results"
            self._parts.append(f"{ICONS['search_results']}{result_count} {result_word}")
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
    
    def with_progress(self, progress: float | None) -> "WebSearchToolRender":
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
    
    def with_execution_trace(self, execution_trace: str | None) -> "WebSearchToolRender":
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
        tool_icon = ICONS.get("web_search_call", ICONS["search"])
        tool_name = "WebSearch"
        
        # Get status icon
        status_icon = STATUS_ICONS.get(self._status, STATUS_ICONS["default"])
        
        # Build result summary
        result_summary = ""
        if self._parts:
            result_summary = f" {ICONS['bullet']} ".join(self._parts)
        else:
            result_summary = f"{ICONS['processing']}searching web..."
        
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
            renderer.with_queries(*tool_item.queries)
        
        # Add result count if available
        if hasattr(tool_item, 'result_count') and tool_item.result_count is not None:
            renderer.with_result_count(tool_item.result_count)
        
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