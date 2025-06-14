"""Base display interface for all output formats."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseDisplay(ABC):
    """Abstract base class for all display implementations."""
    
    @abstractmethod
    async def show_request_info(self, info: Dict[str, Any]) -> None:
        """
        Display request information at the start.
        
        Args:
            info: Dictionary containing request details like question, model, etc.
        """
        pass
    
    @abstractmethod
    async def update_content(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Update the main content display.
        
        Args:
            content: Formatted content to display
            metadata: Optional metadata like usage stats, event counts
        """
        pass
    
    @abstractmethod
    async def show_status(self, status: str) -> None:
        """
        Show a status message.
        
        Args:
            status: Status message to display
        """
        pass
    
    @abstractmethod
    async def show_error(self, error: str) -> None:
        """
        Show an error message.
        
        Args:
            error: Error message to display
        """
        pass
    
    @abstractmethod
    async def finalize(self, response: Dict[str, Any], state: Any) -> None:
        """
        Finalize the display with response data.
        
        Args:
            response: Final response data
            state: Final state object
        """
        pass
    
    # Chat mode methods - optional, with default implementations
    async def show_welcome(self, config: Any) -> None:
        """Show welcome message for chat mode."""
        await self.show_status("Welcome to Knowledge Forge Chat!")
    
    async def show_user_message(self, message: str) -> None:
        """Show a user message in chat mode."""
        await self.show_status(f"You: {message}")
    
    async def show_assistant_message(self, message: str) -> None:
        """Show an assistant message in chat mode."""
        await self.show_status(f"Assistant: {message}")
    
    async def prompt_for_input(self) -> Optional[str]:
        """Prompt for user input in chat mode."""
        # Default implementation using standard input
        try:
            return input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            return None