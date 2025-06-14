#!/usr/bin/env python3
"""
Multi-tool example using the Knowledge Forge SDK.

This script demonstrates how to use multiple tools together in the same request,
enabling complex workflows that combine information from different sources.

Features:
- Combined file search and web search in a single request
- Multiple approaches: research assistant, fact checker, comprehensive Q&A
- Different tool configurations and effort levels
- Rich output formatting with tool-specific results display
- Streaming support with real-time updates
"""

import argparse
import asyncio
import json
import os
import sys
import time
from enum import Enum
from pathlib import Path
from typing import Any

# Rich library for better terminal output
try:
    from rich import print as rich_print
    from rich.columns import Columns
    from rich.console import Console
    from rich.live import Live
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# Add the current directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

# Import SDK functions
try:
    from sdk import astream_response, async_get_vectorstore
except ImportError as e:
    print(f"Error importing SDK: {e}")
    print("Please ensure the SDK module is available and dependencies are installed.")
    sys.exit(1)

# Color support
try:
    import colorama
    from colorama import Fore, Style

    colorama.init()
    HAS_COLORS = True
except ImportError:
    HAS_COLORS = False

    class MockColor:
        def __getattr__(self, name):
            return ""

    Fore = Style = MockColor()


class ToolType(Enum):
    """Types of tools available."""

    FILE_SEARCH = "file_search"
    WEB_SEARCH = "web_search"


class MultiToolMode(Enum):
    """Different modes for multi-tool usage."""

    RESEARCH = "research"  # Research assistant mode
    FACT_CHECK = "fact_check"  # Fact checking mode
    COMPREHENSIVE = "comprehensive"  # Comprehensive Q&A mode
    CUSTOM = "custom"  # Custom tool configuration


class ToolEventTracker:
    """Tracks events from multiple tools."""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.file_search_queries = []
        self.file_search_results = 0
        self.web_search_queries = []
        self.web_search_results = 0
        self.tool_sequence = []  # Track order of tool usage
        self.current_tool = None

    def process_event(self, event_type: str, event_data: dict[str, Any]):
        """Process tool-related events."""
        # File search events
        if "file_search" in event_type:
            if event_type in ["response.file_search_call.searching", "response.file_search_call.in_progress"]:
                queries = self._extract_queries(event_data, "file_search")
                if queries:
                    self.file_search_queries.extend(queries)
                    if self.current_tool != ToolType.FILE_SEARCH:
                        self.tool_sequence.append(ToolType.FILE_SEARCH)
                        self.current_tool = ToolType.FILE_SEARCH

            elif event_type == "response.file_search_call.completed":
                count = self._extract_results_count(event_data, "file_search")
                if count is not None:
                    self.file_search_results = count

        # Web search events
        elif "web_search" in event_type:
            if event_type in ["response.web_search_call.searching", "response.web_search_call.in_progress"]:
                queries = self._extract_queries(event_data, "web_search")
                if queries:
                    self.web_search_queries = queries  # Web search typically has one query
                    if self.current_tool != ToolType.WEB_SEARCH:
                        self.tool_sequence.append(ToolType.WEB_SEARCH)
                        self.current_tool = ToolType.WEB_SEARCH

            elif event_type == "response.web_search_call.completed":
                count = self._extract_results_count(event_data, "web_search")
                if count is not None:
                    self.web_search_results = count

    def _extract_queries(self, event_data: dict[str, Any], tool_type: str) -> list[str]:
        """Extract queries from event data."""
        if not isinstance(event_data, dict):
            return []

        # Direct location
        if "queries" in event_data:
            return event_data.get("queries", [])

        # In tool-specific call
        call_key = f"{tool_type}_call"
        if call_key in event_data:
            return event_data[call_key].get("queries", [])

        # In output array
        if "output" in event_data:
            for item in event_data.get("output", []):
                if item.get("type") == call_key and "queries" in item:
                    return item.get("queries", [])

        return []

    def _extract_results_count(self, event_data: dict[str, Any], tool_type: str) -> int | None:
        """Extract results count from event data."""
        if not isinstance(event_data, dict):
            return None

        # Check various locations for results
        if "results" in event_data and isinstance(event_data["results"], list):
            return len(event_data["results"])

        call_key = f"{tool_type}_call"
        if call_key in event_data and "results" in event_data[call_key]:
            results = event_data[call_key]["results"]
            if isinstance(results, list):
                return len(results)

        # Check in output array
        if "output" in event_data:
            for item in event_data.get("output", []):
                if item.get("type") == call_key and "results" in item:
                    results = item.get("results")
                    if isinstance(results, list):
                        return len(results)

        return None

    def get_summary(self) -> dict[str, Any]:
        """Get summary of tool usage."""
        return {
            "tool_sequence": [tool.value for tool in self.tool_sequence],
            "file_search": {"queries": self.file_search_queries, "results_count": self.file_search_results},
            "web_search": {"queries": self.web_search_queries, "results_count": self.web_search_results},
        }


