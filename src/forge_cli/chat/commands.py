"""Chat command system for interactive mode."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from pydantic import BaseModel

if TYPE_CHECKING:
    from .controller import ChatController


class ChatCommand(BaseModel):
    """Represents a chat command."""
    name: str
    description: str
    handler: Callable[[ChatController, list[str]], Any]
    aliases: list[str] = []
    
    model_config = {"arbitrary_types_allowed": True}


class CommandRegistry:
    """Registry for chat commands."""
    
    def __init__(self):
        self.commands: dict[str, ChatCommand] = {}
        self.aliases: dict[str, str] = {}
        self._register_default_commands()
    
    def register(self, command: ChatCommand) -> None:
        """Register a command."""
        self.commands[command.name] = command
        for alias in command.aliases:
            self.aliases[alias] = command.name
    
    def get(self, name: str) -> ChatCommand | None:
        """Get a command by name or alias."""
        if name in self.commands:
            return self.commands[name]
        if name in self.aliases:
            return self.commands[self.aliases[name]]
        return None
    
    def _register_default_commands(self) -> None:
        """Register default chat commands."""
        # Help command
        self.register(ChatCommand(
            name="help",
            description="Show available commands",
            handler=self._cmd_help,
            aliases=["h", "?"]
        ))
        
        # Save/Load commands
        self.register(ChatCommand(
            name="save",
            description="Save conversation to file",
            handler=self._cmd_save,
            aliases=["s"]
        ))
        
        self.register(ChatCommand(
            name="load",
            description="Load conversation from file",
            handler=self._cmd_load,
            aliases=["l"]
        ))
        
        # Clear command
        self.register(ChatCommand(
            name="clear",
            description="Clear conversation history",
            handler=self._cmd_clear,
            aliases=["c", "new"]
        ))
        
        # Model command
        self.register(ChatCommand(
            name="model",
            description="Change or show AI model",
            handler=self._cmd_model,
            aliases=["m"]
        ))
        
        # Tool commands
        self.register(ChatCommand(
            name="tools",
            description="Show enabled tools",
            handler=self._cmd_tools,
            aliases=["t"]
        ))
        
        self.register(ChatCommand(
            name="enable-web-search",
            description="Enable web search tool",
            handler=self._cmd_enable_web_search,
            aliases=["web-on"]
        ))
        
        self.register(ChatCommand(
            name="disable-web-search",
            description="Disable web search tool",
            handler=self._cmd_disable_web_search,
            aliases=["web-off"]
        ))
        
        self.register(ChatCommand(
            name="enable-file-search",
            description="Enable file search tool",
            handler=self._cmd_enable_file_search,
            aliases=["file-on"]
        ))
        
        self.register(ChatCommand(
            name="disable-file-search",
            description="Disable file search tool",
            handler=self._cmd_disable_file_search,
            aliases=["file-off"]
        ))
        
        self.register(ChatCommand(
            name="enable-page-reader",
            description="Enable page reader tool",
            handler=self._cmd_enable_page_reader,
            aliases=["page-on"]
        ))
        
        self.register(ChatCommand(
            name="disable-page-reader",
            description="Disable page reader tool",
            handler=self._cmd_disable_page_reader,
            aliases=["page-off"]
        ))
        
        # File management commands
        self.register(ChatCommand(
            name="refresh-files",
            description="Refresh file cache for @ completion",
            handler=self._cmd_refresh_files,
            aliases=["rf", "refresh"]
        ))
        
        # Config command
        self.register(ChatCommand(
            name="config",
            description="Show current configuration",
            handler=self._cmd_config,
            aliases=["cfg"]
        ))
        
        # Info command
        self.register(ChatCommand(
            name="info",
            description="Show session information",
            handler=self._cmd_info,
            aliases=["i"]
        ))
        
        # Exit command
        self.register(ChatCommand(
            name="exit",
            description="Exit chat mode",
            handler=self._cmd_exit,
            aliases=["quit", "q"]
        ))
    
    # Command handlers
    async def _cmd_help(self, controller: ChatController, args: list[str]) -> None:
        """Show help message."""
        print("\n📚 Available Commands:")
        print("=" * 60)
        
        # Group commands by category
        categories = {
            "Session": ["save", "load", "clear", "exit"],
            "Configuration": ["model", "tools", "config"],
            "Tools": ["enable-web-search", "disable-web-search", "enable-file-search", 
                     "disable-file-search", "enable-page-reader", "disable-page-reader"],
            "Files": ["refresh-files"],
            "Information": ["help", "info"]
        }
        
        for category, cmd_names in categories.items():
            print(f"\n{category}:")
            for cmd_name in cmd_names:
                if cmd_name in self.commands:
                    cmd = self.commands[cmd_name]
                    aliases = f" ({', '.join(cmd.aliases)})" if cmd.aliases else ""
                    print(f"  /{cmd.name}{aliases} - {cmd.description}")
    
    async def _cmd_save(self, controller: ChatController, args: list[str]) -> None:
        """Save conversation."""
        filename = args[0] if args else f"chat_{controller.conversation.conversation_id}.json"
        if not filename.endswith('.json'):
            filename += '.json'
        
        path = Path(filename)
        controller.conversation.save(path)
        print(f"✅ Conversation saved to: {path}")
    
    async def _cmd_load(self, controller: ChatController, args: list[str]) -> None:
        """Load conversation."""
        if not args:
            print("❌ Please specify a filename to load")
            return
        
        filename = args[0]
        if not filename.endswith('.json'):
            filename += '.json'
        
        path = Path(filename)
        if not path.exists():
            print(f"❌ File not found: {path}")
            return
        
        try:
            controller.conversation = controller.conversation.load(path)
            print(f"✅ Conversation loaded from: {path}")
        except Exception as e:
            print(f"❌ Failed to load conversation: {e}")
    
    async def _cmd_clear(self, controller: ChatController, args: list[str]) -> None:
        """Clear conversation history."""
        controller.conversation.clear()
        print("✅ Conversation history cleared")
    
    async def _cmd_model(self, controller: ChatController, args: list[str]) -> None:
        """Change or show model."""
        if args:
            new_model = args[0]
            controller.conversation.model = new_model
            print(f"✅ Model changed to: {new_model}")
        else:
            print(f"Current model: {controller.conversation.model}")
    
    async def _cmd_tools(self, controller: ChatController, args: list[str]) -> None:
        """Show enabled tools."""
        print("\n🔧 Tool Status:")
        print(f"  Web Search: {'✅ Enabled' if controller.conversation.web_search_enabled else '❌ Disabled'}")
        print(f"  File Search: {'✅ Enabled' if controller.conversation.file_search_enabled else '❌ Disabled'}")
        print(f"  Page Reader: {'✅ Enabled' if controller.conversation.page_reader_enabled else '❌ Disabled'}")
        
        if controller.conversation.current_vector_store_ids:
            print(f"\n📁 Vector Stores: {', '.join(controller.conversation.current_vector_store_ids)}")
    
    async def _cmd_enable_web_search(self, controller: ChatController, args: list[str]) -> None:
        """Enable web search."""
        controller.conversation.enable_web_search()
        print("✅ Web search enabled")
    
    async def _cmd_disable_web_search(self, controller: ChatController, args: list[str]) -> None:
        """Disable web search."""
        controller.conversation.disable_web_search()
        print("✅ Web search disabled")
    
    async def _cmd_enable_file_search(self, controller: ChatController, args: list[str]) -> None:
        """Enable file search."""
        controller.conversation.enable_file_search()
        print("✅ File search enabled")
    
    async def _cmd_disable_file_search(self, controller: ChatController, args: list[str]) -> None:
        """Disable file search."""
        controller.conversation.disable_file_search()
        print("✅ File search disabled")
    
    async def _cmd_enable_page_reader(self, controller: ChatController, args: list[str]) -> None:
        """Enable page reader."""
        controller.conversation.enable_tool("page-reader")
        print("✅ Page reader enabled")
    
    async def _cmd_disable_page_reader(self, controller: ChatController, args: list[str]) -> None:
        """Disable page reader."""
        controller.conversation.disable_tool("page-reader")
        print("✅ Page reader disabled")
    
    async def _cmd_refresh_files(self, controller: ChatController, args: list[str]) -> None:
        """Refresh file cache for @ completion."""
        # Access the completer through the controller
        if hasattr(controller, '_completer') and controller._completer:
            controller._completer.refresh_file_cache()
            print("✅ File cache refreshed. @ completion will show updated files.")
        else:
            print("ℹ️  File cache will be refreshed on next @ completion.")
    
    async def _cmd_config(self, controller: ChatController, args: list[str]) -> None:
        """Show configuration."""
        print("\n⚙️  Current Configuration:")
        print("=" * 60)
        print(f"Model: {controller.conversation.model}")
        print(f"Temperature: {controller.conversation.temperature}")
        print(f"Max Output Tokens: {controller.conversation.max_output_tokens}")
        print(f"Effort: {controller.conversation.effort}")
        print(f"Server URL: {controller.conversation.server_url}")
    
    async def _cmd_info(self, controller: ChatController, args: list[str]) -> None:
        """Show session information."""
        print("\n📊 Session Information:")
        print("=" * 60)
        print(f"Conversation ID: {controller.conversation.conversation_id}")
        print(f"Message Count: {controller.conversation.get_message_count()}")
        print(f"Turn Count: {controller.conversation.turn_count}")
        
        if controller.conversation.usage:
            print(f"\nToken Usage:")
            print(f"  Total: {controller.conversation.usage.total_tokens}")
            print(f"  Input: {controller.conversation.usage.input_tokens}")
            print(f"  Output: {controller.conversation.usage.output_tokens}")
    
    async def _cmd_exit(self, controller: ChatController, args: list[str]) -> None:
        """Exit chat mode."""
        print("\n👋 Goodbye!")
        controller.running = False