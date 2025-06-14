"""Configuration and constants for the refactored file search module."""

from dataclasses import dataclass, field
from typing import List, Optional
import os


# Default vectorstore IDs to use if none are provided
DEFAULT_VEC_IDS = [
    "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
]


@dataclass
class SearchConfig:
    """Central configuration for search operations."""

    # Model settings
    model: str = "qwen-max-latest"
    effort: str = "low"
    temperature: float = 0.7
    max_output_tokens: int = 1000

    # Search settings
    max_results: int = 10
    vec_ids: List[str] = field(default_factory=lambda: DEFAULT_VEC_IDS.copy())

    # Tool settings
    enabled_tools: List[str] = field(default_factory=list)

    # Server settings
    server_url: str = field(default_factory=lambda: os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999"))

    # Display settings
    debug: bool = False
    json_output: bool = False
    quiet: bool = False
    use_rich: bool = True
    throttle_ms: int = 0

    # Chat mode
    chat_mode: bool = False
    show_reasoning: bool = True  # Whether to show reasoning/thinking in output

    # Web search location
    web_country: Optional[str] = None
    web_city: Optional[str] = None

    @classmethod
    def from_args(cls, args) -> "SearchConfig":
        """Create config from command line arguments."""
        config = cls()

        # Model settings
        if hasattr(args, "model"):
            config.model = args.model
        if hasattr(args, "effort"):
            config.effort = args.effort

        # Search settings
        if hasattr(args, "max_results"):
            config.max_results = args.max_results
        if hasattr(args, "vec_id") and args.vec_id:
            config.vec_ids = args.vec_id

        # Tool settings
        if hasattr(args, "tool") and args.tool:
            config.enabled_tools = args.tool

        # Server settings
        if hasattr(args, "server"):
            config.server_url = args.server

        # Display settings
        if hasattr(args, "debug"):
            config.debug = args.debug
        if hasattr(args, "json"):
            config.json_output = args.json
        if hasattr(args, "quiet"):
            config.quiet = args.quiet
        if hasattr(args, "no_color"):
            config.use_rich = not args.no_color
        if hasattr(args, "throttle"):
            config.throttle_ms = args.throttle
        if hasattr(args, "chat"):
            config.chat_mode = args.chat

        # Web search location
        if hasattr(args, "country"):
            config.web_country = args.country
        if hasattr(args, "city"):
            config.web_city = args.city

        return config

    def get_web_location(self) -> Optional[dict]:
        """Get web location configuration if set."""
        if self.web_country or self.web_city:
            location = {}
            if self.web_country:
                location["country"] = self.web_country
            if self.web_city:
                location["city"] = self.web_city
            return location
        return None