def format_tool_summary_display(tool_tracker: ToolEventTracker, use_rich: bool = True) -> str:
    """Format tool usage summary for display."""
    summary = tool_tracker.get_summary()

    if use_rich and HAS_RICH:
        # Create a table for tool usage
        table = Table(title="🛠️ Tool Usage Summary", title_style="bold cyan")
        table.add_column("Tool", style="cyan", no_wrap=True)
        table.add_column("Queries", style="yellow")
        table.add_column("Results", style="green")

        # File search row
        if summary["file_search"]["queries"]:
            fs_queries = "\n".join(summary["file_search"]["queries"])
            table.add_row("📚 File Search", fs_queries, str(summary["file_search"]["results_count"]))

        # Web search row
        if summary["web_search"]["queries"]:
            ws_queries = "\n".join(summary["web_search"]["queries"])
            table.add_row("🌐 Web Search", ws_queries, str(summary["web_search"]["results_count"]))

        # Tool sequence
        if summary["tool_sequence"]:
            sequence_text = " → ".join(["📚" if t == "file_search" else "🌐" for t in summary["tool_sequence"]])
            table.add_row("⚡ Sequence", sequence_text, "-")

        return table
    else:
        # Plain text format
        lines = ["\n🛠️ Tool Usage Summary:"]

        if summary["file_search"]["queries"]:
            lines.append("\n📚 File Search:")
            for q in summary["file_search"]["queries"]:
                lines.append(f"   Query: {q}")
            lines.append(f"   Results: {summary['file_search']['results_count']}")

        if summary["web_search"]["queries"]:
            lines.append("\n🌐 Web Search:")
            for q in summary["web_search"]["queries"]:
                lines.append(f"   Query: {q}")
            lines.append(f"   Results: {summary['web_search']['results_count']}")

        if summary["tool_sequence"]:
            sequence = " → ".join(
                ["File Search" if t == "file_search" else "Web Search" for t in summary["tool_sequence"]]
            )
            lines.append(f"\n⚡ Tool Sequence: {sequence}")

        return "\n".join(lines)


