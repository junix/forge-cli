# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from typing import Literal

from ._models import BaseModel

__all__ = ["WebSearchTool", "UserLocation"]


class UserLocation(BaseModel):
    type: Literal["approximate"]
    """The type of location approximation. Always `approximate`."""

    city: str | None = None
    """Free text input for the city of the user, e.g. `San Francisco`."""

    country: str | None = None
    """
    The two-letter [ISO country code](https://en.wikipedia.org/wiki/ISO_3166-1) of
    the user, e.g. `US`.
    """

    region: str | None = None
    """Free text input for the region of the user, e.g. `California`."""

    timezone: str | None = None
    """
    The [IANA timezone](https://timeapi.io/documentation/iana-timezones) of the
    user, e.g. `America/Los_Angeles`.
    """


class WebSearchTool(BaseModel):
    type: Literal["web_search_preview", "web_search_preview_2025_03_11", "web_search"]
    """The type of the web search tool.

    One of `web_search_preview` or `web_search_preview_2025_03_11`.
    """

    search_context_size: Literal["low", "medium", "high"] | None = None
    """High level guidance for the amount of context window space to use for the
    search.

    One of `low`, `medium`, or `high`. `medium` is the default.
    """

    user_location: UserLocation | None = None
    """The user's location."""
