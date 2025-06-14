#!/usr/bin/env python3
import argparse
import json
import os
from typing import Any

import requests
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Initialize Rich console
console = Console()

# Use environment variable for server URL if available, otherwise default to localhost
default_url = os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999")


def query_vector_store(
    vector_store_id: str,
    query: str,
    top_k: int = 10,
    filters: dict[str, Any] | None = None,
    server_url: str = default_url,
):
    """Query a vector store for documents matching the given query.

    Args:
        vector_store_id (str): ID of the vector store to query.
        query (str): The search query text.
        top_k (int, optional): Number of results to return. Defaults to 10.
        filters (dict, optional): Optional filters to apply to the search.
        server_url (str, optional): Server URL. Defaults to environment variable or localhost.

    Returns:
        dict or None: The server response if successful, None otherwise.
    """
    try:
        # Construct the URL for the POST request
        url = f"{server_url}/v1/vector_stores/{vector_store_id}/search"

        # Check if using default vector store ID
        if vector_store_id == "a1b2c3d4-e5f6-7890-abcd-ef1234567890":
            console.print(f"Querying default vector store with: '[bold cyan]{query}[/]'")
        else:
            console.print(f"Querying vector store '[bold green]{vector_store_id}[/]' with: '[bold cyan]{query}[/]'")

        # Prepare request payload
        payload = {"query": query, "top_k": top_k}

        # Add optional filters if provided
        if filters:
            payload["filters"] = filters

        # Send the POST request
        response = requests.post(url, json=payload)

        # Check if the request was successful
        response.raise_for_status()

        # Get the response data
        response_data = response.json()

        # Create a header panel for the search results
        console.print()
        console.print(
            Panel(
                f"[bold]Search query:[/] [cyan]{response_data['search_query']}[/]\n"
                f"[bold]Found:[/] [green]{len(response_data['data'])}[/] results",
                title="[bold]Knowledge Forge Search Results[/]",
                border_style="blue",
            )
        )

        # Print each result with its score and content
        for i, result in enumerate(response_data["data"], 1):
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
            result_table.add_row("Score", f"[yellow]{result['score']:.4f}[/]")
            result_table.add_row(
                "File",
                f"[green]{result['filename']}[/] (ID: [dim]{result['file_id']}[/])",
            )

            # Add attributes if any
            if result["attributes"]:
                attr_text = Text()
                for key, value in result["attributes"].items():
                    attr_text.append(f"{key}: ", style="cyan")
                    attr_text.append(f"{json.dumps(value)}\n", style="yellow")
                result_table.add_row("Attributes", attr_text)

            # Add content
            for content_item in result["content"]:
                if content_item["type"] == "text":
                    # Format the text content for better readability
                    text = content_item["text"].strip()
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

        return response_data

    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error during vector store query:[/] {e}")
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                console.print(
                    Panel(
                        json.dumps(error_data, indent=2),
                        title="[bold red]Server Error Details[/]",
                        border_style="red",
                    )
                )
            except json.JSONDecodeError:
                console.print(
                    Panel(
                        e.response.text[:500],  # Limit long responses
                        title="[bold red]Server Error Response (non-JSON)[/]",
                        border_style="red",
                    )
                )
        return None


if __name__ == "__main__":
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

    # Server URL option
    parser.add_argument(
        "--server",
        default=default_url,
        help=f"Server URL (default: {default_url})",
    )

    # Parse arguments
    args = parser.parse_args()

    # Query the vector store
    query_vector_store(args.vec_id, args.query, args.top_k, server_url=args.server)
