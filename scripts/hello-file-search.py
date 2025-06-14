#!/usr/bin/env python3
"""
Multi-tool search example using the Knowledge Forge SDK.

This script demonstrates how to use the SDK to create responses using multiple tools,
including file search through vectorstores and web search for current information.

Features:
- Configurable tools: file-search, web-search, or both
- Support for multiple vectorstore IDs
- Web search with optional location context
- Streaming response with real-time updates
- Rich command line interface with customizable options
- Pretty output formatting with rich library
- Citation processing and display
"""

import argparse
import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

# For error handling
import aiohttp

# Rich library for better terminal output
from rich import print as rich_print
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

# Add the current directory to sys.path to allow importing from current directory
sys.path.insert(0, str(Path(__file__).parent))

# Import SDK functions from local sdk.py
from sdk import astream_response, async_get_vectorstore

# Rich library is used for terminal output

# Default vectorstore IDs to use if none are provided
DEFAULT_VEC_IDS = [
    "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
]


# ============================================================================
# Modular File Search Architecture
# ============================================================================

from dataclasses import dataclass, field
from enum import Enum


class FileSearchStatus(Enum):
    """Status of file search operation."""

    IDLE = "idle"
    SEARCHING = "searching"
    COMPLETED = "completed"


@dataclass
class ToolSearchState:
    """Tracks search state for a specific tool type."""

    tool_type: str = ""  # "file_search" or "web_search"
    query: str = ""
    queries: list[str] = field(default_factory=list)
    results_count: int | None = None
    status: FileSearchStatus = FileSearchStatus.IDLE
    query_time: float | None = None
    retrieval_time: float | None = None

    def to_display_info(self) -> dict[str, Any]:
        """Convert to display info dict."""
        info = {}
        if self.query:
            info["query"] = self.query
            info["tool_type"] = self.tool_type
            if self.query_time:
                info["query_time"] = self.query_time
        if self.status == FileSearchStatus.COMPLETED:
            info["results_count"] = self.results_count
            if self.retrieval_time:
                info["retrieval_time"] = self.retrieval_time
        return info


@dataclass
class MultiToolState:
    """Tracks state across multiple tool types."""

    # Dynamic tool states dictionary instead of hardcoded fields
    tool_states: dict[str, ToolSearchState] = field(default_factory=dict)

    def get_tool_state(self, tool_type: str) -> ToolSearchState:
        """Get state for specific tool type, creating if needed."""
        # Normalize tool type by extracting the base name
        # e.g., "response.file_search_call.searching" -> "file_search"
        base_tool_type = tool_type
        for pattern in ["response.", "_call", ".searching", ".completed", ".in_progress"]:
            base_tool_type = base_tool_type.replace(pattern, "")

        # Create state if it doesn't exist
        if base_tool_type not in self.tool_states:
            self.tool_states[base_tool_type] = ToolSearchState(tool_type=base_tool_type)

        return self.tool_states[base_tool_type]

    def get_all_completed_info(self) -> list[dict[str, Any]]:
        """Get display info for all completed tools."""
        info_list = []

        for tool_state in self.tool_states.values():
            if tool_state.status == FileSearchStatus.COMPLETED:
                info_list.append(tool_state.to_display_info())

        return info_list


@dataclass
class ToolSearchUpdate:
    """Update to tool search state."""

    tool_type: str = ""
    queries: list[str] | None = None
    results_count: int | None = None
    status: FileSearchStatus | None = None
    query_time: float | None = None
    retrieval_time: float | None = None


class EventDataExtractor:
    """Extract data from various event structures."""

    @staticmethod
    def extract_queries(event_data: dict[str, Any]) -> list[str]:
        """Extract queries from various event data structures."""
        if not isinstance(event_data, dict):
            return []

        # Check direct location
        if "queries" in event_data:
            return event_data.get("queries", [])

        # Check nested in any tool call (e.g., file_search_call, web_search_call, etc.)
        for key, value in event_data.items():
            if "_call" in key and isinstance(value, dict) and "queries" in value:
                return value.get("queries", [])

        # Check in output array
        if "output" in event_data:
            for item in event_data.get("output", []):
                if "_call" in item.get("type", "") and "queries" in item:
                    return item.get("queries", [])

        return []

    @staticmethod
    def extract_results_count(event_data: dict[str, Any]) -> tuple[int | None, bool]:
        """
        Extract results count and whether it was explicitly found.
        Returns: (count, was_found)
        """
        if not isinstance(event_data, dict):
            return None, False

        # Check direct location
        if "results" in event_data:
            results = event_data.get("results")
            if isinstance(results, list):
                return len(results), True
            return None, True  # Found but null

        # Check nested in any tool call
        for key, value in event_data.items():
            if "_call" in key and isinstance(value, dict) and "results" in value:
                results = value.get("results")
                if isinstance(results, list):
                    return len(results), True
                return None, True

        # Check in output array
        if "output" in event_data:
            for item in event_data.get("output", []):
                if "_call" in item.get("type", "") and "results" in item:
                    results = item.get("results")
                    if isinstance(results, list):
                        return len(results), True
                    return None, True

        return None, False

    @staticmethod
    def extract_from_reasoning(reasoning_text: str) -> int | None:
        """Try to extract result count from reasoning text."""
        if not reasoning_text:
            return None

        # Look for patterns like "网页1到3", "网页6", "网页8和9"
        webpage_matches = re.findall(r"网页\d+", reasoning_text)
        if webpage_matches:
            # Extract all webpage numbers
            webpage_nums = []
            for match in webpage_matches:
                num_match = re.search(r"\d+", match)
                if num_match:
                    webpage_nums.append(int(num_match.group()))
            # Use the highest number as an estimate
            return max(webpage_nums) if webpage_nums else None

        return None


