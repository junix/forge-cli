#!/usr/bin/env python3
"""
SSE JSON Viewer - Displays raw JSON events from the Knowledge Forge API.
This script focuses on clearly displaying each event's JSON data in a syntax-highlighted panel.
"""

import argparse
import asyncio
import json
from datetime import datetime

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from sdk import astream_response

console = Console()


async def main():
    parser = argparse.ArgumentParser(description="Knowledge Forge SSE JSON Viewer")
    parser.add_argument(
        "query",
        nargs="*",
        default=["Tell me about knowledge retrieval systems."],
        help="The query to send to the API",
    )
    parser.add_argument(
        "--model",
        "-m",
        default="qwen-max-latest",
        help="Model to use (default: qwen-max-latest)",
    )
    parser.add_argument(
        "--effort",
        "-e",
        default="low",
        choices=["low", "medium", "high", "dev"],
        help="Effort level (default: low)",
    )
    parser.add_argument(
        "--tokens",
        "-t",
        type=int,
        default=1000,
        help="Maximum output tokens (default: 1000)",
    )
    parser.add_argument(
        "--theme",
        default="monokai",
        choices=["monokai", "github-dark", "one-dark", "dracula", "solarized-dark"],
        help="Syntax highlighting theme (default: monokai)",
    )
    parser.add_argument(
        "--delay",
        "-d",
        type=float,
        default=1.0,
        help="Seconds to display each event (default: 1.0)",
    )

    args = parser.parse_args()
    query = " ".join(args.query)

    # Print startup info
    console.print("[bold magenta]Knowledge Forge SSE JSON Viewer[/bold magenta]")
    console.print(f"Query: [cyan]{query}[/cyan]")
    console.print(f"Model: [green]{args.model}[/green] | Effort: [green]{args.effort}[/green]")

    # Track event information
    event_count = 0
    events_with_data = 0
    start_time = datetime.now()

    # Main loop
    async for event_type, event_data in astream_response(
        input_messages=query,
        model=args.model,
        effort=args.effort,
        max_output_tokens=args.tokens,
    ):
        event_count += 1
        event_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        # Create event header
        header = Table.grid(padding=(0, 1))
        header.add_column(style="cyan", no_wrap=True)
        header.add_column(style="magenta")
        header.add_row("Event Type:", event_type)
        header.add_row("Time:", event_time)
        header.add_row("Count:", f"#{event_count}")

        console.print(header)

        # Display JSON data if available
        if event_data:
            events_with_data += 1
            try:
                json_str = json.dumps(event_data, indent=2, ensure_ascii=False)
                console.print(
                    Panel(
                        Syntax(json_str, "json", theme=args.theme, word_wrap=True),
                        border_style="blue",
                        title=f"Event Data: {event_type}",
                        width=min(console.width - 4, 120),
                    )
                )
            except Exception as e:
                console.print(f"[red]Error formatting JSON: {str(e)}[/red]")
                console.print(f"Raw data: {str(event_data)}")
        else:
            console.print(Panel("No data", border_style="red", title=f"Event: {event_type}"))

        # Add separator line
        console.print("─" * min(console.width - 4, 120), style="dim")

        # Wait before proceeding to next event
        await asyncio.sleep(args.delay)

        # Break on done event
        if event_type == "done":
            break

    # Print summary
    duration = (datetime.now() - start_time).total_seconds()
    console.print("\n[bold green]Session Summary:[/bold green]")

    summary = Table(box=box.ROUNDED)
    summary.add_column("Metric", style="cyan")
    summary.add_column("Value", style="green")

    summary.add_row("Total Events", str(event_count))
    summary.add_row("Events With Data", str(events_with_data))
    summary.add_row("Duration", f"{duration:.2f} seconds")
    summary.add_row("Events Per Second", f"{event_count / duration:.2f}")

    console.print(summary)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        import traceback

        traceback.print_exc()
