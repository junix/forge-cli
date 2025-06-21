"""Configuration for plaintext renderer display options."""

from pydantic import BaseModel, Field, field_validator


class PlaintextDisplayConfig(BaseModel):
    """Configuration for plaintext renderer display options."""

    show_reasoning: bool = Field(True, description="Whether to show reasoning/thinking content")
    show_citations: bool = Field(True, description="Whether to show citation details")
    show_tool_details: bool = Field(True, description="Whether to show detailed tool information")
    show_usage: bool = Field(True, description="Whether to show token usage statistics")
    show_metadata: bool = Field(False, description="Whether to show response metadata")
    show_status_header: bool = Field(True, description="Whether to show status header")
    max_text_preview: int = Field(100, description="Maximum characters for text previews")
    refresh_rate: int = Field(10, description="Live display refresh rate per second")
    indent_size: int = Field(2, description="Number of spaces for indentation")
    separator_char: str = Field("─", description="Character for separators")
    separator_length: int = Field(60, description="Length of separator lines")

    @field_validator("refresh_rate")
    @classmethod
    def validate_refresh_rate(cls, v):
        if v < 1 or v > 30:
            raise ValueError("Refresh rate must be between 1 and 30")
        return v

    @field_validator("indent_size")
    @classmethod
    def validate_indent_size(cls, v):
        if v < 0 or v > 8:
            raise ValueError("Indent size must be between 0 and 8")
        return v 