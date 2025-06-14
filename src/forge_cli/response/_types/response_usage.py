# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ._models import BaseModel

__all__ = ["ResponseUsage", "InputTokensDetails", "OutputTokensDetails"]


class InputTokensDetails(BaseModel):
    cached_tokens: int
    """The number of tokens that were retrieved from the cache.

    [More on prompt caching](https://platform.openai.com/docs/guides/prompt-caching).
    """


class OutputTokensDetails(BaseModel):
    reasoning_tokens: int
    """The number of reasoning tokens."""


class ResponseUsage(BaseModel):
    input_tokens: int
    """The number of input tokens."""

    input_tokens_details: InputTokensDetails
    """A detailed breakdown of the input tokens."""

    output_tokens: int
    """The number of output tokens."""

    output_tokens_details: OutputTokensDetails
    """A detailed breakdown of the output tokens."""

    total_tokens: int
    """The total number of tokens used."""

    def __add__(self, other: "ResponseUsage") -> "ResponseUsage":
        """Add two ResponseUsage objects together.

        This allows combining token usage from multiple LLMs or responses.

        Args:
            other: Another ResponseUsage object to add to this one

        Returns:
            A new ResponseUsage object with combined token counts
        """
        if not isinstance(other, ResponseUsage):
            return NotImplemented

        return ResponseUsage(
            input_tokens=self.input_tokens + other.input_tokens,
            input_tokens_details=InputTokensDetails(
                cached_tokens=self.input_tokens_details.cached_tokens + other.input_tokens_details.cached_tokens
            ),
            output_tokens=self.output_tokens + other.output_tokens,
            output_tokens_details=OutputTokensDetails(
                reasoning_tokens=self.output_tokens_details.reasoning_tokens
                + other.output_tokens_details.reasoning_tokens
            ),
            total_tokens=(self.input_tokens + other.input_tokens) + (self.output_tokens + other.output_tokens),
        )

    def __iadd__(self, other: "ResponseUsage") -> "ResponseUsage":
        """In-place addition of another ResponseUsage object.

        This allows updating token usage by adding another usage object to this one.

        Args:
            other: Another ResponseUsage object to add to this one

        Returns:
            This ResponseUsage object with updated token counts
        """
        if not isinstance(other, ResponseUsage):
            return NotImplemented

        self.input_tokens += other.input_tokens
        self.input_tokens_details.cached_tokens += other.input_tokens_details.cached_tokens
        self.output_tokens += other.output_tokens
        self.output_tokens_details.reasoning_tokens += other.output_tokens_details.reasoning_tokens
        self.total_tokens = self.input_tokens + self.output_tokens

        return self
