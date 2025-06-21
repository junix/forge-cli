"""Page reader tool renderer for plaintext display system."""

from typing import Any

from .base import PlaintextToolRenderBase
from ..config import PlaintextDisplayConfig
from ..styles import PlaintextStyles
from ....style import ICONS


class PlaintextPageReaderToolRender(PlaintextToolRenderBase):
    """Plaintext page reader tool renderer."""
    
    def get_tool_metadata(self) -> tuple[str, str]:
        """Get tool icon and display name.
        
        Returns:
            Tuple of (tool_icon, tool_name)
        """
        return ICONS.get("page_reader_call", "📄"), "Page Reader"
    
    def get_tool_details(self) -> str:
        """Get page reader specific details.
        
        Returns:
            Formatted details string showing document and page info
        """
        if not self._tool_item:
            return ""
        
        parts = []
        
        # Document and page info
        document_id = getattr(self._tool_item, "document_id", None)
        if document_id:
            # Shorten document ID for display
            doc_short = document_id[:8] if len(document_id) > 8 else document_id
            start_page = getattr(self._tool_item, "start_page", None)
            end_page = getattr(self._tool_item, "end_page", None)

            if start_page is not None:
                if end_page is not None and end_page != start_page:
                    page_info = f"p.{start_page}-{end_page}"
                else:
                    page_info = f"p.{start_page}"
                parts.append(f"{ICONS['page_reader_call']}doc:{doc_short} [{page_info}]")
            else:
                parts.append(f"{ICONS['page_reader_call']}doc:{doc_short}")
        
        # Show progress if available (inherited from TraceableToolCall)
        progress = getattr(self._tool_item, "progress", None)
        if progress is not None:
            progress_percent = int(progress * 100)
            parts.append(f"{ICONS['processing']}{progress_percent}%")
        
        # Show execution trace preview if available (for traceable tools)
        execution_trace = getattr(self._tool_item, "execution_trace", None)
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
                    parts.append(f"{ICONS['check']}{message}")
        
        return f" {ICONS['bullet']} ".join(parts) if parts else ""
    
    @classmethod
    def from_tool_item(cls, tool_item: Any, styles: PlaintextStyles, config: PlaintextDisplayConfig) -> "PlaintextPageReaderToolRender":
        """Factory method to create renderer from tool item.
        
        Args:
            tool_item: Page reader tool item
            styles: Style manager instance
            config: Display configuration
            
        Returns:
            Page reader tool renderer
        """
        return cls(styles, config).with_tool_item(tool_item) 