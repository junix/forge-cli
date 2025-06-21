"""Function call tool renderer for plaintext display system."""

from forge_cli.response._types.response_function_tool_call import ResponseFunctionToolCall
from .base import PlaintextToolRenderBase
from ..config import PlaintextDisplayConfig
from ..styles import PlaintextStyles


class PlaintextFunctionCallToolRender(PlaintextToolRenderBase):
    """Plaintext renderer for function call tool calls."""

    def _render_tool_specific_content(self) -> str:
        """Render function call specific content.
        
        Returns:
            Function call content string
        """
        if not self._tool_item:
            return ""

        parts = []
        
        # Add function name
        if hasattr(self._tool_item, 'name') and self._tool_item.name:
            parts.append(f"Function: {self._tool_item.name}")
        
        # Add call ID
        if hasattr(self._tool_item, 'call_id') and self._tool_item.call_id:
            parts.append(f"Call ID: {self._tool_item.call_id}")
        
        # Add arguments if available
        if hasattr(self._tool_item, 'arguments') and self._tool_item.arguments:
            # Truncate long arguments for display
            args_str = str(self._tool_item.arguments)
            if len(args_str) > 100:
                args_str = args_str[:97] + "..."
            parts.append(f"Arguments: {args_str}")
        
        return self._format_list(parts)

    @classmethod
    def from_tool_item(cls, tool_item: ResponseFunctionToolCall, styles: PlaintextStyles, config: PlaintextDisplayConfig) -> "PlaintextFunctionCallToolRender":
        """Create function call tool renderer from tool item.
        
        Args:
            tool_item: Function call tool item
            styles: Plaintext styling configuration
            config: Display configuration
            
        Returns:
            PlaintextFunctionCallToolRender instance
        """
        renderer = cls(styles, config)
        return renderer.with_tool_item(tool_item) 