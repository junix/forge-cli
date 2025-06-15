"""Web search tool call processor with typed API support."""

from typing import Any
from .base_typed import BaseToolCallProcessor


class WebSearchProcessor(BaseToolCallProcessor):
    """Processes web search tool calls with typed API support."""

    TOOL_TYPE = "web_search"
    TOOL_CONFIG = {
        "emoji": "🌐",
        "action": "搜索网络",
        "status_searching": "正在搜索网络...",
        "status_completed": "搜索已完成",
        "results_text": "个搜索结果",
    }

    def _add_tool_specific_data(
        self,
        item: Any,
        processed: dict[str, Any],
    ) -> None:
        """Add web search specific data."""
        # Extract location info
        if hasattr(item, "country"):
            processed["country"] = str(item.country) if item.country else None

        if hasattr(item, "city"):
            processed["city"] = str(item.city) if item.city else None

    def _add_tool_specific_formatting(self, processed: dict[str, Any], parts: list[str]) -> None:
        """Add web search specific formatting."""
        # Add location if specified
        country = processed.get("country")
        city = processed.get("city")

        if country or city:
            location_parts = []
            if city:
                location_parts.append(city)
            if country:
                location_parts.append(country)
            if location_parts:
                parts.append(f"📍 位置: {', '.join(location_parts)}")

    def extract_urls(self, item: Any) -> list[str]:
        """Extract URLs from search results."""
        urls = []

        results = self.extract_results(item)
        for result in results:
            if hasattr(result, "url"):
                urls.append(str(result.url))

        return urls
