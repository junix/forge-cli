"""File reader tool renderer for plaintext display system."""

from typing import Any

from .base import PlaintextToolRenderBase
from ..config import PlaintextDisplayConfig
from ..styles import PlaintextStyles
from ....style import ICONS


class PlaintextFileReaderToolRender(PlaintextToolRenderBase):
    """Plaintext file reader tool renderer."""
    
    def get_tool_metadata(self) -> tuple[str, str]:
        """Get tool icon and display name.
        
        Returns:
            Tuple of (tool_icon, tool_name)
        """
        return ICONS.get("file_reader_call", "📖"), "File Reader"
    
    def get_tool_details(self) -> str:
        """Get file reader specific details.
        
        Returns:
            Formatted details string showing file info and progress
        """
        if not self._tool_item:
            return ""
        
        parts = []
        
        # File name and status
        file_name = getattr(self._tool_item, "file_name", None)
        if file_name:
            parts.append(f"{ICONS['file_reader_call']}{file_name}")
        elif self._tool_item.doc_ids and len(self._tool_item.doc_ids) > 0:
            # Use first doc_id as fallback
            parts.append(f"{ICONS['file_reader_call']}{self._tool_item.doc_ids[0]}")
        
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
    def from_tool_item(cls, tool_item: Any, styles: PlaintextStyles, config: PlaintextDisplayConfig) -> "PlaintextFileReaderToolRender":
        """Factory method to create renderer from tool item.
        
        Args:
            tool_item: File reader tool item
            styles: Style manager instance
            config: Display configuration
            
        Returns:
            File reader tool renderer
        """
        return cls(styles, config).with_tool_item(tool_item) 