def create_tools_config(
    mode: MultiToolMode,
    vec_ids: list[str] | None = None,
    location: dict[str, str] | None = None,
    max_file_results: int = 10,
    max_web_results: int = 5,
    search_context_size: str | None = None,
) -> list[dict[str, Any]]:
    """Create tools configuration based on the mode."""
    tools = []

    if mode == MultiToolMode.RESEARCH:
        # Research mode: Use both tools with balanced settings
        if vec_ids:
            tools.append({"type": "file_search", "vector_store_ids": vec_ids, "max_num_results": max_file_results})

        web_tool = {"type": "web_search"}
        if search_context_size:
            web_tool["search_context_size"] = search_context_size
        if location:
            web_tool["user_location"] = {"type": "approximate", **location}
        tools.append(web_tool)

    elif mode == MultiToolMode.FACT_CHECK:
        # Fact check mode: Prioritize accuracy with more results
        if vec_ids:
            tools.append(
                {
                    "type": "file_search",
                    "vector_store_ids": vec_ids,
                    "max_num_results": max_file_results * 2,  # More results for verification
                }
            )

        web_tool = {
            "type": "web_search",
            "search_context_size": "high",  # More context for fact checking
        }
        if location:
            web_tool["user_location"] = {"type": "approximate", **location}
        tools.append(web_tool)

    elif mode == MultiToolMode.COMPREHENSIVE:
        # Comprehensive mode: Maximum information gathering
        if vec_ids:
            tools.append({"type": "file_search", "vector_store_ids": vec_ids, "max_num_results": max_file_results * 3})

        web_tool = {"type": "web_search", "search_context_size": "high"}
        if location:
            web_tool["user_location"] = {"type": "approximate", **location}
        tools.append(web_tool)

    return tools


