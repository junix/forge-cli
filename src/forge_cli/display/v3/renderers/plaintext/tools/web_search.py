"""Web search tool renderer for plaintext display system."""

from forge_cli.response._types.response_function_web_search import ResponseFunctionWebSearch
from .base import PlaintextToolRenderBase
from ..config import PlaintextDisplayConfig
from ..styles import PlaintextStyles


class PlaintextWebSearchToolRender(PlaintextToolRenderBase):
    """Plaintext renderer for web search tool calls."""

    def _render_tool_specific_content(self) -> str:
        """Render web search specific content.
        
        Returns:
            Web search content string
        """
        if not self._tool_item:
            return ""

        parts = []
        
        # Add query if available
        if hasattr(self._tool_item, 'query') and self._tool_item.query:
            parts.append(f"Query: {self._tool_item.query}")
        
        # Add result count if available
        if hasattr(self._tool_item, 'result_count') and self._tool_item.result_count is not None:
            result_word = "result" if self._tool_item.result_count == 1 else "results"
            parts.append(f"Found: {self._tool_item.result_count} {result_word}")
        
        # Add progress if available
        if hasattr(self._tool_item, 'progress') and self._tool_item.progress is not None:
            progress_percent = int(self._tool_item.progress * 100)
            parts.append(f"Progress: {progress_percent}%")
        
        return self._format_list(parts)

    @classmethod
    def from_tool_item(cls, tool_item: ResponseFunctionWebSearch, styles: PlaintextStyles, config: PlaintextDisplayConfig) -> "PlaintextWebSearchToolRender":
        """Create web search tool renderer from tool item.
        
        Args:
            tool_item: Web search tool item
            styles: Plaintext styling configuration
            config: Display configuration
            
        Returns:
            PlaintextWebSearchToolRender instance
        """
        renderer = cls(styles, config)
        return renderer.with_tool_item(tool_item) 