"""Display registry module for rendering implementations."""

from collections.abc import Callable
from typing import Any

from .base import BaseDisplay


class DisplayRegistry:
    """Registry for display implementations.

    This registry allows dynamic registration of display implementations,
    making it easy to add new rendering styles without modifying existing code.
    """

    _displays: dict[str, type[BaseDisplay]] = {}
    _factories: dict[str, Callable[..., BaseDisplay]] = {}
    _conditions: dict[str, Callable[[Any], bool]] = {}

    @classmethod
    def register_display(
        cls,
        name: str,
        display_cls: type[BaseDisplay],
        factory: Callable[..., BaseDisplay] = None,
        condition: Callable[[Any], bool] = None,
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
    def get_display_class(cls, name: str) -> type[BaseDisplay]:
        """Get a display class by name."""
        return cls._displays.get(name)

    @classmethod
    def get_display_classes(cls) -> dict[str, type[BaseDisplay]]:
        """Get all registered display classes."""
        return cls._displays

    @classmethod
    def create_display(cls, name: str, **kwargs) -> BaseDisplay:
        """Create a display instance by name with optional parameters."""
        if name not in cls._displays:
            raise ValueError(f"Display implementation '{name}' not found")

        if name in cls._factories:
            # Use factory if available
            return cls._factories[name](**kwargs)

        # Otherwise create instance directly
        return cls._displays[name](**kwargs)

    @classmethod
    def get_display_for_config(cls, config: Any) -> BaseDisplay:
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
    """Initialize the default display implementations."""
    from .json_display import JsonDisplay
    from .plain_display import PlainDisplay
    from .rich_display import RichDisplay
    from .json_chat_display import JsonChatDisplay

    # Register JSON display with condition
    DisplayRegistry.register_display(
        "json", 
        JsonDisplay, 
        condition=lambda config: getattr(config, "json_output", False) is True and getattr(config, "chat", False) is False
    )
    
    # Register JSON Chat display with condition
    DisplayRegistry.register_display(
        "json_chat",
        JsonChatDisplay,
        factory=lambda **kwargs: JsonChatDisplay(console=kwargs.get("console", None)),
        condition=lambda config: getattr(config, "json_output", False) is True and getattr(config, "chat", False) is True
    )

    # Register Rich display with condition and factory
    DisplayRegistry.register_display(
        "rich",
        RichDisplay,
        factory=lambda **kwargs: RichDisplay(console=kwargs.get("console", None)),
        condition=lambda config: (
            getattr(config, "use_rich", False) is True and getattr(config, "quiet", False) is False
        ),
    )

    # Register Plain display as default
    DisplayRegistry.register_display(
        "plain",
        PlainDisplay,
        condition=lambda config: True,  # Will be used as fallback
    )
