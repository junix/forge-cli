"""Web search tool renderer for Rich display system."""

from rich.text import Text
from forge_cli.response._types.response_function_web_search import ResponseFunctionWebSearch
from ....style import ICONS, STATUS_ICONS, pack_queries, get_status_color
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
        self._progress = None
        self._queries = []
    
    def with_queries(self, *queries: str) -> "WebSearchToolRender":
        """Add search queries display to the render using consistent styling.
        
        Args:
            *queries: Variable number of search queries
            
        Returns:
            Self for method chaining
        """
        if queries:
            self._queries = list(queries)
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
            self._progress = progress
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
    

    
    def render(self) -> list[Text]:
        """Build and return the complete rendered content including tool line and trace.
        
        Returns:
            List of Text objects (tool line and optional trace block)
        """
        parts = []
        
        # Get tool icon and name (keep original icons unchanged)
        tool_icon = ICONS.get("web_search_call", ICONS["search"])
        tool_name = "WebSearch"
        
        # Get status color using mood-based colors
        status_color = get_status_color(self._status)
        
        # Build the tool line with colors
        tool_line = Text()
        
        # Add tool icon and name - tool name in bright_white + bold
        tool_line.append(f"{tool_icon} ")
        tool_line.append(tool_name, style="bright_white bold italic")
        tool_line.append(" • ")
        
        # Add status with mood-based color
        status_icon = STATUS_ICONS.get(self._status, STATUS_ICONS["default"])
        tool_line.append(f"{status_icon}")
        tool_line.append(self._status, style=f"{status_color} italic")
        
        # Add progress if available - bright_cyan for active feeling
        if self._progress is not None:
            progress_percent = int(self._progress * 100)
            tool_line.append(f" {ICONS['bullet']} ")
            tool_line.append(f"{ICONS['processing']}")
            tool_line.append(f"{progress_percent}%", style="bright_cyan bold")
        
        # Add queries if available - bright_yellow for attention
        if self._queries:
            formatted_queries = [f'"{q}"' for q in self._queries]
            packed = pack_queries(*formatted_queries)
            tool_line.append(f" {ICONS['bullet']} ")
            tool_line.append(packed, style="bright_yellow")
        
        # Add other parts (result count, etc.) in default white
        if self._parts:
            result_summary = f" {ICONS['bullet']} ".join(self._parts)
            tool_line.append(f" {ICONS['bullet']} ")
            tool_line.append(result_summary)
        elif not self._parts and not self._queries and self._progress is None:
            tool_line.append(f" {ICONS['bullet']} ")
            tool_line.append(f"{ICONS['processing']}searching web...")
        
        parts.append(tool_line)
        
        # Add execution trace if available
        if self._execution_trace:
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