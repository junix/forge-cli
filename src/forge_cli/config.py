"""Configuration and constants for the refactored file search module."""

import os
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

# Default vectorstore IDs to use if none are provided
DEFAULT_VEC_IDS = [
    "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
]

# Valid effort levels
EffortLevel = Literal["low", "medium", "high"]

# Valid tool types
ToolType = Literal[
    "file-search", "web-search", "code-analyzer", "function", "computer", "list-documents", "file-reader"
]


class AppConfig(BaseModel):
    """Central configuration for the forge-cli application."""

    # Model settings
    model: str = "qwen-max-latest"
    effort: EffortLevel = "low"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_output_tokens: int = Field(default=1000, gt=0)

    # Search settings
    max_results: int = Field(default=10, gt=0)
    vec_ids: list[str] = Field(default_factory=lambda: DEFAULT_VEC_IDS.copy(), alias="vec_id")

    # Tool settings
    enabled_tools: list[ToolType] = Field(default_factory=list, alias="tool")

    # Server settings
    server_url: str = Field(
        default_factory=lambda: os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999"), alias="server"
    )

    # Display settings
    debug: bool = False
    json_output: bool = Field(default=False, alias="json")
    quiet: bool = False
    use_rich: bool = Field(default=True, alias="no_color")
    throttle_ms: int = Field(default=0, ge=0, alias="throttle")

    # Chat mode
    chat_mode: bool = Field(default=False, alias="chat")
    show_reasoning: bool = True  # Whether to show reasoning/thinking in output

    # Question/query
    question: str = "What information can you find in the documents?"

    # Web search location
    web_country: str | None = Field(default=None, alias="country")
    web_city: str | None = Field(default=None, alias="city")

    # Display settings (migrated to v3)
    display_api_debug: bool = False  # Debug logging for display API

    @field_validator("vec_ids")
    @classmethod
    def validate_vec_ids(cls, v: list[str]) -> list[str]:
        """Validate vector store IDs format."""
        for vec_id in v:
            if not vec_id or not isinstance(vec_id, str):
                raise ValueError(f"Invalid vector store ID: {vec_id}")
        return v

    @field_validator("server_url")
    @classmethod
    def validate_server_url(cls, v: str) -> str:
        """Validate server URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("Server URL must start with http:// or https://")
        return v.rstrip("/")

    @model_validator(mode="after")
    def validate_config_consistency(self) -> "AppConfig":
        """Validate configuration consistency."""
        # If file search tools are enabled, ensure vec_ids are provided
        if any(tool in ["file-search", "list-documents"] for tool in self.enabled_tools):
            if not self.vec_ids:
                raise ValueError("Vector store IDs required when file search tools are enabled")

        return self

    @classmethod
    def from_args(cls, args) -> "AppConfig":
        """Create config from command line arguments using Pydantic validation."""
        # Convert args namespace to dict and filter out None values
        args_dict = {k: v for k, v in vars(args).items() if v is not None}

        # Special handling for no_color -> use_rich inversion
        if "no_color" in args_dict:
            args_dict["no_color"] = not args_dict["no_color"]

        # Create config with validation - Pydantic handles aliases automatically
        return cls.model_validate(args_dict)

    def apply_dataset_config(self, dataset, args) -> "AppConfig":
        """Apply dataset configuration with proper tool enablement logic.

        Args:
            dataset: TestDataset instance or None
            args: Parsed command line arguments

        Returns:
            New AppConfig instance with dataset configuration applied
        """
        updates = {}

        # Use vectorstore ID from dataset if no command line vec_ids provided
        if dataset and dataset.vectorstore_id and not getattr(args, "vec_id", None):
            updates["vec_ids"] = [dataset.vectorstore_id]
            # Enable file-search tool when using dataset
            if "file-search" not in self.enabled_tools:
                updates["enabled_tools"] = self.enabled_tools + ["file-search"]

        # Use default vector IDs if none provided
        if not self.vec_ids and "vec_ids" not in updates:
            updates["vec_ids"] = DEFAULT_VEC_IDS.copy()

        # Default to file-search if vec_ids provided but no tools specified
        vec_ids_to_check = updates.get("vec_ids", self.vec_ids)
        tools_to_check = updates.get("enabled_tools", self.enabled_tools)
        if not tools_to_check and vec_ids_to_check:
            updates["enabled_tools"] = ["file-search"]

        # Return new instance with updates if any, otherwise return self
        if updates:
            return self.model_copy(update=updates)
        return self

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
