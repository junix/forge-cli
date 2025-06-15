#!/usr/bin/env python3
"""
Multi-tool search example using the Knowledge Forge SDK with typed API.

This script demonstrates the migration from dict-based to typed Response API
while maintaining all the original functionality.

Features:
- Typed Request/Response objects for better type safety
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
from typing import Any, Optional, List, Dict

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

# Import typed SDK functions and types
from sdk import (
    astream_typed_response,
    async_get_vectorstore,
    create_typed_request,
)
from forge_cli.response._types import (
    Response,
    FileSearchTool,
    WebSearchTool,
)
from forge_cli.response._types.web_search_tool import UserLocation
from forge_cli.response.adapters import MigrationHelper

# Default vectorstore IDs to use if none are provided
DEFAULT_VEC_IDS = [
    "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
]

# Global console object for rich output
console = Console()


class FileSearchStatus:
    """Status constants for file search."""

    SEARCHING = "searching"
    COMPLETED = "completed"
    FAILED = "failed"


class ToolSearchUpdate:
    """Update information for tool search status."""

    def __init__(self, tool_type: str):
        self.tool_type = tool_type
        self.queries: Optional[List[str]] = None
        self.results_count: Optional[int] = None
        self.status: Optional[str] = None
        self.query_time: Optional[float] = None
        self.retrieval_time: Optional[float] = None


class ToolState:
    """State for a single tool."""

    def __init__(self, tool_type: str):
        self.tool_type = tool_type
        self.query = ""
        self.queries: List[str] = []
        self.results_count = 0
        self.status = ""
        self.query_time: Optional[float] = None
        self.retrieval_time: Optional[float] = None


class MultiToolState:
    """Manages state for multiple tools."""

    def __init__(self):
        self.tools: Dict[str, ToolState] = {}
        self.final_text = ""
        self.citations: List[Dict[str, Any]] = []

    def get_tool_state(self, tool_type: str) -> ToolState:
        """Get or create tool state."""
        if tool_type not in self.tools:
            self.tools[tool_type] = ToolState(tool_type)
        return self.tools[tool_type]


class EventDataExtractor:
    """Extracts data from typed Response objects."""

    @staticmethod
    def extract_queries(response: Optional[Response]) -> List[str]:
        """Extract search queries from response."""
        if not response:
            return []

        queries = []
        for item in response.output:
            # Check for file search tool calls
            if hasattr(item, "type") and item.type == "file_search_call":
                if hasattr(item, "queries") and item.queries:
                    queries.extend(item.queries)
            # Check for web search tool calls
            elif hasattr(item, "type") and item.type == "web_search_call":
                if hasattr(item, "queries") and item.queries:
                    queries.extend(item.queries)

        return queries

    @staticmethod
    def extract_results_count(response: Optional[Response]) -> tuple[int, bool]:
        """Extract results count from response."""
        if not response:
            return 0, False

        total_count = 0
        found = False

        for item in response.output:
            if hasattr(item, "type") and "search_call" in item.type:
                if hasattr(item, "results") and item.results:
                    total_count += len(item.results)
                    found = True

        return total_count, found

    @staticmethod
    def extract_citations(response: Optional[Response]) -> List[Dict[str, Any]]:
        """Extract citations from response."""
        if not response:
            return []

        citations = []

        # Use Response's built-in citation methods
        try:
            citable_items = response.collect_citable_items()
            for idx, item in enumerate(citable_items):
                citation = {
                    "id": str(idx + 1),
                    "file_id": getattr(item, "file_id", "unknown"),
                    "filename": getattr(item, "filename", "unknown"),
                    "page": getattr(item, "page", None),
                }
                citations.append(citation)
        except Exception:
            # Fallback to manual extraction if needed
            pass

        return citations


class MultiToolEventHandler:
    """Handles all tool-related events using typed Response objects."""

    def __init__(self, debug: bool = False):
        self.state = MultiToolState()
        self.debug = debug
        self.file_id_to_name: Dict[str, str] = {}

    def can_handle(self, event_type: str) -> bool:
        """Check if this handler can process the event."""
        return "_call.searching" in event_type or "_call.in_progress" in event_type or "_call.completed" in event_type

    def handle_event(
        self,
        event_type: str,
        response: Optional[Response],
        query_time: Optional[float] = None,
        retrieval_time: Optional[float] = None,
    ) -> ToolSearchUpdate:
        """Process tool search event using typed Response."""

        # Extract tool type from event type
        tool_type = event_type
        if "response." in tool_type:
            tool_type = tool_type.replace("response.", "")
        if "_call." in tool_type:
            tool_type = tool_type.split("_call.")[0]

        update = ToolSearchUpdate(tool_type=tool_type)

        if "_call.searching" in event_type or "_call.in_progress" in event_type:
            # Extract queries using typed API
            queries = EventDataExtractor.extract_queries(response)
            if queries:
                update.queries = queries
                update.status = FileSearchStatus.SEARCHING
                if query_time:
                    update.query_time = query_time

        elif "_call.completed" in event_type:
            # Extract results using typed API
            count, found = EventDataExtractor.extract_results_count(response)
            if found:
                update.results_count = count
            update.status = FileSearchStatus.COMPLETED
            if retrieval_time:
                update.retrieval_time = retrieval_time

            # Store file mappings if available
            if response:
                self._extract_file_mappings(response)

        # Apply update to internal state
        self.apply_update(update)

        return update

    def _extract_file_mappings(self, response: Response):
        """Extract file ID to name mappings from response."""
        for item in response.output:
            if hasattr(item, "type") and "search_call" in item.type:
                if hasattr(item, "results") and item.results:
                    for result in item.results:
                        if hasattr(result, "file_id") and hasattr(result, "filename"):
                            self.file_id_to_name[result.file_id] = result.filename

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


def create_display_text(state: MultiToolState, is_final: bool = False) -> str:
    """Create formatted display text for the current state."""
    lines = []

    # Show tool states
    for tool_type, tool_state in state.tools.items():
        emoji = "📚" if tool_type == "file_search" else "🌐" if tool_type == "web_search" else "🔧"
        status_emoji = "✅" if tool_state.status == FileSearchStatus.COMPLETED else "🔍"

        lines.append(f"{emoji} **{tool_type.replace('_', ' ').title()}** {status_emoji}")

        if tool_state.query:
            lines.append(f"   Query: {tool_state.query}")

        if tool_state.results_count > 0:
            lines.append(f"   Results: {tool_state.results_count} found")

        if tool_state.query_time:
            lines.append(f"   Query time: {tool_state.query_time:.2f}s")

        if tool_state.retrieval_time:
            lines.append(f"   Retrieval time: {tool_state.retrieval_time:.2f}s")

        lines.append("")

    # Show response text if available
    if state.final_text:
        lines.append("## Response\n")
        lines.append(state.final_text)

        # Show citations if available
        if state.citations:
            lines.append("\n## Citations\n")
            for citation in state.citations:
                lines.append(f"[{citation['id']}] {citation['filename']}")
                if citation.get("page"):
                    lines[-1] += f" (page {citation['page']})"

    return "\n".join(lines)


async def hello_file_search(
    query: str,
    tools: List[str],
    model: str = "qwen-max-latest",
    vec_ids: Optional[List[str]] = None,
    country: Optional[str] = None,
    city: Optional[str] = None,
    debug: bool = False,
):
    """
    Run a multi-tool search query using the typed API.

    Args:
        query: The search query
        tools: List of tools to use (file-search, web-search)
        model: Model to use
        vec_ids: Vector store IDs for file search
        country: Country for web search
        city: City for web search
        debug: Enable debug output
    """
    # Use default vectorstore IDs if none provided
    if not vec_ids:
        vec_ids = DEFAULT_VEC_IDS

    # Build tools list using typed API
    typed_tools = []

    if "file-search" in tools:
        # Validate vectorstore IDs
        for vec_id in vec_ids:
            vec_info = await async_get_vectorstore(vec_id)
            if vec_info:
                console.print(f"[green]✓[/green] Using vectorstore: {vec_info.get('name', vec_id)}")
            else:
                console.print(f"[yellow]⚠[/yellow] Warning: Could not fetch vectorstore {vec_id}")

        typed_tools.append(FileSearchTool(type="file_search", vector_store_ids=vec_ids, max_num_results=20))

    if "web-search" in tools:
        user_location = None
        if country or city:
            user_location = UserLocation(type="approximate", country=country, city=city)

        typed_tools.append(WebSearchTool(type="web_search", search_context_size="medium", user_location=user_location))

    # Create typed request
    request = create_typed_request(input_messages=query, model=model, tools=typed_tools, effort="low", store=True)

    # Initialize event handler
    event_handler = MultiToolEventHandler(debug=debug)

    # Create initial display
    with Live(console=console, refresh_per_second=4) as live:
        start_time = time.time()

        # Process streaming response with typed API
        async for event_type, response in astream_typed_response(request, debug=debug):
            if debug:
                console.print(f"[dim]Event: {event_type}[/dim]")

            # Handle tool events
            if event_handler.can_handle(event_type):
                update = event_handler.handle_event(event_type, response, query_time=time.time() - start_time)

                # Update display
                display_text = create_display_text(event_handler.state)
                live.update(Markdown(display_text))

            # Handle text output
            elif event_type == "response.output_text.delta" and response:
                if response.output_text:
                    event_handler.state.final_text = response.output_text
                    display_text = create_display_text(event_handler.state)
                    live.update(Markdown(display_text))

            # Handle completion
            elif event_type == "response.completed" and response:
                # Extract citations
                event_handler.state.citations = EventDataExtractor.extract_citations(response)

                # Final display update
                display_text = create_display_text(event_handler.state, is_final=True)
                live.update(Markdown(display_text))

            # Exit on done
            elif event_type == "done":
                break

        # Show final timing
        total_time = time.time() - start_time
        console.print(f"\n[dim]Total time: {total_time:.2f}s[/dim]")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Multi-tool search using Knowledge Forge SDK (Typed API)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # File search only
  %(prog)s -t file-search "What is machine learning?"
  
  # Web search only  
  %(prog)s -t web-search "Latest AI news"
  
  # Both tools
  %(prog)s -t file-search web-search "Compare internal docs with latest trends"
  
  # Custom vectorstore
  %(prog)s -t file-search --vec-id vs_abc123 "Find information about Python"
  
  # Web search with location
  %(prog)s -t web-search --country US --city "San Francisco" "Local tech events"
        """,
    )

    parser.add_argument(
        "query",
        nargs="?",
        default="What information is available about artificial intelligence and machine learning?",
        help="Search query (default: AI/ML query)",
    )

    parser.add_argument(
        "--tools",
        "-t",
        nargs="+",
        choices=["file-search", "web-search"],
        default=["file-search"],
        help="Tools to use (default: file-search)",
    )

    parser.add_argument(
        "--model",
        "-m",
        default="qwen-max-latest",
        help="Model to use (default: qwen-max-latest)",
    )

    parser.add_argument(
        "--vec-id",
        "--vector-store-id",
        dest="vec_ids",
        nargs="+",
        help=f"Vector store IDs (default: {DEFAULT_VEC_IDS})",
    )

    parser.add_argument(
        "--country",
        help="Country for web search location (e.g., US)",
    )

    parser.add_argument(
        "--city",
        help="City for web search location (e.g., San Francisco)",
    )

    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Show debug information",
    )

    args = parser.parse_args()

    # Print header
    console.print(
        Panel.fit(
            f"[bold]Multi-Tool Search with Typed API[/bold]\n"
            f"Query: {args.query}\n"
            f"Tools: {', '.join(args.tools)}\n"
            f"Model: {args.model}",
            border_style="blue",
        )
    )

    # Run the search
    try:
        asyncio.run(
            hello_file_search(
                query=args.query,
                tools=args.tools,
                model=args.model,
                vec_ids=args.vec_ids,
                country=args.country,
                city=args.city,
                debug=args.debug,
            )
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Search cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        if args.debug:
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    main()
