"""Web search tool call processor."""

from typing import Dict, Any
from .base import BaseToolCallProcessor


class WebSearchProcessor(BaseToolCallProcessor):
    """Processes web search tool calls."""

    TOOL_TYPE = "web_search"
    TOOL_CONFIG = {
        "emoji": "🌐",
        "action": "搜索网络",
        "status_searching": "正在搜索网络...",
        "status_completed": "搜索已完成",
        "results_text": "个网络结果",
    }
