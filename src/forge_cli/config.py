from __future__ import annotations

"""Configuration and constants for the refactored file search module."""

import os
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

# Default vectorstore IDs to use if none are provided
DEFAULT_VEC_IDS = [
    "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
]

# Valid effort levels
EffortLevel = Literal["low", "medium", "high", "dev"]

# Valid tool types
ToolType = Literal[
    "file-search", "web-search", "code-analyzer", "function", "computer", "list-documents", "file-reader", "page-reader"
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
    enabled_tools: list[ToolType] = Field(default_factory=lambda: ["file-search"], alias="tool")

    # Server settings
    server_url: str = Field(
        default_factory=lambda: os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999"), alias="server"
    )

    # Display settings
    debug: bool = False
    render_format: str = Field(default="rich", alias="render")
    quiet: bool = False
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

    # Custom role and response style settings
    custom_role: str | None = Field(default=None, alias="role")
    response_language: str | None = Field(default=None, alias="language")
    response_style: str | None = Field(default=None, alias="style")

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

    @field_validator("response_language")
    @classmethod
    def validate_response_language(cls, v: str | None) -> str | None:
        """Validate response language."""
        if v is None:
            return v

        valid_languages = {
            "chinese",
            "english",
            "spanish",
            "french",
            "german",
            "japanese",
            "korean",
            "portuguese",
            "russian",
            "arabic",
        }

        if v.lower() not in valid_languages:
            raise ValueError(f"Invalid language: {v}. Must be one of: {', '.join(valid_languages)}")

        return v.lower()

    @field_validator("response_style")
    @classmethod
    def validate_response_style(cls, v: str | None) -> str | None:
        """Validate response style - accepts any string."""
        if v is None:
            return v

        # Accept any non-empty string
        if not v.strip():
            raise ValueError("Response style cannot be empty")

        return v.strip()

    @model_validator(mode="after")
    def validate_config_consistency(self) -> AppConfig:
        """Validate configuration consistency."""
        # If file search tools are enabled, ensure vec_ids are provided
        if any(tool in ["file-search", "list-documents"] for tool in self.enabled_tools):
            if not self.vec_ids:
                raise ValueError("Vector store IDs required when file search tools are enabled")

        return self

    @classmethod
    def from_args(cls, args) -> AppConfig:
        """Create config from command line arguments using Pydantic validation."""
        # Convert args namespace to dict and filter out None values
        args_dict = {k: v for k, v in vars(args).items() if v is not None}

        # Create config with validation - Pydantic handles aliases automatically
        return cls.model_validate(args_dict)

    def apply_dataset_config(self, dataset, args) -> AppConfig:
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

    def build_instructions_json(self) -> str | None:
        """Build instructions JSON from custom role and response style settings.

        Returns:
            JSON string for instructions field, or None if no custom settings are provided
        """
        if not (self.custom_role or self.response_language or self.response_style):
            return None

        instructions_config = {}

        # Add custom role if provided
        if self.custom_role:
            instructions_config["custom_role"] = self.custom_role

        # Add response style configuration
        response_style = {}

        # Add language if provided
        if self.response_language:
            response_style["language"] = self.response_language

        # Add custom style if provided
        if self.response_style:
            response_style["custom"] = self.response_style

        # Only add response_style if we have any style settings
        if response_style:
            instructions_config["response_style"] = response_style

        # Return JSON string
        import json

        return json.dumps(instructions_config, ensure_ascii=False)
