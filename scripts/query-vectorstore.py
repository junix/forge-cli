#!/usr/bin/env python3
import argparse
import asyncio
import json
from typing import Any

from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Import SDK functions
from forge_cli.sdk import async_query_vectorstore

# Initialize Rich console
console = Console()


async def query_vector_store(
    vector_store_id: str,
    query: str,
    top_k: int = 10,
    filters: dict[str, Any] | None = None,
):
    """Query a vector store for documents matching the given query using SDK.

    Args:
        vector_store_id (str): ID of the vector store to query.
        query (str): The search query text.
        top_k (int, optional): Number of results to return. Defaults to 10.
        filters (dict, optional): Optional filters to apply to the search.

    Returns:
        dict or None: The server response if successful, None otherwise.
    """
    try:
        # Check if using default vector store ID
        if vector_store_id == "a1b2c3d4-e5f6-7890-abcd-ef1234567890":
            console.print(f"Querying default vector store with: '[bold cyan]{query}[/]'")
        else:
            console.print(f"Querying vector store '[bold green]{vector_store_id}[/]' with: '[bold cyan]{query}[/]'")

        # Call the SDK function to query the vector store
        result = await async_query_vectorstore(
            vector_store_id=vector_store_id,
            query=query,
            top_k=top_k,
            filters=filters,
        )

        if not result:
            console.print("[bold red]Failed to query vector store.[/]")
            return None

        # Create a header panel for the search results
        console.print()
        console.print(
            Panel(
                f"[bold]Search query:[/] [cyan]{result.search_query}[/]\n"
                f"[bold]Found:[/] [green]{len(result.data)}[/] results",
                title="[bold]Knowledge Forge Search Results[/]",
                border_style="blue",
            )
        )

        # Print each result with its score and content
        for i, search_result in enumerate(result.data, 1):
            # Create a table for each result
            result_table = Table(
                show_header=False,
                box=box.ROUNDED,
                title=f"[bold]Result #{i}[/]",
                title_style="bold magenta",
                border_style="dim",
                expand=True,
            )

            result_table.add_column("Property", style="bold blue", width=12)
            result_table.add_column("Value", style="white")

            # Add score and file info
            result_table.add_row("Score", f"[yellow]{search_result.score:.4f}[/]")
            result_table.add_row(
                "File",
                f"[green]{search_result.filename}[/] (ID: [dim]{search_result.file_id}[/])",
            )

            # Add attributes if any
            if search_result.attributes:
                attr_text = Text()
                for key, value in search_result.attributes.items():
                    attr_text.append(f"{key}: ", style="cyan")
                    attr_text.append(f"{json.dumps(value)}\n", style="yellow")
                result_table.add_row("Attributes", attr_text)

            # Add content
            for content_item in search_result.content:
                if content_item.type == "text":
                    # Format the text content for better readability
                    text = content_item.text.strip()
                    # Truncate long text for display
                    if len(text) > 500:
                        text = text[:500] + "..."

                    # Try to detect if content is markdown and render it accordingly
                    if "```" in text or "##" in text or "*" in text:
                        try:
                            content_display = Markdown(text)
                        except Exception:
                            content_display = Text(text)
                    else:
                        content_display = Text(text)

                    result_table.add_row("Content", content_display)

            console.print(result_table)
            console.print()  # Add spacing between results

        return result.model_dump()

    except Exception as e:
        console.print(f"[bold red]Error during vector store query:[/] {e}")
        return None


async def main():
    """Main async function to handle the query."""
    parser = argparse.ArgumentParser(description="Knowledge Forge Vector Store Query Tool")

    # Vector store query arguments
    parser.add_argument("-q", "--query", required=True, help="Search query text")
    parser.add_argument(
        "--vec-id",
        default="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        help="ID of the vector store to query (default: a1b2c3d4-e5f6-7890-abcd-ef1234567890)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="Number of results to return (default: 10)",
    )

    # Parse arguments
    args = parser.parse_args()

    # Query the vector store
    await query_vector_store(args.vec_id, args.query, args.top_k)


if __name__ == "__main__":
    asyncio.run(main())
