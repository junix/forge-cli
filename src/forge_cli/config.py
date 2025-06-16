"""Configuration and constants for the refactored file search module."""

import os
from dataclasses import dataclass, field

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
    vec_ids: list[str] = field(default_factory=lambda: DEFAULT_VEC_IDS.copy())

    # Tool settings
    enabled_tools: list[str] = field(default_factory=list)

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

    # Question/query
    question: str = "What information can you find in the documents?"

    # Web search location
    web_country: str | None = None
    web_city: str | None = None

    # Display settings (migrated to v3)
    display_api_debug: bool = False  # Debug logging for display API

    @classmethod
    def from_args(cls, args) -> "SearchConfig":
        """Create config from command line arguments using type-safe attribute access."""
        config = cls()

        # Model settings - use direct attribute access since args is typed
        config.model = getattr(args, "model", config.model)
        config.effort = getattr(args, "effort", config.effort)

        # Question/query
        config.question = getattr(args, "question", config.question)

        # Search settings
        config.max_results = getattr(args, "max_results", config.max_results)
        if getattr(args, "vec_id", None):
            config.vec_ids = args.vec_id

        # Tool settings
        if getattr(args, "tool", None):
            config.enabled_tools = args.tool

        # Server settings
        config.server_url = getattr(args, "server", config.server_url)

        # Display settings
        config.debug = getattr(args, "debug", config.debug)
        config.json_output = getattr(args, "json", config.json_output)
        config.quiet = getattr(args, "quiet", config.quiet)
        config.use_rich = not getattr(args, "no_color", False)
        config.throttle_ms = getattr(args, "throttle", config.throttle_ms)
        config.chat_mode = getattr(args, "chat", config.chat_mode)

        # Web search location
        config.web_country = getattr(args, "country", config.web_country)
        config.web_city = getattr(args, "city", config.web_city)

        return config

    def apply_dataset_config(self, dataset, args) -> None:
        """Apply dataset configuration with proper tool enablement logic.

        Args:
            dataset: TestDataset instance or None
            args: Parsed command line arguments
        """
        # Use vectorstore ID from dataset if no command line vec_ids provided
        if dataset and dataset.vectorstore_id and not getattr(args, "vec_id", None):
            self.vec_ids = [dataset.vectorstore_id]
            # Enable file-search tool when using dataset
            if "file-search" not in self.enabled_tools:
                self.enabled_tools.append("file-search")

        # Use default vector IDs if none provided
        if not self.vec_ids:
            self.vec_ids = SearchConfig().vec_ids

        # Default to file-search if vec_ids provided but no tools specified
        if not self.enabled_tools and self.vec_ids:
            self.enabled_tools = ["file-search"]

    def get_web_location(self) -> dict | None:
        """Get web location configuration if set."""
        if self.web_country or self.web_city:
            location = {}
            if self.web_country:
                location["country"] = self.web_country
            if self.web_city:
                location["city"] = self.web_city
            return location
        return None