class MultiToolEventHandler:
    """Handles all tool-related events (file search and web search)."""

    def __init__(self, debug: bool = False):
        self.state = MultiToolState()
        self.debug = debug
        self.file_id_to_name = {}  # Map file IDs to filenames from search results

    def can_handle(self, event_type: str) -> bool:
        """Check if this handler can process the event."""
        # Handle any event that looks like a tool call event
        return "_call.searching" in event_type or "_call.in_progress" in event_type or "_call.completed" in event_type

    def handle_event(
        self,
        event_type: str,
        event_data: dict[str, Any],
        query_time: float | None = None,
        retrieval_time: float | None = None,
    ) -> ToolSearchUpdate:
        """Process tool search event and return update."""

        # Extract tool type from event type
        # e.g., "response.file_search_call.searching" -> "file_search"
        # e.g., "response.code_interpreter_call.completed" -> "code_interpreter"
        tool_type = event_type
        if "response." in tool_type:
            tool_type = tool_type.replace("response.", "")
        if "_call." in tool_type:
            tool_type = tool_type.split("_call.")[0]

        update = ToolSearchUpdate(tool_type=tool_type)

        if "_call.searching" in event_type or "_call.in_progress" in event_type:
            # Extract queries
            queries = EventDataExtractor.extract_queries(event_data)
            if queries:
                update.queries = queries
                update.status = FileSearchStatus.SEARCHING
                if query_time:
                    update.query_time = query_time

        elif "_call.completed" in event_type:
            # Extract results
            count, found = EventDataExtractor.extract_results_count(event_data)
            if found:
                update.results_count = count
            update.status = FileSearchStatus.COMPLETED
            if retrieval_time:
                update.retrieval_time = retrieval_time

        # Apply update to internal state
        self.apply_update(update)

        return update

    def apply_update(self, update: ToolSearchUpdate):
        """Apply an update to the internal state."""
        tool_state = self.state.get_tool_state(update.tool_type)

        if update.queries:
            tool_state.queries = update.queries
            tool_state.query = ", ".join(update.queries)
        if update.results_count is not None:
            tool_state.results_count = update.results_count
        if update.status:
            tool_state.status = update.status
        if update.query_time:
            tool_state.query_time = update.query_time
        if update.retrieval_time:
            tool_state.retrieval_time = update.retrieval_time

    def extract_from_snapshot(self, snapshot_data: dict[str, Any]) -> list[ToolSearchUpdate]:
        """Extract tool search info from snapshot data."""
        updates = []

        if "output" in snapshot_data and isinstance(snapshot_data["output"], list):
            for item in snapshot_data["output"]:
                item_type = item.get("type")

                if "_call" in item_type:
                    # Extract tool type from item type (e.g., "file_search_call" -> "file_search")
                    tool_type = item_type.replace("_call", "")
                    update = ToolSearchUpdate(tool_type=tool_type)

                    # Extract queries
                    queries = item.get("queries", [])
                    if queries:
                        update.queries = queries

                    # Extract results and build file mapping (for file search)
                    results = item.get("results")
                    if results is not None:
                        if isinstance(results, list):
                            update.results_count = len(results)
                            # Build file ID to filename mapping for file search
                            if tool_type == "file_search":
                                for result in results:
                                    if isinstance(result, dict):
                                        file_id = result.get("file_id", "")
                                        filename = result.get("filename", "")
                                        if file_id and filename:
                                            self.file_id_to_name[file_id] = filename
                        else:
                            # Results are null - don't update count
                            pass

                    # Extract status
                    if item.get("status") == "completed":
                        update.status = FileSearchStatus.COMPLETED
                    elif item.get("status") in ["searching", "in_progress"]:
                        update.status = FileSearchStatus.SEARCHING

                    updates.append(update)

        # Apply updates
        for update in updates:
            if update.queries or update.results_count is not None or update.status:
                self.apply_update(update)

        return updates

    def update_from_reasoning(self, reasoning_text: str):
        """Update state based on reasoning text if needed."""
        # Check all tool states that exist
        for tool_state in self.state.tool_states.values():
            if tool_state.results_count is None and reasoning_text:
                count = EventDataExtractor.extract_from_reasoning(reasoning_text)
                if count:
                    tool_state.results_count = count


# ============================================================================
# End of Modular File Search Architecture
# ============================================================================


