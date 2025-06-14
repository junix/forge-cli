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
    """Initialize the default display implementations using v2 renderers by default."""
    # Import v2 components
    from .v2.adapter import V1ToV2Adapter
    from .v2.base import Display as DisplayV2
    from .v2.renderers.json import JsonRenderer
    from .v2.renderers.plain import PlainRenderer
    from .v2.renderers.rich import RichRenderer

    # Import v1 displays for fallback
    from .json_chat_display import JsonChatDisplay
    from .json_display import JsonDisplay
    from .plain_display import PlainDisplay
    from .rich_display import RichDisplay

    # Helper function to create v2 display wrapped in v1 adapter
    def create_v2_json_display(**kwargs):
        renderer = JsonRenderer(
            include_events=kwargs.get("config", {}).debug if hasattr(kwargs.get("config", {}), "debug") else False,
            pretty=True
        )
        display_v2 = DisplayV2(renderer)
        return V1ToV2Adapter(display_v2)

    def create_v2_rich_display(**kwargs):
        config = kwargs.get("config", {})
        try:
            renderer = RichRenderer(
                show_reasoning=config.show_reasoning if hasattr(config, "show_reasoning") else True
            )
            display_v2 = DisplayV2(renderer)
            return V1ToV2Adapter(display_v2)
        except ImportError:
            # Fallback to plain if rich not available
            renderer = PlainRenderer()
            display_v2 = DisplayV2(renderer)
            return V1ToV2Adapter(display_v2)

    def create_v2_plain_display(**kwargs):
        renderer = PlainRenderer()
        display_v2 = DisplayV2(renderer)
        return V1ToV2Adapter(display_v2)

    # Register JSON display using v2
    DisplayRegistry.register_display(
        "json",
        V1ToV2Adapter,  # The class type for registry
        factory=create_v2_json_display,
        condition=lambda config: getattr(config, "json_output", False) is True
        and getattr(config, "chat", False) is False,
    )

    # Register JSON Chat display - still using v1 for now (complex chat integration)
    DisplayRegistry.register_display(
        "json_chat",
        JsonChatDisplay,
        factory=lambda **kwargs: JsonChatDisplay(console=kwargs.get("console", None)),
        condition=lambda config: getattr(config, "json_output", False) is True
        and getattr(config, "chat", False) is True,
    )

    # Register Rich display using v2
    DisplayRegistry.register_display(
        "rich",
        V1ToV2Adapter,  # The class type for registry
        factory=create_v2_rich_display,
        condition=lambda config: (
            getattr(config, "use_rich", False) is True and getattr(config, "quiet", False) is False
        ),
    )

    # Register Plain display as default using v2
    DisplayRegistry.register_display(
        "plain",
        V1ToV2Adapter,  # The class type for registry
        factory=create_v2_plain_display,
        condition=lambda config: True,  # Will be used as fallback
    )