async def process_multi_tool_request(
    question: str,
    mode: MultiToolMode = MultiToolMode.RESEARCH,
    vec_ids: list[str] | None = None,
    location: dict[str, str] | None = None,
    model: str = "qwen-max-latest",
    effort: str = "medium",
    max_file_results: int = 10,
    max_web_results: int = 5,
    search_context_size: str | None = None,
    debug: bool = False,
    no_color: bool = False,
    json_output: bool = False,
) -> dict[str, Any] | None:
    """Process a request using multiple tools."""
    start_time = time.time()

    # Create tools configuration
    tools = create_tools_config(mode, vec_ids, location, max_file_results, max_web_results, search_context_size)

    if not tools:
        print("❌ No tools configured. Please provide vector store IDs or enable web search.")
        return None

    # Create input messages
    input_messages = [
        {
            "role": "user",
            "id": "user_message_1",
            "content": question,
        }
    ]

    # Setup display
    use_rich = HAS_RICH and not no_color and not json_output
    console = Console() if use_rich else None

    # Print request information
    if not json_output:
        if use_rich:
            request_info = Text()
            request_info.append("📋 Multi-Tool Request\n", style="bold cyan")
            request_info.append("  Mode: ", style="green")
            request_info.append(f"{mode.value}\n", style="yellow")
            request_info.append("  Question: ", style="green")
            request_info.append(f"{question}\n")
            request_info.append("  Model: ", style="green")
            request_info.append(f"{model}\n")
            request_info.append("  Effort: ", style="green")
            request_info.append(f"{effort}\n")
            request_info.append("  Tools: ", style="green")
            tool_names = []
            for tool in tools:
                if tool["type"] == "file_search":
                    tool_names.append(f"📚 File Search ({len(tool['vector_store_ids'])} stores)")
                elif tool["type"] == "web_search":
                    tool_names.append("🌐 Web Search")
            request_info.append(", ".join(tool_names) + "\n")

            console.print(Panel(request_info, title="Request Configuration", border_style="blue"))
        else:
            print("\n📋 Multi-Tool Request")
            print(f"  Mode: {mode.value}")
            print(f"  Question: {question}")
            print(f"  Model: {model}")
            print(f"  Effort: {effort}")
            tool_names = []
            for tool in tools:
                if tool["type"] == "file_search":
                    tool_names.append(f"File Search ({len(tool['vector_store_ids'])} stores)")
                elif tool["type"] == "web_search":
                    tool_names.append("Web Search")
            print(f"  Tools: {', '.join(tool_names)}")
            print("=" * 80)

    # Initialize tool event tracker
    tool_tracker = ToolEventTracker(debug=debug)

    # Variables for tracking response
    final_response = None
    current_text = ""
    usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

    # Setup live display if using rich
    if use_rich:
        live_display = Live(
            Panel("Initializing...", title="Multi-Tool Response", border_style="green"),
            refresh_per_second=10,
            console=console,
            transient=False,
        )
        live_display.start()
    else:
        live_display = None

    try:
        # Process streaming response
        async for event_type, event_data in astream_response(
            input_messages=input_messages,
            model=model,
            effort=effort,
            store=True,
            tools=tools,
            debug=debug,
        ):
            # Track tool events
            if event_type and event_data:
                tool_tracker.process_event(event_type, event_data)

            # Update usage if available
            if event_data and isinstance(event_data, dict) and "usage" in event_data:
                usage.update(event_data.get("usage", {}))

            # Debug output
            if debug and not json_output:
                print(f"\nDEBUG: Event: {event_type}")
                if event_data:
                    print(f"DEBUG: Data: {json.dumps(event_data, indent=2, ensure_ascii=False)}")

            # Process text content
            if event_data and "output" in event_data:
                for output_item in event_data.get("output", []):
                    if output_item.get("type") == "message" and output_item.get("role") == "assistant":
                        for content_item in output_item.get("content", []):
                            if content_item.get("type") == "output_text":
                                current_text = content_item.get("text", "")

            # Update display in rich mode
            if use_rich and live_display:
                # Create content panels
                panels = []

                # Tool usage panel
                tool_summary = format_tool_summary_display(tool_tracker, use_rich=True)
                if isinstance(tool_summary, Table):
                    panels.append(tool_summary)

                # Current response text
                if current_text:
                    try:
                        panels.append(Panel(Markdown(current_text), title="💬 Response", border_style="cyan"))
                    except:
                        panels.append(Panel(Text(current_text), title="💬 Response", border_style="cyan"))

                # Usage stats
                usage_text = Text()
                usage_text.append("📊 Usage: ", style="yellow")
                usage_text.append(f"↑{usage['input_tokens']} ", style="blue")
                usage_text.append(f"↓{usage['output_tokens']} ", style="magenta")
                usage_text.append(f"∑{usage['total_tokens']}", style="green")

                # Combine panels
                if panels:
                    live_display.update(
                        Panel(
                            Columns(panels, equal=False, expand=True),
                            title="Multi-Tool Response",
                            subtitle=usage_text,
                            border_style="green",
                        )
                    )

            # Handle text deltas in non-rich mode
            elif event_type == "response.output_text.delta" and event_data and not use_rich:
                if "text" in event_data:
                    text = event_data["text"]
                    if isinstance(text, str):
                        print(text, end="", flush=True)

            # Check for completion
            if event_type == "done":
                final_response = event_data
                break

        # Stop live display
        if use_rich and live_display:
            live_display.stop()

        # Calculate duration
        duration = time.time() - start_time

        # Handle final output
        if final_response:
            if json_output:
                # Add tool usage summary to JSON output
                final_response["tool_usage_summary"] = tool_tracker.get_summary()
                print(json.dumps(final_response, indent=2, ensure_ascii=False))
            else:
                # Display completion info
                if use_rich:
                    completion_info = Text()
                    completion_info.append("\n✅ Multi-tool response completed!\n", style="green bold")
                    completion_info.append("  Response ID: ", style="yellow")
                    completion_info.append(f"{final_response.get('id')}\n")
                    completion_info.append("  Duration: ", style="yellow")
                    completion_info.append(f"{duration:.2f}s\n")

                    console.print(completion_info)

                    # Show final tool summary
                    console.print(format_tool_summary_display(tool_tracker, use_rich=True))
                else:
                    print("\n\n✅ Multi-tool response completed!")
                    print(f"  Response ID: {final_response.get('id')}")
                    print(f"  Duration: {duration:.2f}s")
                    print(format_tool_summary_display(tool_tracker, use_rich=False))

            return final_response

    except Exception as e:
        if live_display:
            live_display.stop()

        if not json_output:
            error_msg = f"❌ Error during multi-tool request: {e}"
            if use_rich:
                console.print(Text(error_msg, style="red bold"))
            else:
                print(f"\n{error_msg}")
        return None


