#!/usr/bin/env python3
#!/usr/bin/env python3
"""
Simple SSE client that displays raw JSON events from the Knowledge Forge API.
"""

import argparse
import asyncio
import json
from datetime import datetime

from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.syntax import Syntax
from rich.table import Table
from sdk import astream_response  # 自己的 SDK

console = Console()


def make_status_renderable(status: str, event_count: int, is_done: bool) -> Panel:
    """Constructs a Rich Panel for the status bar.

    The status bar displays the current status message, event count, and a
    spinner or completion indicator.

    Args:
        status: The current status message to display.
        event_count: The number of events processed so far.
        is_done: Boolean indicating if the SSE stream has completed.

    Returns:
        A Rich Panel object representing the status bar.
    """
    if is_done:
        return Align.center(
            Panel(
                f"[bold green]✓ Response complete — {event_count} events processed[/bold green]",
                border_style="green",
                width=min(console.width - 4, 120),
            )
        )

    table = Table.grid(expand=True, padding=(0, 1))
    table.add_column(no_wrap=True)
    table.add_column()
    table.add_row(Spinner("dots"), f"[bold cyan]{status} — Event #{event_count}[/bold cyan]")

    return Align.center(
        Panel(table, border_style="cyan", width=min(console.width - 4, 120)),
    )


def make_event_panel(
    event_type: str | None,
    event_data: dict | None,
    timestamp: str | None,
    color_scheme: str,
) -> Panel | None:
    """Constructs a Rich Panel to display an individual SSE event.

    The panel includes the event type, timestamp, and a syntax-highlighted
    JSON representation of the event data.

    Args:
        event_type: The type of the SSE event (e.g., "message", "done").
        event_data: A dictionary containing the data payload of the event.
        timestamp: A string representing the time the event was received.
        color_scheme: The Rich color scheme to use for JSON syntax highlighting.

    Returns:
        A Rich Panel object for the event, or None if event_type is None.
    """
    if not event_type:
        return None

    title = f"Event: {event_type}"
    if timestamp:
        title += f" ({timestamp})"

    if event_data:
        json_str = json.dumps(event_data, indent=2, ensure_ascii=False)
        body = Syntax(json_str, "json", theme=color_scheme, word_wrap=True)
    else:
        body = "No data"

    return Panel(
        body,
        title=title,
        border_style="blue",
        width=min(console.width - 4, 120),
    )


async def main() -> None:
    """Main asynchronous function to run the SSE client.

    Parses command-line arguments, connects to the Knowledge Forge API,
    processes SSE events, and displays them in a Rich Live view.
    """
    # ---------- CLI ----------
    parser = argparse.ArgumentParser(description="Test the astream_response API with JSON display")
    parser.add_argument(
        "query",
        nargs="*",
        default=["Tell me about knowledge retrieval systems. Keep it brief."],
        help="The query to send to the API",
    )
    parser.add_argument("--model", "-m", default="qwen-max-latest", help="Model to use")
    parser.add_argument(
        "--effort",
        "-e",
        default="low",
        choices=["low", "medium", "high", "dev"],
        help="Effort level",
    )
    parser.add_argument(
        "--tokens",
        "-t",
        type=int,
        default=1000,
        help="Maximum output tokens (default: 1000)",
    )
    parser.add_argument(
        "--color-scheme",
        default="monokai",
        choices=["monokai", "github-dark", "one-dark", "dracula", "solarized-dark"],
        help="Syntax highlighting color scheme for JSON",
    )
    args = parser.parse_args()
    query = " ".join(args.query)

    # ---------- Banner ----------
    console.print(Align.center("[bold]Knowledge Forge SSE JSON Client[/bold]"))
    console.print(Align.center(f"Query: [cyan]{query}[/cyan]"))
    console.print(Align.center(f"Model: [green]{args.model}[/green], Effort: [green]{args.effort}[/green]"))
    console.print(Align.center("Displaying raw JSON events with syntax highlighting...\n"))

    # ---------- State ----------
    event_count = 0
    is_done = False
    status_msg = "Starting..."
    current_event_type: str | None = None
    current_event_data: dict | None = None
    current_event_time: str | None = None

    # ---------- Render callback ----------
    def render() -> Group:
        """Renders the current state of the UI as a Rich Group.

        This function is called by the Rich Live display to update the terminal output.
        It combines the status bar and the current event panel.

        Returns:
            A Rich Group object containing all UI components.
        """
        components: list = [
            make_status_renderable(status_msg, event_count, is_done),
        ]

        event_panel = make_event_panel(
            current_event_type,
            current_event_data,
            current_event_time,
            args.color_scheme,
        )
        if event_panel:
            components.append(Align.center(event_panel))

        return Group(*components)

    # ---------- Live view ----------
    with Live(render(), console=console, refresh_per_second=10) as live:
        async for ev_type, ev_data in astream_response(
            input_messages=query,
            model=args.model,
            effort=args.effort,
            max_output_tokens=args.tokens,
        ):
            # 更新状态
            event_count += 1
            status_msg = f"Received event: {ev_type}"
            current_event_type = ev_type
            if ev_data is not None and ev_data != "no data":
                current_event_data = ev_data
            current_event_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]

            if ev_type == "done":
                is_done = True
                status_msg = "Complete"

            live.update(render())
            await asyncio.sleep(0.5)  # 纯展示需要，可按需调整

        await asyncio.sleep(2)  # 停留片刻让用户看清结果

    # ---------- Summary ----------
    console.print("\n[green]Response completed successfully[/green]")
    console.print(f"[blue]Total events: {event_count}[/blue]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
    except Exception as exc:  # pragma: no cover
        console.print(f"\n[red]Error: {exc}[/red]")
        import traceback

        traceback.print_exc()
