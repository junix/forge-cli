"""Factory for creating display instances with v1/v2 compatibility."""

import sys
from typing import Union

from ..config import SearchConfig
from .base import BaseDisplay  # v1 interface
from .v2.base import Display as DisplayV2  # v2 interface
from .v2.adapter import V1ToV2Adapter
from .v2.renderers.plain import PlainRenderer


def create_display(config: SearchConfig) -> Union[BaseDisplay, DisplayV2]:
    """Factory function with feature flag support.

    Args:
        config: Search configuration with display settings

    Returns:
        Either a v1 BaseDisplay or v2 Display instance based on config
    """
    if config.use_new_display_api:
        return _create_v2_display(config)
    else:
        return _create_v1_display(config)


def _create_v2_display(config: SearchConfig) -> DisplayV2:
    """Create v2 display system.

    Args:
        config: Search configuration

    Returns:
        A v2 Display instance with appropriate renderer
    """
    # Select renderer based on config
    if config.json_output:
        # TODO: Implement JsonRenderer
        renderer = PlainRenderer()  # Fallback for now
    elif not config.use_rich or not sys.stdout.isatty():
        renderer = PlainRenderer()
    else:
        try:
            # TODO: Implement RichRenderer
            renderer = PlainRenderer()  # Fallback for now
        except ImportError:
            # Fallback if rich not available
            renderer = PlainRenderer()

    if config.display_api_debug:
        print(f"[DEBUG] Using v2 display API with {renderer.__class__.__name__}", file=sys.stderr)

    return DisplayV2(renderer)


def _create_v1_display(config: SearchConfig) -> BaseDisplay:
    """Create legacy v1 display.

    Args:
        config: Search configuration

    Returns:
        A v1 BaseDisplay instance
    """
    # Import existing displays
    from .rich_display import RichDisplay
    from .plain_display import PlainDisplay
    from .json_display import JsonDisplay

    if config.json_output:
        if config.chat_mode:
            # Use JSON chat display for chat mode
            from .json_chat_display import JsonChatDisplay

            return JsonChatDisplay()
        else:
            return JsonDisplay()
    elif not config.use_rich or not sys.stdout.isatty():
        return PlainDisplay()
    else:
        try:
            return RichDisplay()
        except ImportError:
            # Fallback if rich not available
            return PlainDisplay()


def create_compatible_display(config: SearchConfig) -> BaseDisplay:
    """Create display that's compatible with v1 interface.

    This function always returns a v1-compatible BaseDisplay instance,
    using an adapter if necessary when v2 is enabled.

    Args:
        config: Search configuration

    Returns:
        A BaseDisplay instance (possibly adapted from v2)
    """
    if config.use_new_display_api:
        # Use v2 system but wrap in adapter for compatibility
        display_v2 = _create_v2_display(config)
        return V1ToV2Adapter(display_v2)
    else:
        return _create_v1_display(config)


def determine_display_api_version(config: SearchConfig) -> None:
    """Auto-determine which API version to use based on config.

    This function can be called to automatically set the use_new_display_api
    flag based on various conditions.

    Args:
        config: Search configuration to update
    """
    # Force v2 for specific scenarios during migration

    # Use v2 for plain text output (simpler implementation)
    if not config.use_rich and not config.json_output:
        config.use_new_display_api = True

    # Allow environment variable override
    import os

    if os.environ.get("FORGE_USE_V2_DISPLAY") == "1":
        config.use_new_display_api = True
    elif os.environ.get("FORGE_USE_V1_DISPLAY") == "1":
        config.use_new_display_api = False