async def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Multi-tool example for Knowledge Forge API",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Mode selection
    parser.add_argument(
        "--mode",
        "-m",
        type=str,
        choices=["research", "fact_check", "comprehensive", "custom"],
        default="research",
        help="Mode of operation for multi-tool usage",
    )

    # Question
    parser.add_argument(
        "--question",
        "-q",
        type=str,
        default="What are the latest developments in AI and how do they compare to existing research?",
        help="Question to ask using multiple tools",
    )

    # Vector store IDs
    parser.add_argument("--vec-id", action="append", help="Vector store ID(s) for file search (can specify multiple)")

    # Web search configuration
    parser.add_argument(
        "--search-context", choices=["low", "medium", "high"], help="Search context size for web search"
    )
    parser.add_argument("--country", type=str, help="Two-letter ISO country code for web search")
    parser.add_argument("--city", type=str, help="City for web search location")

    # Model configuration
    parser.add_argument("--model", type=str, default="qwen-max-latest", help="Model to use for the response")
    parser.add_argument(
        "--effort",
        "-e",
        type=str,
        choices=["low", "medium", "high", "dev"],
        default="low",
        help="Effort level for the response",
    )

    # Search limits
    parser.add_argument("--max-file-results", type=int, default=10, help="Maximum file search results per vector store")
    parser.add_argument("--max-web-results", type=int, default=5, help="Maximum web search results")

    # Display options
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug output")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Server configuration
    parser.add_argument(
        "--server", default=os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999"), help="Server URL"
    )

    args = parser.parse_args()

    # Set server URL
    if args.server:
        os.environ["KNOWLEDGE_FORGE_URL"] = args.server

    # Create location dict if provided
    location = None
    if args.country or args.city:
        location = {}
        if args.country:
            location["country"] = args.country
        if args.city:
            location["city"] = args.city

    # Convert mode string to enum
    mode = MultiToolMode(args.mode)

    # Run the multi-tool request
    response = await process_multi_tool_request(
        question=args.question,
        mode=mode,
        vec_ids=args.vec_id,
        location=location,
        model=args.model,
        effort=args.effort,
        max_file_results=args.max_file_results,
        max_web_results=args.max_web_results,
        search_context_size=args.search_context,
        debug=args.debug,
        no_color=args.no_color,
        json_output=args.json,
    )

    if not response and not args.json:
        print("\n❌ Failed to get response")
        sys.exit(1)


def example_usage():
    """Show example usage commands."""
    examples = """
Example Usage:

1. Research Mode (default) - Balanced search across documents and web:
   python hello-multi-tools.py -q "What are recent AI breakthroughs?" --vec-id vec123

2. Fact Checking Mode - Verify information across sources:
   python hello-multi-tools.py --mode fact_check -q "Is GPT-4 really multimodal?" --vec-id vec123 --vec-id vec456

3. Comprehensive Mode - Maximum information gathering:
   python hello-multi-tools.py --mode comprehensive -q "Explain quantum computing" --max-file-results 20 --max-web-results 10

4. Custom Mode with Location - Web search with location context:
   python hello-multi-tools.py --mode custom -q "Local AI events" --country US --city "San Francisco"

5. Multiple Vector Stores + Web Search:
   python hello-multi-tools.py --vec-id store1 --vec-id store2 --search-context high

6. JSON Output for Integration:
   python hello-multi-tools.py -q "AI safety research" --json --vec-id vec123

7. High Effort with Debug:
   python hello-multi-tools.py --effort high --debug -q "Compare transformer architectures"
    """
    print(examples)


if __name__ == "__main__":
    # Check if showing examples
    if len(sys.argv) == 1 or "--examples" in sys.argv:
        example_usage()
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\n\nOperation cancelled.")
        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
            if "--debug" in sys.argv or "-d" in sys.argv:
                import traceback

                traceback.print_exc()
            sys.exit(1)