def process_snapshot_with_annotations(
    event_data: dict[str, Any],
    debug: bool = False,
    file_id_to_name: dict[str, str] | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """
    Process a complete snapshot response with annotations.
    Since each event is a full snapshot, we can process it completely.

    Args:
        event_data: Event data containing output
        debug: Whether to show debug info
        file_id_to_name: Optional mapping of file IDs to filenames

    Returns:
        Tuple of (full_text, citations_list)
    """
    full_text = ""
    all_citations = []
    if file_id_to_name is None:
        file_id_to_name = {}

    # Extract text and annotations from the current snapshot
    if "output" in event_data and isinstance(event_data["output"], list):
        for output_item in event_data["output"]:
            if output_item.get("type") == "message" and output_item.get("role") == "assistant":
                if "content" in output_item and isinstance(output_item["content"], list):
                    for content_item in output_item["content"]:
                        if content_item.get("type") == "output_text":
                            full_text = content_item.get("text", "")
                            annotations = content_item.get("annotations", [])

                            # Process all annotations
                            for i, ann in enumerate(annotations):
                                citation_type = ann.get("type")

                                if citation_type == "file_citation":
                                    # Debug: log annotation structure
                                    if debug and i == 0:  # Only log first annotation
                                        print(
                                            f"DEBUG: File citation annotation: {json.dumps(ann, indent=2, ensure_ascii=False)}"
                                        )

                                    # Extract file_id first
                                    file_id = ann.get("file_id", "")

                                    # Extract filename - might be in different locations
                                    filename = ann.get("filename", "")
                                    if not filename:
                                        # Try to get from file object
                                        if "file" in ann:
                                            filename = ann["file"].get("filename", "")

                                        # If still no filename, try the file_id mapping
                                        if not filename and file_id and file_id in file_id_to_name:
                                            filename = file_id_to_name[file_id]

                                        # Last resort
                                        if not filename:
                                            filename = "Unknown"

                                    # Convert 0-based page index to 1-based for human readability
                                    page_index = ann.get("index", "N/A")
                                    if isinstance(page_index, int):
                                        page_index = page_index + 1

                                    all_citations.append(
                                        {
                                            "number": i + 1,
                                            "type": "file",
                                            "page": page_index,
                                            "filename": filename,
                                            "file_id": file_id,
                                            "url": None,
                                            "title": filename,
                                        }
                                    )

                                elif citation_type == "url_citation":
                                    # Debug: log annotation structure
                                    if debug and i == 0:  # Only log first annotation
                                        print(
                                            f"DEBUG: URL citation annotation: {json.dumps(ann, indent=2, ensure_ascii=False)}"
                                        )

                                    # Extract URL citation information
                                    url = ann.get("url", "")
                                    title = ann.get("title", "")
                                    snippet = ann.get("snippet", "")

                                    # Use title as display name, fallback to URL domain
                                    display_name = title
                                    if not display_name and url:
                                        try:
                                            from urllib.parse import urlparse

                                            parsed = urlparse(url)
                                            display_name = parsed.netloc or url
                                        except:
                                            display_name = url

                                    if not display_name:
                                        display_name = "Web Source"

                                    all_citations.append(
                                        {
                                            "number": i + 1,
                                            "type": "web",
                                            "page": "Web",
                                            "filename": display_name,
                                            "file_id": None,
                                            "url": url,
                                            "title": title,
                                            "snippet": snippet,
                                        }
                                    )

    return full_text, all_citations


def format_citations_for_display(citations: list[dict[str, Any]]) -> str:
    """
    Format citations for display.

    Args:
        citations: List of citation dictionaries

    Returns:
        Formatted citations string
    """
    if not citations:
        return ""

    lines = ["\n📚 References:"]
    for cite in citations:
        if cite.get("type") == "web":
            # Web citation format
            url_display = cite.get("url", "")
            if len(url_display) > 60:
                url_display = url_display[:57] + "..."
            lines.append(f"  [{cite['number']}] {cite['filename']} ({url_display})")
        else:
            # File citation format
            lines.append(f"  [{cite['number']}] {cite['filename']}, p.{cite['page']} ({cite.get('file_id', 'N/A')})")
    return "\n".join(lines)


def format_reasoning_item(reasoning_item: dict[str, Any]) -> str:
    """Format a single reasoning item."""
    if "summary" not in reasoning_item:
        return ""

    reasoning_parts = []
    for summary_item in reasoning_item.get("summary", []):
        if summary_item.get("type") == "summary_text":
            text = summary_item.get("text", "")
            if text:
                # Split text into lines and add markdown quote indicator to each line
                lines = text.split("\n")
                for line in lines:
                    reasoning_parts.append(f"> {line}")

    return "\n".join(reasoning_parts) if reasoning_parts else ""


def format_file_search_item(search_item: dict[str, Any]) -> str:
    """Format a file search tool call item."""
    queries = search_item.get("queries", [])
    results = search_item.get("results", [])
    status = search_item.get("status", "")

    parts = []
    if queries:
        parts.append("📄 搜索文档:")
        for query in queries:
            parts.append(f"- {query}")

    if status == "completed" and results is not None:
        count = len(results) if isinstance(results, list) else 0
        parts.append("\n✅ 搜索已结束")

    return "\n".join(parts)


def format_document_finder_item(search_item: dict[str, Any]) -> str:
    """Format a document finder tool call item."""
    queries = search_item.get("queries", [])
    results = search_item.get("results", [])
    status = search_item.get("status", "")

    parts = []
    if queries:
        parts.append("🔍 查找文档:")
        for query in queries:
            parts.append(f"- {query}")

    if status == "completed" and results is not None:
        count = len(results) if isinstance(results, list) else 0
        parts.append("\n✅ 查找已结束")

    return "\n".join(parts)


def format_file_reader_item(search_item: dict[str, Any]) -> str:
    """Format a file reader tool call item."""
    query = search_item.get("query", "")
    doc_ids = search_item.get("doc_ids", [])
    status = search_item.get("status", "")
    execution_trace = search_item.get("execution_trace", "")
    progress = search_item.get("progress", 0.0)

    parts = []
    if query:
        parts.append(f"📖 精读文档: {query}")
    elif doc_ids:
        doc_count = len(doc_ids)
        parts.append(f"📖 精读文档: {doc_count} 个文档")

    if status == "completed":
        parts.append("\n\n✅ 精读已结束")
        # Extract chunk count from execution trace if available
        if execution_trace and "chunks" in execution_trace:
            import re

            chunk_match = re.search(r"(\d+) chunks", execution_trace)
            if chunk_match:
                chunk_count = chunk_match.group(1)
                parts.append(f"  📄 获得 {chunk_count} 个内容块")
    elif status and status != "completed":
        if progress and progress > 0:
            parts.append(f"\n\n⏳ 正在精读... ({progress * 100:.0f}%)")
        else:
            parts.append("\n\n⏳ 正在精读...")

    return "\n".join(parts)


def format_web_search_item(search_item: dict[str, Any]) -> str:
    """Format a web search tool call item."""
    queries = search_item.get("queries", [])
    status = search_item.get("status", "")

    parts = []
    if queries:
        parts.append("🌐 搜索网络:")
        for query in queries:
            parts.append(f"- {query}")

    if status == "completed":
        parts.append("\n✅ 搜索已结束")

    return "\n".join(parts)


def format_message_item(message_item: dict[str, Any], file_id_to_name: dict[str, str] | None = None) -> str:
    """Format a message item with text and citations."""
    if message_item.get("role") != "assistant":
        return ""

    if file_id_to_name is None:
        file_id_to_name = {}

    content_list = message_item.get("content", [])
    for content_item in content_list:
        if content_item.get("type") == "output_text":
            text = content_item.get("text", "")
            annotations = content_item.get("annotations", [])

            # Process citations from annotations
            citations = []
            for i, ann in enumerate(annotations):
                citation_type = ann.get("type")

                if citation_type == "file_citation":
                    file_id = ann.get("file_id", "")
                    filename = ann.get("filename", "")
                    if not filename:
                        if "file" in ann:
                            filename = ann["file"].get("filename", "")
                        if not filename and file_id and file_id in file_id_to_name:
                            filename = file_id_to_name[file_id]
                        if not filename:
                            filename = "Unknown"

                    page_index = ann.get("index", "N/A")
                    if isinstance(page_index, int):
                        page_index = page_index + 1

                    citations.append(
                        {
                            "number": i + 1,
                            "type": "file",
                            "page": page_index,
                            "filename": filename,
                            "file_id": file_id,
                            "url": None,
                            "title": filename,
                        }
                    )

                elif citation_type == "url_citation":
                    url = ann.get("url", "")
                    title = ann.get("title", "")
                    snippet = ann.get("snippet", "")

                    display_name = title
                    if not display_name and url:
                        try:
                            from urllib.parse import urlparse

                            parsed = urlparse(url)
                            display_name = parsed.netloc or url
                        except:
                            display_name = url

                    if not display_name:
                        display_name = "Web Source"

                    citations.append(
                        {
                            "number": i + 1,
                            "type": "web",
                            "page": "Web",
                            "filename": display_name,
                            "file_id": None,
                            "url": url,
                            "title": title,
                            "snippet": snippet,
                        }
                    )

            # Format the message content
            parts = []
            if text:
                parts.append(text)

            if citations:
                parts.append("")  # Empty line
                parts.append(format_citations_table(citations))

            return "\n".join(parts)

    return ""


def format_citations_table(citations: list[dict[str, Any]]) -> str:
    """Format citations as a markdown table."""
    if not citations:
        return ""

    # Check citation types to determine table format
    has_file_citations = any(cite.get("type") == "file" for cite in citations)
    has_web_citations = any(cite.get("type") == "web" for cite in citations)

    parts = ["### 📚 References", ""]

    if has_file_citations and has_web_citations:
        # Mixed citations - flexible table
        parts.extend(["| Citation | Source | Location | ID/URL |", "|----------|--------|----------|--------|"])
        for cite in citations:
            if cite.get("type") == "web":
                url_display = cite.get("url", "")
                if len(url_display) > 50:
                    url_display = url_display[:47] + "..."
                parts.append(f"| [{cite['number']}] | {cite['filename']} | Web | {url_display} |")
            else:
                parts.append(
                    f"| [{cite['number']}] | {cite['filename']} | p.{cite['page']} | {cite.get('file_id', 'N/A')} |"
                )
    elif has_web_citations:
        # Web citations only
        parts.extend(["| Citation | Title | URL |", "|----------|-------|-----|"])
        for cite in citations:
            url_display = cite.get("url", "")
            if len(url_display) > 60:
                url_display = url_display[:57] + "..."
            parts.append(f"| [{cite['number']}] | {cite['filename']} | {url_display} |")
    else:
        # File citations only
        parts.extend(["| Citation | Document | Page | File ID |", "|----------|----------|------|---------|"])
        for cite in citations:
            parts.append(f"| [{cite['number']}] | {cite['filename']} | {cite['page']} | {cite.get('file_id', 'N/A')} |")

    return "\n".join(parts)


def format_generic_tool_call_item(search_item: dict[str, Any]) -> str:
    """Format a generic tool call item."""
    item_type = search_item.get("type", "")
    queries = search_item.get("queries", [])
    results = search_item.get("results", [])
    status = search_item.get("status", "")

    # Extract tool name from type (e.g., "file_search_call" -> "file_search")
    tool_name = item_type.replace("_call", "") if "_call" in item_type else item_type

    # Map tool names to emojis and Chinese names
    tool_mapping = {
        "file_search": ("📄", "搜索文档"),
        "document_finder": ("🔍", "查找文档"),
        "web_search": ("🌐", "搜索网络"),
        "code_interpreter": ("💻", "执行代码"),
    }

    tool_emoji, tool_action = tool_mapping.get(tool_name, ("🔧", "执行工具"))

    parts = []
    if queries:
        parts.append(f"{tool_emoji} {tool_action}:")
        for query in queries:
            parts.append(f"- {query}")

    if status == "completed" and results is not None:
        count = len(results) if isinstance(results, list) else 0
        parts.append("\n✅ 操作已结束")

    return "\n".join(parts)


def format_native_order_display(
    output_items: list[dict[str, Any]], file_id_to_name: dict[str, str] | None = None
) -> str:
    """
    Format display content in native output order, preserving the original sequence
    and keeping reasoning segments separate.

    Args:
        output_items: Complete output array from response
        file_id_to_name: Mapping of file IDs to filenames

    Returns:
        Formatted markdown string in native order
    """
    if file_id_to_name is None:
        file_id_to_name = {}

    content_parts = []

    for item in output_items:
        item_type = item.get("type")

        if item_type == "reasoning":
            # Format individual reasoning segment
            reasoning_content = format_reasoning_item(item)
            if reasoning_content:
                content_parts.append(reasoning_content)

        elif item_type == "file_search_call":
            # Format file search tool call
            search_content = format_file_search_item(item)
            if search_content:
                content_parts.append(search_content)

        elif item_type == "document_finder_call":
            # Format document finder tool call
            search_content = format_document_finder_item(item)
            if search_content:
                content_parts.append(search_content)

        elif item_type == "file_reader_call":
            # Format file reader tool call
            search_content = format_file_reader_item(item)
            if search_content:
                content_parts.append(search_content)

        elif item_type == "web_search_call":
            # Format web search tool call
            search_content = format_web_search_item(item)
            if search_content:
                content_parts.append(search_content)

        elif item_type == "message":
            # Format message with text and citations
            message_content = format_message_item(item, file_id_to_name)
            if message_content:
                content_parts.append(message_content)

        elif item_type and "_call" in item_type:
            # Handle any other tool call types generically
            search_content = format_generic_tool_call_item(item)
            if search_content:
                content_parts.append(search_content)

    return "\n\n".join(content_parts)


def format_annotated_display(
    text: str,
    citations: list[dict[str, Any]],
    search_info: dict[str, Any] | None = None,
    reasoning: str | None = None,
    search_info_list: list[dict[str, Any]] | None = None,
) -> str:
    """
    Format complete display with all components for Rich mode.

    Args:
        text: Main response text
        citations: List of citations
        search_info: Single search information (for backward compatibility)
        reasoning: Reasoning text if available
        search_info_list: List of search information from multiple tools

    Returns:
        Formatted markdown string
    """
    content_parts = []

    # Add search info if available (use list if provided, otherwise single info)
    info_list = search_info_list if search_info_list else ([search_info] if search_info else [])

    for info in info_list:
        if info and info.get("query"):
            tool_type = info.get("tool_type", "")
            if tool_type == "file_search":
                tool_emoji = "📄"
                tool_name = "文档"
            elif tool_type == "document_finder":
                tool_emoji = "🔍"
                tool_name = "文档"
            elif tool_type == "web_search":
                tool_emoji = "🌐"
                tool_name = "网络"
            else:
                tool_emoji = "🔧"
                tool_name = "工具"

            query_line = f"{tool_emoji} 搜索{tool_name}: {info['query']}"
            if info.get("query_time"):
                query_line += f" (查询生成: {info['query_time']:.0f}ms)"
            content_parts.append(query_line)

        if info and "results_count" in info:
            count = info.get("results_count")
            tool_type = info.get("tool_type", "")
            if tool_type == "file_search":
                result_type = "内容块"
            elif tool_type == "document_finder":
                result_type = "文档"
            elif tool_type == "web_search":
                result_type = "网络结果"
            else:
                result_type = "结果"

            if count is not None:
                results_line = f"\n✅ 搜索已结束，找到了 {count} 个相关{result_type}"
            else:
                results_line = "\n✅ 搜索已结束"
            if info.get("retrieval_time"):
                results_line += f" (检索时间: {info['retrieval_time']:.0f}ms)"
            content_parts.append(results_line)
            content_parts.append("")  # Add extra newline after each tool's results

    if info_list:
        content_parts.append("")  # Empty line

    # Add reasoning if available
    if reasoning:
        content_parts.append("")
        for line in reasoning.split("\n"):
            if line.strip():
                content_parts.append(f"> {line}")
        content_parts.append("")  # Empty line

    # Add main text
    if text:
        content_parts.append(text)

    # Add citations if available
    if citations:
        content_parts.append("")  # Empty line
        content_parts.append("### 📚 References")
        content_parts.append("")

        # Check if we have mixed citation types
        has_file_citations = any(cite.get("type") == "file" for cite in citations)
        has_web_citations = any(cite.get("type") == "web" for cite in citations)

        if has_file_citations and has_web_citations:
            # Mixed citations - use flexible table
            content_parts.append("| Citation | Source | Location | ID/URL |")
            content_parts.append("|----------|--------|----------|--------|")
            for cite in citations:
                if cite.get("type") == "web":
                    url_display = cite.get("url", "")
                    if len(url_display) > 50:
                        url_display = url_display[:47] + "..."
                    content_parts.append(f"| [{cite['number']}] | {cite['filename']} | Web | {url_display} |")
                else:
                    content_parts.append(
                        f"| [{cite['number']}] | {cite['filename']} | p.{cite['page']} | {cite.get('file_id', 'N/A')} |"
                    )
        elif has_web_citations:
            # Web citations only
            content_parts.append("| Citation | Title | URL |")
            content_parts.append("|----------|-------|-----|")
            for cite in citations:
                url_display = cite.get("url", "")
                if len(url_display) > 60:
                    url_display = url_display[:57] + "..."
                content_parts.append(f"| [{cite['number']}] | {cite['filename']} | {url_display} |")
        else:
            # File citations only (original format)
            content_parts.append("| Citation | Document | Page | File ID |")
            content_parts.append("|----------|----------|------|---------|")
            for cite in citations:
                content_parts.append(
                    f"| [{cite['number']}] | {cite['filename']} | {cite['page']} | {cite.get('file_id', 'N/A')} |"
                )

    # Join all parts
    return "\n".join(content_parts)


async def process_with_streaming(
    question: str,
    vec_ids: list[str],
    model: str = "qwen-max-latest",
    effort: str = "low",
    max_results: int = 10,
    debug: bool = False,
    json_output: bool = False,
    throttle_ms: int = 0,
    enabled_tools: list[str] | None = None,
    web_location: dict[str, str] | None = None,
) -> dict[str, Any] | None:
    """
    Send a request using the astream_response approach for streaming.

    Args:
        question: Question to ask using the vector store search
        vec_ids: List of vector store IDs to search in
        model: Model to use for the response
        effort: Effort level for the response (low, medium, high)
        max_results: Maximum number of search results to return per vector store
        debug: Whether to show debug information
        json_output: Output the final response as JSON
        throttle_ms: Throttle the output by adding a delay between tokens (in milliseconds)
        enabled_tools: List of enabled tools ('file-search', 'web-search')
        web_location: Optional location context for web search

    Returns:
        The API response if successful, None otherwise
    """
    start_time = time.time()

    # Create input messages with question
    input_messages = [
        {
            "role": "user",
            "id": "user_message_1",
            "content": question,
        },
    ]

    # Create tools list based on enabled tools
    tools = []

    # Add file search tool if enabled and vectorstore IDs are provided
    if enabled_tools and "file-search" in enabled_tools and vec_ids:
        file_search_tool = {
            "type": "file_search",
            "vector_store_ids": vec_ids,
            "max_num_results": max_results,
        }
        tools.append(file_search_tool)

    # Add web search tool if enabled
    if enabled_tools and "web-search" in enabled_tools:
        web_search_tool = {"type": "web_search"}

        # Add location context if provided
        if web_location:
            web_search_tool["user_location"] = {"type": "approximate", **web_location}

        tools.append(web_search_tool)

    # Set tools to None if empty
    tools = tools if tools else None

    # Setup display - use rich unless JSON output is requested
    use_rich = not json_output
    rich_console = Console() if use_rich else None

    # Print request information
    if not json_output:
        if use_rich:
            # Create a rich panel for request information
            request_info = Text()
            request_info.append("\n📄 Request Information:\n", style="cyan bold")
            request_info.append("  💬 Question: ", style="green")
            request_info.append(f"{question}\n")
            request_info.append("  🔍 Vector Store IDs: ", style="green")
            request_info.append(f"{', '.join(vec_ids)}\n")
            request_info.append("  🤖 Model: ", style="green")
            request_info.append(f"{model}\n")
            request_info.append("  ⚙️ Effort Level: ", style="green")
            request_info.append(f"{effort}\n")
            request_info.append("  📊 Max Results: ", style="green")
            request_info.append(f"{max_results}\n")
            request_info.append("  🔄 Method: ", style="green")
            request_info.append("Direct streaming with Rich Live Display\n")
            request_info.append("  🛠️ Enabled Tools: ", style="green")
            if tools:
                tool_names = [tool["type"] for tool in tools]
                request_info.append(f"{', '.join(tool_names)}\n")
            else:
                request_info.append("None\n")
            if throttle_ms > 0:
                request_info.append("  ⏱️ Throttle: ", style="green")
                request_info.append(f"{throttle_ms}ms per token\n")

            rich_console.print(request_info)
            rich_console.print(Text("\n🔄 Streaming response (please wait):", style="yellow bold"))
            rich_console.print("=" * 80, style="blue")
        else:
            print("\n📄 Request Information:")
            print(f"  💬 Question: {question}")
            print(f"  🔍 Vector Store IDs: {', '.join(vec_ids)}")
            print(f"  🤖 Model: {model}")
            print(f"  ⚙️ Effort Level: {effort}")
            print(f"  📊 Max Results: {max_results}")
            print("  🔄 Method: Direct streaming")
            if tools:
                tool_names = [tool["type"] for tool in tools]
                print(f"  🛠️ Enabled Tools: {', '.join(tool_names)}")
            else:
                print("  🛠️ Enabled Tools: None")
            print("\n🔄 Streaming response (please wait):")
            print("=" * 80)

    # Variables to track streaming progress
    final_response = None
    current_citations = []  # Track citations from snapshots
    current_output_items = []  # Track complete output items in native order

    # Initialize modular multi-tool handler
    tool_handler = MultiToolEventHandler(debug=debug)

    # Time tracking variables
    search_start_time = None
    search_completed_time = None
    query_generation_time = None
    retrieval_time = None

    # Usage tracking variables
    usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    event_count = 0
    response_event_count = 0  # Response-specific event counter

    def collect_usage(usage_data):
        """Update the usage statistics from the provided usage data."""
        if not usage_data:
            return

        # Extract token information
        input_tokens = usage_data.get("input_tokens", 0)
        output_tokens = usage_data.get("output_tokens", 0)
        total_tokens = usage_data.get("total_tokens", 0)

        # Update usage tracking
        usage["input_tokens"] = input_tokens
        usage["output_tokens"] = output_tokens
        usage["total_tokens"] = total_tokens

    def format_usage_text(event_type):
        """Format the usage information into a rich Text object, right-aligned."""
        status_text = Text()
        # Use 1-based response event counter
        status_text.append(f"{response_event_count:05d}", style="cyan bold")
        status_text.append(" / ", style="white")
        status_text.append(f"{event_type}", style="green")
        status_text.append(" / ", style="white")
        status_text.append("  ↑ ", style="blue")
        status_text.append(f"{usage['input_tokens']}", style="blue bold")
        status_text.append("  ↓ ", style="magenta")
        status_text.append(f"{usage['output_tokens']}", style="magenta bold")
        status_text.append("  ∑ ", style="yellow")
        status_text.append(f"{usage['total_tokens']}", style="yellow bold")

        # Right-align the text
        status_text.justify = "right"
        return status_text

    # Set up Rich Live display if available
    if use_rich:
        # Create a live display context
        live_display = Live(Panel(""), refresh_per_second=10, console=rich_console, transient=False)
        live_display.start()
    else:
        live_display = None

    try:
        # Process the streaming response
        async for event_type, event_data in astream_response(
            input_messages=input_messages,
            model=model,
            effort=effort,
            store=True,
            tools=tools,
            debug=debug,
        ):
            # Update event count
            event_count += 1

            # Update response event count (1-based) only for response-related events
            if event_type and event_type.startswith("response"):
                response_event_count += 1

            # Collect usage data if present
            if event_data and isinstance(event_data, dict) and "usage" in event_data:
                collect_usage(event_data.get("usage"))
            # Time tracking for search events
            if event_type in [
                "response.file_search_call.searching",
                "response.file_search_call.in_progress",
            ]:
                if search_start_time is None:  # 只记录第一次
                    search_start_time = time.time()
                    query_generation_time = (search_start_time - start_time) * 1000

            if event_type == "response.file_search_call.completed":
                search_completed_time = time.time()
                retrieval_time = (search_completed_time - search_start_time) * 1000 if search_start_time else None

            # Print debug information if requested
            if debug and not json_output:
                debug_prefix = "DEBUG: "
                print(f"\n{debug_prefix}Event: {event_type}")

                # Special debug for file search events
                if "file_search" in str(event_type):
                    print(f"{debug_prefix}[FILE_SEARCH] Event type: {event_type}")
                    if event_data:
                        # Check for results in various places
                        if isinstance(event_data, dict):
                            if "results" in event_data:
                                print(
                                    f"{debug_prefix}[FILE_SEARCH] Direct results count: {len(event_data.get('results', []))}"
                                )
                            if "output" in event_data and isinstance(event_data["output"], list):
                                for idx, item in enumerate(event_data["output"]):
                                    if item.get("type") == "file_search_call":
                                        results = item.get("results")
                                        print(
                                            f"{debug_prefix}[FILE_SEARCH] output[{idx}] results: {type(results)}, count: {len(results) if isinstance(results, list) else 'N/A'}"
                                        )

                # Special debug for Rich mode to track what's happening
                if use_rich and event_type in [
                    "response.file_search_call.completed",
                    "response.output_item.done",
                    "final_response",
                ]:
                    print(f"{debug_prefix}[RICH MODE] Processing event: {event_type}")
                    if event_data:
                        print(f"{debug_prefix}[RICH MODE] Event data keys: {list(event_data.keys())}")

                if event_data:
                    # Special handling for different event types in debug
                    if "output" in event_data and isinstance(event_data.get("output"), list):
                        # Check if output contains reasoning items
                        for idx, output_item in enumerate(event_data["output"]):
                            if isinstance(output_item, dict) and output_item.get("type") == "reasoning":
                                print(f"{debug_prefix}  Found reasoning in output[{idx}]:")
                                if "summary" in output_item:
                                    for s_idx, summary in enumerate(output_item["summary"]):
                                        if summary.get("type") == "summary_text":
                                            print(
                                                f"{debug_prefix}    Summary[{s_idx}]: {summary.get('text', '')[:200]}..."
                                            )

                    # Print full event data
                    print(f"{debug_prefix}{json.dumps(event_data, indent=2, ensure_ascii=False)}")

            # Handle tool events with modular handler
            if tool_handler.can_handle(event_type):
                # Handle the event
                update = tool_handler.handle_event(
                    event_type,
                    event_data,
                    query_time=query_generation_time,
                    retrieval_time=retrieval_time,
                )

                # Update display for Rich mode
                if use_rich and (update.queries or update.status == FileSearchStatus.COMPLETED):
                    # For tool events, if we have current output items, use native order
                    # Otherwise, fall back to simple status display
                    if current_output_items:
                        display_content = format_native_order_display(
                            output_items=current_output_items,
                            file_id_to_name=tool_handler.file_id_to_name,
                        )
                    else:
                        # Fallback for early tool events before any snapshot
                        tool_state = tool_handler.state.get_tool_state(update.tool_type)
                        search_info = tool_state.to_display_info()

                        status_text = ""
                        if tool_state.status == FileSearchStatus.SEARCHING:
                            tool_name = "文档" if update.tool_type == "file_search" else "网络"
                            status_text = f"⏳ 正在搜索{tool_name}..."

                        display_content = format_annotated_display(
                            text=status_text,
                            citations=[],
                            search_info=search_info,
                            reasoning=None,
                        )

                    # Update display
                    subtitle = format_usage_text(event_type)
                    try:
                        live_display.update(
                            Panel(
                                Markdown(display_content),
                                title=question,
                                subtitle=subtitle,
                                border_style="green",
                            )
                        )
                    except Exception:
                        live_display.update(
                            Panel(
                                Text(display_content),
                                title=question,
                                subtitle=subtitle,
                                border_style="green",
                            )
                        )

            # Process snapshot data with annotations
            elif event_data and "output" in event_data:
                # Store complete output items for native order display
                current_output_items = event_data.get("output", [])

                # Extract full text and citations from snapshot (for backward compatibility)
                snapshot_text, snapshot_citations = process_snapshot_with_annotations(
                    event_data,
                    debug=debug,
                    file_id_to_name=tool_handler.file_id_to_name,
                )

                # Update current citations if we have new ones
                if snapshot_citations:
                    current_citations = snapshot_citations

                # Update tool states from snapshot
                tool_handler.extract_from_snapshot(event_data)

                # Update tool handler with reasoning info from snapshot
                for output_item in current_output_items:
                    if output_item.get("type") == "reasoning" and "summary" in output_item:
                        for summary_item in output_item.get("summary", []):
                            if summary_item.get("type") == "summary_text" and "text" in summary_item:
                                reasoning_text = summary_item["text"]
                                if reasoning_text:
                                    tool_handler.update_from_reasoning(reasoning_text)

                # Update Rich display with complete snapshot in native order
                if use_rich:
                    # Use native order display for complete snapshot
                    display_content = format_native_order_display(
                        output_items=current_output_items,
                        file_id_to_name=tool_handler.file_id_to_name,
                    )

                    # Update display
                    subtitle = format_usage_text(event_type or "unknown")
                    try:
                        live_display.update(
                            Panel(
                                Markdown(display_content),
                                title=question,
                                subtitle=subtitle,
                                border_style="green",
                            )
                        )
                    except Exception:
                        live_display.update(
                            Panel(
                                Text(display_content),
                                title=question,
                                subtitle=subtitle,
                                border_style="green",
                            )
                        )

            # Skip text delta events in Rich mode since we're using snapshots
            if event_type == "response.output_text.delta" and use_rich:
                # In Rich mode, we handle everything through snapshots
                pass

            # Handle search events for non-Rich mode
            if tool_handler.can_handle(event_type) and not use_rich and not json_output:
                # Get the tool state for this event
                tool_type = "file_search" if "file_search" in event_type else "web_search"
                tool_state = tool_handler.state.get_tool_state(tool_type)
                prev_status = tool_state.status

                # Process the event (already done above, but need to check for non-rich)
                if event_type in [
                    "response.file_search_call.searching",
                    "response.file_search_call.in_progress",
                    "response.web_search_call.searching",
                    "response.web_search_call.in_progress",
                ]:
                    if tool_state.status == FileSearchStatus.SEARCHING and prev_status != FileSearchStatus.SEARCHING:
                        search_type = "vector stores" if "file_search" in event_type else "web"
                        print(f"\n🔍 Searching {search_type}...")

                        if tool_state.query:
                            print(f"  Query: {tool_state.query}")

                elif "_call.completed" in event_type:
                    print("\n✅ Search completed")

                    if tool_state.results_count is not None:
                        result_type = "relevant chunks" if "file_search" in event_type else "web results"
                        print(f"  Found {tool_state.results_count} {result_type}")

            # Handle text delta events for non-Rich mode
            if event_type == "response.output_text.delta" and event_data and "text" in event_data and not use_rich:
                if not json_output:  # Only print streaming output in normal mode
                    text_content = event_data["text"]

                    # Extract the actual text from the event data, which can be nested
                    fragment = ""
                    if isinstance(text_content, dict) and "text" in text_content:
                        fragment = text_content["text"]
                    elif isinstance(text_content, str):
                        fragment = text_content

                    # Process the fragment
                    if fragment:
                        # For non-rich mode, just print the text
                        print(fragment, end="", flush=True)

                        # Apply throttling if requested
                        if throttle_ms > 0:
                            await asyncio.sleep(throttle_ms / 1000)

            # Handle error events
            if event_type == "error" and event_data and not json_output:
                error_message = event_data.get("message", "Unknown error occurred")
                if use_rich:
                    error_panel = Panel(
                        Text(f"Error: {error_message}", style="red bold"),
                        title="Error",
                        border_style="red",
                    )
                    live_display.update(error_panel)
                else:
                    print(f"\nError: {error_message}")

            # Exit on done event
            if event_type == "done":
                # Store final response data
                final_response = event_data
                break

        # Stop the live display if it's running
        if use_rich and live_display:
            live_display.stop()

        end_time = time.time()
        duration = end_time - start_time

        if json_output and final_response:
            # In JSON mode, add citation summary to response
            if current_citations:
                final_response["citations_summary"] = {
                    "total_citations": len(current_citations),
                    "citations": current_citations,
                }
            print(json.dumps(final_response, indent=2, ensure_ascii=False))
            return final_response

        if not json_output and not use_rich:
            print("=" * 80)

        if final_response:
            # Check if there's actual text content in the response
            has_content = False
            content_text = ""

            # Log the response structure for debugging
            if debug:
                print(f"\nResponse structure: {json.dumps(final_response, indent=2, ensure_ascii=False)}")

            # Extract text content and citations from final response
            if isinstance(final_response, dict):
                # Process the final snapshot to get text and citations
                content_text, final_citations = process_snapshot_with_annotations(
                    final_response,
                    debug=debug,
                    file_id_to_name=tool_handler.file_id_to_name,
                )
                if content_text:
                    has_content = True
                if final_citations:
                    current_citations = final_citations

                # Also update tool handler with final data
                tool_handler.extract_from_snapshot(final_response)

            if not json_output:
                # Display completion information
                if use_rich:
                    # 对于 Rich 模式，完成信息已经在内容中了
                    completion_info = Text()
                    completion_info.append("\n✅ Response completed successfully!\n", style="green bold")
                    completion_info.append("  🆔 Response ID: ", style="yellow")
                    completion_info.append(f"{final_response.get('id')}\n")
                    completion_info.append("  🤖 Model used: ", style="yellow")
                    completion_info.append(f"{final_response.get('model')}\n")
                    completion_info.append("  ⏱️ Time taken: ", style="yellow")
                    completion_info.append(f"{duration:.2f} seconds\n")

                    rich_console.print(completion_info)
                else:
                    print("\n✅ Response completed successfully!")
                    print(f"  🆔 Response ID: {final_response.get('id')}")
                    print(f"  🤖 Model used: {final_response.get('model')}")
                    print(f"  ⏱️ Time taken: {duration:.2f} seconds")

                # Display vector store info
                await display_vectorstore_info(vec_ids, use_rich)

                # Show content if found, or a warning if not
                if has_content:
                    if use_rich:
                        rich_console.print(Text("\n📃 Response Content:", style="cyan bold"))
                        # Try to show as markdown if possible
                        try:
                            rich_console.print(Markdown(content_text))
                        except Exception:
                            # Fallback to plain text if markdown parsing fails
                            rich_console.print(Text(content_text))
                    else:
                        print("\n📃 Response Content:")
                        print(f"{content_text}")

                    # Display citations for non-Rich mode
                    if not use_rich and current_citations:
                        citation_display = format_citations_for_display(current_citations)
                        print(citation_display)
                else:
                    warning_msg = "⚠️  Warning: No text content found in the response."
                    if use_rich:
                        rich_console.print(Text(warning_msg, style="yellow"))
                    else:
                        print(f"\n{warning_msg}")

            return final_response
        else:
            error_msg = "❌ No final response received."
            if not json_output:
                if use_rich:
                    rich_console.print(Text(error_msg, style="red bold"))
                else:
                    print(f"\n{error_msg}")
            return None

    except Exception as e:
        if not json_output:
            error_msg = f"❌ Error during streaming request: {e}"
            if use_rich:
                # Make sure to stop the live display before showing error
                if live_display:
                    live_display.stop()
                rich_console.print(Text(error_msg, style="red bold"))
            else:
                print(f"\n{error_msg}")
        return None


async def display_vectorstore_info(vec_ids: list[str], use_rich: bool = True) -> None:
    """
    Display information about the vector stores being used in the search.

    Args:
        vec_ids: List of vector store IDs to display information for
        use_rich: Whether to use Rich library for display
    """
    # Check if we should use rich for display
    rich_console = Console() if use_rich else None

    if use_rich:
        rich_console.print(Text("\n📚 Vector Store Information:", style="cyan bold"))
    else:
        print("\n📚 Vector Store Information:")

    for i, vec_id in enumerate(vec_ids, 1):
        try:
            vec_info = await async_get_vectorstore(vec_id)
            if vec_info:
                if use_rich:
                    # Create a rich table for vector store info
                    vec_table = Text()
                    vec_table.append(f"  🔍 Vector Store #{i}:\n", style="blue bold")
                    vec_table.append("    🔑 ID: ", style="yellow")
                    vec_table.append(f"{vec_id}\n")
                    vec_table.append("    📝 Name: ", style="yellow")
                    vec_table.append(f"{vec_info.get('name', 'Unknown')}\n")

                    # Show description if available
                    if vec_info.get("description"):
                        vec_table.append("    📄 Description: ", style="yellow")
                        vec_table.append(f"{vec_info.get('description')}\n")

                    # Show file count if available
                    file_count = len(vec_info.get("file_ids", []))
                    vec_table.append("    📊 File Count: ", style="yellow")
                    vec_table.append(f"{file_count}\n")

                    # Show creation date if available
                    if vec_info.get("created_at"):
                        vec_table.append("    🕒 Created: ", style="yellow")
                        vec_table.append(f"{vec_info.get('created_at')}\n")

                    rich_console.print(vec_table)
                else:
                    # Plain text output (no colors)
                    print(f"  🔍 Vector Store #{i}:")
                    print(f"    🔑 ID: {vec_id}")
                    print(f"    📝 Name: {vec_info.get('name', 'Unknown')}")

                    # Show description if available
                    if vec_info.get("description"):
                        print(f"    📄 Description: {vec_info.get('description')}")

                    # Show file count if available
                    file_count = len(vec_info.get("file_ids", []))
                    print(f"    📊 File Count: {file_count}")

                    # Show creation date if available
                    if vec_info.get("created_at"):
                        print(f"    🕒 Created: {vec_info.get('created_at')}")
            else:
                if use_rich:
                    error_text = Text()
                    error_text.append(f"  ❓ Vector Store #{i}:\n", style="yellow")
                    error_text.append(f"    🔑 ID: {vec_id}\n")
                    error_text.append(
                        "    ⚠️ Status: Unable to fetch vectorstore details\n",
                        style="red",
                    )
                    rich_console.print(error_text)
                else:
                    # Plain text output (no colors)
                    print(f"  ❓ Vector Store #{i}:")
                    print(f"    🔑 ID: {vec_id}")
                    print("    ⚠️ Status: Unable to fetch vectorstore details")
        except Exception as e:
            if use_rich:
                error_text = Text()
                error_text.append(f"  ❌ Vector Store #{i}:\n", style="red bold")
                error_text.append(f"    🔑 ID: {vec_id}\n")
                error_text.append(f"    🚫 Error: {e}\n", style="red")
                rich_console.print(error_text)
            else:
                # Plain text output (no colors)
                print(f"  ❌ Vector Store #{i}:")
                print(f"    🔑 ID: {vec_id}")
                print(f"    🚫 Error: {e}")


async def main():
    """Main function to handle command line arguments and run the request."""
    # Check if no arguments provided
    show_help = len(sys.argv) == 1

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Send requests to Knowledge Forge API with configurable tools (file-search, web-search)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--vec-id",
        action="append",
        default=None,
        help="Vector store ID(s) to search in (can specify multiple)",
    )
    parser.add_argument(
        "--question",
        "-q",
        type=str,
        default="What information can you find in the documents?",
        help="Question to ask about the document content",
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default="qwen-max-latest",
        help="Model to use for the response",
    )
    parser.add_argument(
        "--effort",
        "-e",
        type=str,
        choices=["low", "medium", "high", "dev"],
        default="low",
        help="Effort level for the response",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Maximum number of search results to return per vector store",
    )
    parser.add_argument(
        "--server",
        default=os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999"),
        help="Server URL (default: from env or http://localhost:9999)",
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Enable debug output with detailed event information",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the response as JSON",
    )
    parser.add_argument(
        "--throttle",
        type=int,
        default=0,
        help="Throttle the output by adding a delay between tokens (in milliseconds)",
    )
    parser.add_argument(
        "--save",
        type=str,
        help="Save the response to a file",
    )
    parser.add_argument(
        "--quiet",
        "-Q",
        action="store_true",
        help="Quiet mode - minimal output",
    )
    parser.add_argument(
        "--tool",
        "-t",
        action="append",
        choices=["file-search", "web-search"],
        help="Enable specific tools (can specify multiple: file-search, web-search)",
    )
    parser.add_argument(
        "--country",
        type=str,
        help="Country for web search location context (e.g., 'US', 'CN')",
    )
    parser.add_argument(
        "--city",
        type=str,
        help="City for web search location context (e.g., 'San Francisco')",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="store_true",
        help="Show version information and exit",
    )

    args = parser.parse_args()

    # Show help if no arguments provided and not asking for help directly
    if show_help and not any(arg in sys.argv for arg in ["-h", "--help"]):
        parser.print_help()
        print("\nExample usage:")
        print("  # File search only (default if vec-id provided)")
        print('  python -m commands.hello-file-search -q "What information is in these documents?"')
        print("  python -m commands.hello-file-search --vec-id vec_id1 vec_id2 --model qwen-max --effort medium")
        print("")
        print("  # Web search only")
        print('  python -m commands.hello-file-search -t web-search -q "What happened today in tech?"')
        print(
            '  python -m commands.hello-file-search -t web-search --country US --city "San Francisco" -q "Local weather"'
        )
        print("")
        print("  # Both tools together")
        print(
            '  python -m commands.hello-file-search -t file-search -t web-search --vec-id vec_id1 -q "Compare docs with latest info"'
        )
        print(
            '  python -m commands.hello-file-search --tool file-search --tool web-search --vec-id vec_id1 --effort high -q "Research question"'
        )
        print("")
        print("  # Explicit tool selection")
        print("  python -m commands.hello-file-search -t file-search --vec-id vec_id1 --effort dev --debug")
        return

    # Handle version display
    if args.version:
        version = "1.0.0"
        print(f"Knowledge Forge File Search v{version}")
        print("Part of the Knowledge Forge SDK toolkit")
        return

    # Use default vector IDs if none provided
    if args.vec_id is None:
        args.vec_id = DEFAULT_VEC_IDS

    # Handle quiet mode
    if args.quiet:
        pass  # Quiet mode handling

    # Set server URL if provided
    if args.server != os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999"):
        os.environ["KNOWLEDGE_FORGE_URL"] = args.server
        if not args.quiet:
            print(f"🔗 Using server: {args.server}")

    # Prepare enabled tools list
    enabled_tools = args.tool if args.tool else []

    # If no tools specified, default to file-search for backward compatibility (only if vec_ids provided)
    if not enabled_tools and args.vec_id:
        enabled_tools = ["file-search"]

    # Prepare web location context
    web_location = None
    if args.country or args.city:
        web_location = {}
        if args.country:
            web_location["country"] = args.country
        if args.city:
            web_location["city"] = args.city

    # Run the request with streaming
    response = await process_with_streaming(
        question=args.question,
        vec_ids=args.vec_id,
        model=args.model,
        effort=args.effort,
        max_results=args.max_results,
        debug=args.debug,
        json_output=args.json,
        throttle_ms=args.throttle,
        enabled_tools=enabled_tools,
        web_location=web_location,
    )

    # Save response to file if requested
    if args.save and response:
        try:
            with open(args.save, "w", encoding="utf-8") as f:
                if args.json:
                    # Save the full response
                    json.dump(response, f, indent=2, ensure_ascii=False)
                else:
                    # Save just the text response
                    for msg in response.get("output", []):
                        if msg.get("role") == "assistant" and "content" in msg:
                            content = msg["content"]
                            if isinstance(content, list):
                                for item in content:
                                    if item.get("type") == "output_text":
                                        f.write(f"{item.get('text', '')}\n")
                            else:
                                f.write(f"{content}\n")

            if not args.quiet and not args.json:
                print(f"\n💾 Response saved to: {args.save}")
        except Exception as e:
            if not args.quiet and not args.json:
                print(f"\n❌ Error saving response to file: {e}")


