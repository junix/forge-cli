"""Display factory for creating appropriate display instances."""

from typing import TYPE_CHECKING

from forge_cli.config import AppConfig

if TYPE_CHECKING:
    from forge_cli.display.v3.base import Display


class DisplayFactory:
    """Factory for creating display instances based on configuration."""

    @staticmethod
    def create_display(config: AppConfig) -> "Display":
        """Create appropriate display based on configuration using v3 architecture.

        Args:
            config: AppConfig containing display preferences

        Returns:
            Display instance configured for the specified output format
        """
        # Import v3 components
        from forge_cli.display.v3.base import Display

        # Determine if we're in chat mode
        in_chat_mode = config.chat_mode
        mode = "chat" if in_chat_mode else "default"

        # Choose renderer based on configuration
        if config.json_output:
            # JSON output with Rich live updates
            from forge_cli.display.v3.renderers.json import JsonDisplayConfig, JsonRenderer

            json_config = JsonDisplayConfig(
                pretty_print=True,
                include_metadata=config.debug,
                include_usage=not config.quiet,
                show_panel=not config.quiet,  # No panel in quiet mode
                panel_title="🔍 Knowledge Forge JSON Response" if in_chat_mode else "📋 JSON Response",
                syntax_theme="monokai",
                line_numbers=not in_chat_mode and not config.quiet,  # No line numbers in chat or quiet mode
            )
            renderer = JsonRenderer(config=json_config)

        elif not config.use_rich:
            # Plain text output
            from forge_cli.display.v3.renderers.plaintext import PlaintextDisplayConfig, PlaintextRenderer

            plain_config = PlaintextDisplayConfig(
                show_reasoning=config.show_reasoning,
                show_citations=True,
                show_usage=not config.quiet,
                show_metadata=config.debug,
            )
            renderer = PlaintextRenderer(config=plain_config)

        else:
            # Rich terminal UI (default)
            from forge_cli.display.v3.renderers.rich import RichDisplayConfig, RichRenderer

            display_config = RichDisplayConfig(
                show_reasoning=config.show_reasoning,
                show_citations=True,
                show_tool_details=True,
                show_usage=not config.quiet,
                show_metadata=config.debug,
            )
            renderer = RichRenderer(config=display_config, in_chat_mode=in_chat_mode)

        # Create v3 display
        return Display(renderer, mode=mode)
