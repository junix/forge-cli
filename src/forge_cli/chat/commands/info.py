"""Information and inspection commands for chat mode."""

from typing import TYPE_CHECKING

from .base import ChatCommand

if TYPE_CHECKING:
    from ..controller import ChatController


class InspectCommand(ChatCommand):
    """Displays comprehensive session state information.

    Shows token usage, conversation metrics, vector store info, file usage, and model configuration.
    """

    name = "inspect"
    description = "Display comprehensive session state information"
    aliases = ["i", "status", "info"]

    async def execute(self, args: str, controller: "ChatController") -> bool:
        """Executes the inspect command.

        Args:
            args: Command arguments (not used by this command).
            controller: The `ChatController` instance.

        Returns:
            True, indicating the chat session should continue.
        """
        from rich.align import Align
        from rich.panel import Panel
        from rich.table import Table

        # Create main table for session information
        table = Table(title="📊 Session State Information", show_header=False, box=None)
        table.add_column("Category", style="bold cyan", width=20)
        table.add_column("Details", style="white")

        # 1. Token Usage Statistics
        usage = controller.conversation.get_token_usage()
        if usage:
            token_info = f"Input: {usage.input_tokens:,} tokens, Output: {usage.output_tokens:,} tokens, Total: {usage.total_tokens:,} tokens"
        else:
            token_info = "No token usage data available"
        table.add_row("🔢 Token Usage", token_info)

        # 2. Conversation Metrics
        turn_info = f"Turn: {controller.conversation.turn_count}"
        table.add_row("💬 Conversation", turn_info)

        # 3. Vector Store Information
        try:
            vector_store_info = await self._get_vector_store_info(controller)
        except Exception as e:
            vector_store_info = f"Error retrieving vector store info: {str(e)[:50]}..."
        table.add_row("🗂️ Vector Store", vector_store_info)

        # 4. Model Configuration
        model_info = f"Model: {controller.conversation.model}"
        table.add_row("🤖 Model", model_info)

        # 5. File Usage Tracking
        accessed_files = controller.conversation.get_accessed_files()
        if accessed_files:
            file_info = "\n".join([f"• {file}" for file in accessed_files])
        else:
            file_info = "No files accessed in this session"
        table.add_row("📁 Files Accessed", file_info)

        # Display the table in a panel
        panel = Panel(
            Align.center(table),
            title="Session Inspector",
            border_style="blue",
            padding=(1, 2),
        )

        # Use the display's renderer console if available, otherwise fallback to show_status
        if hasattr(controller.display, "_renderer") and hasattr(controller.display._renderer, "_console"):
            controller.display._renderer._console.print(panel)
        else:
            # Fallback: convert to string and use show_status
            controller.display.show_status("📊 Session State Information")
            controller.display.show_status(f"🔢 Token Usage: {token_info}")
            controller.display.show_status(f"💬 Turn: {turn_info}")
            # Handle multiline vector store info for fallback display
            vs_lines = vector_store_info.split("\n")
            if len(vs_lines) == 1:
                controller.display.show_status(f"🗂️ Vector Store: {vector_store_info}")
            else:
                controller.display.show_status("🗂️ Vector Store:")
                for line in vs_lines:
                    controller.display.show_status(f"  {line}")
            controller.display.show_status(f"🤖 Model: {model_info}")
            if accessed_files:
                controller.display.show_status(
                    f"📁 Files: {', '.join(accessed_files[:3])}{'...' if len(accessed_files) > 3 else ''}"
                )
            else:
                controller.display.show_status("📁 Files: No files accessed")

        return True

    async def _get_vector_store_info(self, controller: "ChatController") -> str:
        """Get vector store information from configuration and API.

        Args:
            controller: The ChatController instance.

        Returns:
            Formatted string with vector store information.
        """
        vec_ids = controller.config.vec_ids
        if not vec_ids:
            return "None"

        # Try to get vector store details from API, but handle errors gracefully
        vector_stores = []
        for vec_id in vec_ids:
            try:
                from ...sdk.vectorstore import async_get_vectorstore

                vs = await async_get_vectorstore(vec_id)
                if vs and hasattr(vs, "name") and vs.name:
                    vector_stores.append(f"{vec_id} - {vs.name}")
                else:
                    vector_stores.append(f"{vec_id} - Unnamed")
            except Exception as e:
                # Handle different types of errors with more specific messages
                error_msg = str(e)
                if "validation errors" in error_msg.lower():
                    vector_stores.append(f"{vec_id} - (Schema mismatch)")
                elif "method not allowed" in error_msg.lower():
                    vector_stores.append(f"{vec_id} - (API not supported)")
                elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                    vector_stores.append(f"{vec_id} - (Connection error)")
                else:
                    vector_stores.append(f"{vec_id} - (API error)")

        return "\n".join([f"• {vs}" for vs in vector_stores])