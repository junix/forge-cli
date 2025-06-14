#!/usr/bin/env python3
"""
Web search example using typed API.

This demonstrates using the typed API for web search operations
with proper type safety and Response objects.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from forge_cli.config import SearchConfig
from forge_cli.sdk import astream_typed_response
from forge_cli.models import Request, WebSearchTool
from forge_cli.response.adapters import MigrationHelper
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.markdown import Markdown


async def main():
    """Run web search example with typed API."""
    console = Console()
    
    # Example queries
    queries = [
        ("Latest developments in artificial intelligence", None, None),
        ("Weather forecast", "US", "San Francisco"),
        ("Local restaurants", "JP", "Tokyo"),
    ]
    
    for query, country, city in queries:
        console.print(f"\n[bold blue]🌐 Web Search:[/bold blue] {query}")
        if country or city:
            location = []
            if city:
                location.append(city)
            if country:
                location.append(country)
            console.print(f"[dim]📍 Location: {', '.join(location)}[/dim]")
        
        # Create request with web search tool
        tool_params = {"type": "web_search"}
        if country:
            tool_params["country"] = country
        if city:
            tool_params["city"] = city
            
        request = Request(
            input=[{"type": "text", "text": query}],
            model="qwen-max-latest",
            tools=[WebSearchTool(**tool_params)],
            temperature=0.7,
            max_output_tokens=1500,
        )
        
        # Stream response
        full_response = ""
        search_results = []
        
        with Live(Panel("Searching...", title="Web Search"), refresh_per_second=4) as live:
            try:
                async for event_type, event_data in astream_typed_response(request, debug=False):
                    if event_type == "response.web_search_call.searching":
                        live.update(Panel("🔍 Searching the web...", title="Web Search"))
                    
                    elif event_type == "response.web_search_call.completed" and event_data:
                        # Extract search results using safe methods
                        output_items = MigrationHelper.safe_get_output_items(event_data)
                        for item in output_items:
                            if MigrationHelper.is_typed_item(item):
                                if hasattr(item, 'type') and 'web_search' in str(item.type):
                                    if hasattr(item, 'results'):
                                        search_results.extend(item.results)
                            elif isinstance(item, dict) and 'web_search' in item.get('type', ''):
                                results = item.get('results', [])
                                search_results.extend(results)
                        
                        result_count = len(search_results)
                        live.update(Panel(f"✅ Found {result_count} results", title="Web Search"))
                    
                    elif event_type == "response.output_text.delta":
                        text = MigrationHelper.safe_get_text(event_data)
                        if text:
                            full_response += text
                            live.update(Panel(Markdown(full_response), title="Response"))
                    
                    elif event_type == "done":
                        break
                        
            except KeyboardInterrupt:
                console.print("\n[yellow]Search interrupted[/yellow]")
                break
            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]")
                import traceback
                traceback.print_exc()
        
        # Show search results summary
        if search_results:
            console.print(f"\n[bold]Search Results ({len(search_results)}):[/bold]")
            for i, result in enumerate(search_results[:5], 1):
                if hasattr(result, 'title') and hasattr(result, 'url'):
                    # Typed result
                    console.print(f"{i}. [blue]{result.title}[/blue]")
                    console.print(f"   [dim]{result.url}[/dim]")
                    if hasattr(result, 'snippet') and result.snippet:
                        console.print(f"   {result.snippet[:100]}...")
                elif isinstance(result, dict):
                    # Dict result
                    console.print(f"{i}. [blue]{result.get('title', 'Untitled')}[/blue]")
                    console.print(f"   [dim]{result.get('url', '')}[/dim]")
                    snippet = result.get('snippet', '')
                    if snippet:
                        console.print(f"   {snippet[:100]}...")
                console.print()


if __name__ == "__main__":
    asyncio.run(main())