def handle_exceptions(func):
    """
    Decorator to handle exceptions gracefully.

    Args:
        func: The async function to wrap

    Returns:
        A wrapper function that handles exceptions
    """

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\n\nOperation canceled by user.")
            return None
        except aiohttp.ClientConnectorError as e:
            print(
                f"\n❌ Connection error: Could not connect to server. Is the server running at {os.environ.get('KNOWLEDGE_FORGE_URL')}?"
            )
            print(f"  Error details: {e}")
            return None
        except aiohttp.ClientResponseError as e:
            print(f"\n❌ Server error: The server returned an error: {e.status} {e.message}")
            return None
        except Exception as e:
            print(f"\n❌ Unexpected error: {type(e).__name__}: {e}")
            if "--debug" in sys.argv or "-d" in sys.argv:
                import traceback

                traceback.print_exc()
            return None

    return wrapper


if __name__ == "__main__":
    # Apply the exception handler decorator to main
    wrapped_main = handle_exceptions(main)

    try:
        asyncio.run(wrapped_main())
    except KeyboardInterrupt:
        print("\n\nOperation canceled by user.")
    except Exception as e:
        print(f"\n❌ Fatal error: {type(e).__name__}: {e}")
        if "--debug" in sys.argv or "-d" in sys.argv:
            import traceback

            traceback.print_exc()
        sys.exit(1)
