#!/usr/bin/env python3
"""
Simple end-to-end workflow using typed API.

This demonstrates a complete workflow:
1. Upload a file
2. Create a vector store
3. Query the vector store
4. Stream response with file search

All using the typed API for better type safety.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from forge_cli.sdk import (
    async_upload_file,
    async_create_vectorstore,
    async_wait_for_task_completion,
    astream_typed_response,
)
from forge_cli.models import Request, FileSearchTool
from forge_cli.response.adapters import MigrationHelper
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn


async def upload_file_with_progress(file_path: str, console: Console) -> Optional[str]:
    """Upload a file and wait for processing."""
    console.print(f"\n[bold blue]📤 Uploading file:[/bold blue] {file_path}")

    try:
        # Upload file
        result = await async_upload_file(file_path, purpose="general")

        if "error" in result:
            console.print(f"[red]Error: {result['error']}[/red]")
            return None

        file_id = result.get("file_id")
        task_id = result.get("task_id")

        console.print(f"✅ File uploaded: {file_id}")

        # Wait for processing if needed
        if task_id:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Processing file...", total=None)

                status = await async_wait_for_task_completion(
                    task_id,
                    poll_interval=2,
                    max_attempts=60,
                )

                progress.update(task, completed=True)

            if status.get("status") == "completed":
                console.print("✅ File processing completed")
            else:
                console.print(f"[yellow]File processing status: {status.get('status')}[/yellow]")

        return file_id

    except Exception as e:
        console.print(f"[red]Upload error: {e}[/red]")
        return None


async def create_vectorstore_with_file(file_id: str, name: str, console: Console) -> Optional[str]:
    """Create a vector store with the uploaded file."""
    console.print(f"\n[bold blue]🗄️  Creating vector store:[/bold blue] {name}")

    try:
        result = await async_create_vectorstore(
            name=name,
            description=f"Vector store for {name}",
            file_ids=[file_id],
        )

        if "error" in result:
            console.print(f"[red]Error: {result['error']}[/red]")
            return None

        vector_store_id = result.get("vector_store_id")
        console.print(f"✅ Vector store created: {vector_store_id}")

        return vector_store_id

    except Exception as e:
        console.print(f"[red]Vector store error: {e}[/red]")
        return None


async def query_with_typed_api(query: str, vector_store_id: str, console: Console) -> None:
    """Query using typed API with file search."""
    console.print(f"\n[bold blue]🔍 Querying:[/bold blue] {query}")

    # Create request with file search tool
    request = Request(
        input=[{"type": "text", "text": query}],
        model="qwen-max-latest",
        tools=[
            FileSearchTool(
                type="file_search",
                vector_store_ids=[vector_store_id],
                max_num_results=5,
            )
        ],
        temperature=0.7,
        max_output_tokens=2000,
    )

    # Track response
    full_response = ""
    citations = []
    search_completed = False

    try:
        async for event_type, event_data in astream_typed_response(request, debug=False):
            if event_type == "response.file_search_call.searching":
                console.print("[dim]🔍 Searching documents...[/dim]")

            elif event_type == "response.file_search_call.completed":
                search_completed = True
                console.print("[dim]✅ Search completed[/dim]")

            elif event_type == "response.output_text.delta":
                text = MigrationHelper.safe_get_text(event_data)
                if text:
                    full_response += text
                    # Print text as it streams
                    console.print(text, end="")

            elif event_type == "response.completed" and event_data:
                # Extract citations from final response
                output_items = MigrationHelper.safe_get_output_items(event_data)
                for item in output_items:
                    # Handle typed message item
                    if hasattr(item, "type") and item.type == "message":
                        if hasattr(item, "content"):
                            for content in item.content:
                                if hasattr(content, "annotations"):
                                    citations.extend(content.annotations)
                    # Handle dict message item
                    elif isinstance(item, dict) and item.get("type") == "message":
                        for content in item.get("content", []):
                            if isinstance(content, dict):
                                annotations = content.get("annotations", [])
                                citations.extend(annotations)

            elif event_type == "done":
                break

    except KeyboardInterrupt:
        console.print("\n[yellow]Query interrupted[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Query error: {e}[/red]")
        import traceback

        traceback.print_exc()

    # Show citations if any
    if citations:
        console.print(f"\n\n[bold]📚 Citations ({len(citations)}):[/bold]")
        for i, citation in enumerate(citations, 1):
            if hasattr(citation, "filename"):
                # Typed citation
                console.print(f"[{i}] {citation.filename}")
                if hasattr(citation, "file_id"):
                    console.print(f"    File: {citation.file_id}")
            elif isinstance(citation, dict):
                # Dict citation
                console.print(f"[{i}] {citation.get('filename', 'Unknown')}")
                if "file_id" in citation:
                    console.print(f"    File: {citation['file_id']}")


async def main():
    """Main workflow."""
    console = Console()

    # Configuration
    file_path = "example.pdf"  # Change this to your file
    vector_store_name = "My Test Collection"
    queries = [
        "What is the main topic of this document?",
        "Summarize the key points",
        "What conclusions are drawn?",
    ]

    console.print("[bold green]Knowledge Forge Typed API Workflow[/bold green]")
    console.print("=" * 50)

    # Check if file exists
    if not Path(file_path).exists():
        console.print(f"[red]Error: File not found: {file_path}[/red]")
        console.print("\nPlease update the file_path variable with an actual file.")
        return

    # Step 1: Upload file
    file_id = await upload_file_with_progress(file_path, console)
    if not file_id:
        return

    # Step 2: Create vector store
    vector_store_id = await create_vectorstore_with_file(file_id, vector_store_name, console)
    if not vector_store_id:
        return

    # Step 3: Query the vector store
    for query in queries:
        await query_with_typed_api(query, vector_store_id, console)
        console.print("\n" + "-" * 50 + "\n")

    console.print("[bold green]✅ Workflow completed![/bold green]")


if __name__ == "__main__":
    asyncio.run(main())
