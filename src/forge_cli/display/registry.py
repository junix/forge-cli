"""Display registry module for rendering implementations."""

from collections.abc import Callable

from .v3.base import Display


class DisplayRegistry:
    """Registry for display implementations.

    This registry allows dynamic registration of display implementations,
    making it easy to add new rendering styles without modifying existing code.
    """

    _displays: dict[str, type[Display]] = {}
    _factories: dict[str, Callable[..., Display]] = {}
    _conditions: dict[str, Callable[[object], bool]] = {}

    @classmethod
    def register_display(
        cls,
        name: str,
        display_cls: type[Display],
        factory: Callable[..., Display] = None,
        condition: Callable[[object], bool] = None,
    ):
        """Register a display implementation.

        Args:
            name: Unique name for the display implementation
            display_cls: The display class implementation
            factory: Optional factory function for creating display instances
            condition: Optional condition function that determines if this display should be used
        """
        cls._displays[name] = display_cls
        if factory:
            cls._factories[name] = factory
        if condition:
            cls._conditions[name] = condition

    @classmethod
    def get_display_class(cls, name: str) -> type[Display]:
        """Get a display class by name."""
        return cls._displays.get(name)

    @classmethod
    def get_display_classes(cls) -> dict[str, type[Display]]:
        """Get all registered display classes."""
        return cls._displays

    @classmethod
    def create_display(cls, name: str, **kwargs) -> Display:
        """Create a display instance by name with optional parameters."""
        if name not in cls._displays:
            raise ValueError(f"Display implementation '{name}' not found")

        if name in cls._factories:
            # Use factory if available
            return cls._factories[name](**kwargs)

        # Otherwise create instance directly
        return cls._displays[name](**kwargs)

    @classmethod
    def get_display_for_config(cls, config: object) -> Display:
        """Get the appropriate display for the given configuration.

        Evaluates registered conditions and returns the first matching display.
        """
        for name, condition in cls._conditions.items():
            if condition(config):
                return cls.create_display(name, config=config)

        # Default to the first registered display or none
        if cls._displays:
            default_name = next(iter(cls._displays))
            return cls.create_display(default_name, config=config)

        raise ValueError("No display implementations registered")


def initialize_default_displays():
    """Initialize the default display implementations using v3."""
    # Import v3 components
    from .v3.base import Display
    from .v3.renderers.json import JsonRenderer
    from .v3.renderers.plaintext import PlaintextRenderer
    from .v3.renderers.rich import RichRenderer

    # Helper function to create v3 displays
    def create_json_display(**kwargs):
        config = kwargs.get("config", {})
        chat_active = getattr(config, "chat_mode", False) or getattr(config, "chat", False)
        renderer = JsonRenderer(
            include_events=getattr(config, "debug", False),
            pretty=True,
            in_chat_mode=chat_active,
        )
        mode = "chat" if chat_active else "default"
        return Display(renderer, mode=mode)

    def create_rich_display(**kwargs):
        config = kwargs.get("config", {})
        try:
            renderer = RichRenderer(show_reasoning=getattr(config, "show_reasoning", True))
            mode = "chat" if getattr(config, "chat_mode", False) or getattr(config, "chat", False) else "default"
            return Display(renderer, mode=mode)
        except ImportError:
            # Fallback to plain if rich not available
            renderer = PlaintextRenderer()
            return Display(renderer)

    def create_plain_display(**_kwargs):
        # Plain display doesn't need configuration
        renderer = PlaintextRenderer()
        return Display(renderer)

    # Register JSON display
    DisplayRegistry.register_display(
        "json",
        Display,
        factory=create_json_display,
        condition=lambda config: getattr(config, "render_format", "rich") == "json",
    )

    # Register Rich display
    DisplayRegistry.register_display(
        "rich",
        Display,
        factory=create_rich_display,
        condition=lambda config: (
            getattr(config, "render_format", "rich") == "rich" and getattr(config, "quiet", False) is False
        ),
    )

    # Register Plain display as default
    DisplayRegistry.register_display(
        "plain",
        Display,
        factory=create_plain_display,
        condition=lambda _config: True,  # Will be used as fallback
    )
