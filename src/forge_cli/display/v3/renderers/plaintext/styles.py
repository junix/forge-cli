"""Centralized style management for plaintext renderer."""

from ...style import ICONS, STATUS_ICONS


class PlaintextStyles:
    """Centralized style management for plaintext renderer."""
    
    def __init__(self):
        """Initialize style definitions."""
        self._styles = {
            "header": "bold cyan",
            "status_completed": "bold green",
            "status_failed": "bold red",
            "status_in_progress": "bold yellow",
            "status_default": "bold blue",
            "model": "green",
            "id": "dim white",
            "separator": "dim blue",
            "content": "white",  # 正式文本用白色
            "tool_icon": "yellow",
            "tool_name": "bold magenta",  # 工具名称用洋红色，更活泼
            "tool_status_completed": "bold green",
            "tool_status_in_progress": "bold yellow",
            "tool_status_failed": "bold red",
            "tool_details": "cyan",  # 工具细节用青色
            "reasoning": "italic dark_green",  # 推理文本用暗绿色斜体
            "reasoning_header": "bold dark_green",
            "citation_ref": "bold cyan",
            "citation_source": "blue",
            "citation_text": "dim",
            "usage": "green",
            "usage_label": "cyan",
            "error": "bold red",
            "warning": "bold orange3",
            "info": "cyan",
            "success": "green",
        }
    
    def get_style(self, name: str) -> str:
        """Get style by name.
        
        Args:
            name: Style name
            
        Returns:
            Style definition
        """
        return self._styles.get(name, "white")
    
    def get_status_style(self, status: str) -> str:
        """Get style for status text.
        
        Args:
            status: Status string
            
        Returns:
            Style definition for the status
        """
        return {
            "completed": self._styles["status_completed"],
            "failed": self._styles["status_failed"],
            "in_progress": self._styles["status_in_progress"],
            "incomplete": self._styles["warning"],
        }.get(status, self._styles["status_default"])
    
    def get_status_icon_and_style(self, status: str) -> tuple[str, str]:
        """Get icon and style for status.
        
        Args:
            status: Status string
            
        Returns:
            Tuple of (icon, style)
        """
        return {
            "completed": ("  ", self._styles["status_completed"]),
            "in_progress": (" 󰜎 ", self._styles["status_in_progress"]),
            "failed": ("  ", self._styles["status_failed"]),
            "incomplete": ("  ", self._styles["status_default"]),
        }.get(status, ("  ", "white"))
    
    def get_tool_status_style(self, status: str) -> str:
        """Get style for tool status.
        
        Args:
            status: Tool status string
            
        Returns:
            Style definition for the tool status
        """
        return {
            "completed": self._styles["tool_status_completed"],
            "in_progress": self._styles["tool_status_in_progress"],
            "searching": self._styles["tool_status_in_progress"],
            "interpreting": self._styles["tool_status_in_progress"],
            "failed": self._styles["tool_status_failed"],
        }.get(status, "white")
    
    def get_tool_icon(self, tool_type: str) -> str:
        """Get icon for tool type.
        
        Args:
            tool_type: Tool type string
            
        Returns:
            Icon for the tool type
        """
        return ICONS.get(tool_type, ICONS["processing"])
    
    def get_status_icon(self, status: str) -> str:
        """Get icon for status.
        
        Args:
            status: Status string
            
        Returns:
            Icon for the status
        """
        return STATUS_ICONS.get(status, STATUS_ICONS["default"]) 