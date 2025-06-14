"""JSON Chat display implementation with Rich live preview."""

import json
from typing import Any, Optional, Dict
import asyncio
from datetime import datetime

try:
    from rich.console import Console
    from rich.json import JSON
    from rich.live import Live
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from .base import BaseDisplay


class JsonChatDisplay(BaseDisplay):
    """JSON Chat display with Rich Live preview for interactive use."""

    def __init__(self, console=None):
        self.console = console or (Console() if RICH_AVAILABLE else None)
        self.current_data = {
            "session": {
                "id": f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat()
            },
            "messages": []
        }
        self.live = None
        self._json_view = None
        self._in_chat_mode = False

    def _render_json(self):
        """Render the current JSON state."""
        if not RICH_AVAILABLE:
            return None
        
        return JSON.from_data(self.current_data)
        
    async def show_welcome(self, config: Any) -> None:
        """Show welcome message in JSON format."""
        self.current_data["config"] = {
            "model": config.model,
            "tools": config.enabled_tools
        }
        
        if RICH_AVAILABLE and self.console:
            self.live = Live(self._render_json(), console=self.console, auto_refresh=False)
            self.live.start()
            self.live.update(self._render_json())
            self.live.refresh()
        else:
            print(json.dumps(self.current_data, indent=2))

    async def show_user_message(self, content: str) -> None:
        """Show user message in JSON format."""
        message_obj = {
            "role": "user",
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.current_data["messages"].append(message_obj)
        
        if self.live:
            self.live.update(self._render_json())
            self.live.refresh()

    async def show_request_info(self, info: Dict[str, Any]) -> None:
        """Store request info in the JSON structure."""
        self.current_data["request"] = info
        if self.live:
            self.live.update(self._render_json())
            self.live.refresh()

    async def update_content(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Update the assistant message content."""
        # Check if we already have an assistant message
        assistant_message = None
        for msg in reversed(self.current_data["messages"]):
            if msg["role"] == "assistant":
                assistant_message = msg
                break
                
        if not assistant_message:
            # Create a new assistant message
            assistant_message = {
                "role": "assistant",
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            self.current_data["messages"].append(assistant_message)
        else:
            # Update the existing message
            assistant_message["content"] = content
            if metadata:
                assistant_message["metadata"].update(metadata)
        
        if self.live:
            self.live.update(self._render_json())
            self.live.refresh()

    async def show_status(self, status: str) -> None:
        """Show status in the JSON structure."""
        self.current_data["status"] = status
        if self.live:
            self.live.update(self._render_json())
            self.live.refresh()

    async def show_error(self, error: str) -> None:
        """Show error in the JSON structure."""
        self.current_data["error"] = error
        if self.live:
            self.live.update(self._render_json())
            self.live.refresh()
            
    async def prompt_for_input(self) -> str:
        """Get user input for chat."""
        if self.live:
            self.live.stop()
        
        try:
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(None, input, "\nYou: ")
            user_input = await future
            
            if self.live:
                self.live.start()
                
            return user_input.strip()
        except (EOFError, KeyboardInterrupt):
            if self.live:
                self.live.start()
            return None

    async def finalize(self, response: Dict[str, Any], state: Any) -> None:
        """Finalize and close the live display."""
        if response:
            self.current_data["response"] = response
            
        if hasattr(state, "citations") and state.citations:
            self.current_data["citations"] = state.citations
            
        # Stop the live display if it's running
        if self.live:
            self.live.stop()
            
            # Final output as JSON
            self.console.print(JSON.from_data(self.current_data))
        else:
            # Fallback to plain JSON output
            print(json.dumps(self.current_data, indent=2, ensure_ascii=False))
