#!/usr/bin/env python3
import json

from rich.align import Align
from rich.box import SIMPLE
from rich.live import Live
from rich.panel import Panel
from rich.syntax import Syntax


class JsonLive:
    def __init__(self, console, refresh_per_second=4):
        """Initialize a live JSON display.

        Args:
            console (Console): The rich console to display on
            refresh_per_second (int): How often to refresh the display
        """
        self.console = console
        self.live = Live(
            "",
            console=console,
            refresh_per_second=refresh_per_second,
            auto_refresh=False,
        )
        self.is_started = False
        self.last_content = None
        self.last_title = None
        self.last_subtitle = None

    def update(
        self,
        content: str | dict,
        *,
        title: str | None = None,
        subtitle: str | None = None,
        panel_style: str | None = None,
    ):
        # Store the latest non-None data
        if content is not None:
            self.last_content = content
        if title is not None:
            self.last_title = title
        if subtitle is not None:
            self.last_subtitle = subtitle
        """Update the live display with new JSON content.

        Args:
            content: JSON string or Python dictionary to display
            title: Optional title for the panel
            subtitle: Optional subtitle for the panel
            panel_style: Optional panel border style (e.g. 'blue', 'red', 'green')
        """
        # Start the live display if not already started
        if not self.is_started:
            self.live.start()
            self.is_started = True

        if content is None:
            content = self.last_content
        if title is None:
            title = self.last_title
        if subtitle is None:
            subtitle = self.last_subtitle

        # Convert content to a JSON string if it's a dictionary
        if isinstance(content, dict):
            json_str = json.dumps(content, ensure_ascii=False, indent=2)
        elif isinstance(content, str):
            # Assume it's already a JSON string
            json_str = content
        else:
            # If it's neither a dict nor string, it's an error
            raise TypeError("Content must be a string or dictionary")

        # Create a syntax object with JSON formatting
        json_syntax = Syntax(json_str, "json", theme="monokai", word_wrap=True, padding=(1, 2))

        # Create a panel with the JSON content and optional parameters
        json_panel = Panel(
            json_syntax,
            width=150,
            border_style="green",
            box=SIMPLE,
            title=title,
            subtitle=subtitle,
            subtitle_align="right" if subtitle else None,
        )

        # Update the display with centered panel
        self.live.update(Align.center(json_panel))

        # Force a refresh
        self.live.refresh()

    def done(self):
        """Stop the live display."""
        if self.is_started:
            self.live.stop()
            self.is_started = False
