#!/usr/bin/env python3
"""
Command-line utility for managing files through the Knowledge Forge API.
Uses the sdk.py client library for all API interactions.

Server Configuration:
- Default server URL is http://localhost:9999
- Can be overridden by setting KNOWLEDGE_FORGE_URL environment variable
- Can also be specified with --server command line argument
"""

import argparse
import asyncio
import os
from pathlib import Path

# Import sdk functions that we'll use
from forge_cli.sdk.files import (
    async_delete_file,
    async_fetch_file,
    async_upload_file,
    async_wait_for_task_completion,
)
from forge_cli.sdk.types import DeleteResponse, File, TaskStatus
from forge_cli.sdk.utils import print_file_results


def main():
    """Main entry point for the file management script."""
    # Set up command-line argument parser
    parser = argparse.ArgumentParser(description="Upload, download, or delete files using Knowledge Forge API")

    # Server configuration - use environment variable if available
    default_server = os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999")
    parser.add_argument(
        "--server",
        default=default_server,
        help=f"Server URL (default: {default_server})",
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Upload file command
    upload_parser = subparsers.add_parser("upload", help="Upload a file")
    upload_parser.add_argument("-f", "--file", required=True, help="Path to the file to upload")
    upload_parser.add_argument(
        "--purpose", default="general", choices=["general", "qa"], help="Purpose of the file upload (default: general)"
    )
    upload_parser.add_argument("--id", dest="custom_id", help="Custom ID for the file (optional)")
    upload_parser.add_argument("--skip-exists", action="store_true", help="Skip upload if file with same MD5 exists")
    upload_parser.add_argument(
        "--dump",
        action="store_true",
        help="Create a Document object and dump to <doc-id>.json in current directory",
    )

    # Delete file command
    delete_parser = subparsers.add_parser("delete", help="Delete a file")
    delete_parser.add_argument("-i", "--id", required=True, dest="file_id", help="ID of the file to delete")

    # Fetch file command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch a file's details")
    fetch_parser.add_argument("-i", "--id", required=True, dest="file_id", help="ID of the file to fetch")
    fetch_parser.add_argument(
        "--dump",
        action="store_true",
        help="Dump the document content to <doc-id>.json in current directory",
    )

    # Parse arguments
    args = parser.parse_args()

    # Set the server URL for the SDK if provided via command line
    # (otherwise the SDK will use the environment variable or default)
    if args.server != default_server:
        os.environ["KNOWLEDGE_FORGE_URL"] = args.server

    # Execute the appropriate command
    if args.command == "upload" and args.file:
        asyncio.run(upload_file_async(args.file, args.purpose, args.custom_id, args.skip_exists, args.dump))
    elif args.command == "delete" and args.file_id:
        asyncio.run(delete_file_async(args.file_id))
    elif args.command == "fetch" and args.file_id:
        asyncio.run(fetch_file_async(args.file_id, args.dump))
    else:
        # If no command or required args are provided, show help
        parser.print_help()


async def upload_file_async(
    file_path: str,
    purpose: str = "general",
    custom_id: str | None = None,
    skip_exists: bool = False,
    dump: bool = False,
):
    """
    Upload a file using the SDK and optionally dump the result.

    Args:
        file_path: Path to the file to upload
        purpose: Purpose of the file upload
        custom_id: Optional custom ID for the file
        skip_exists: Whether to skip upload if file with same MD5 exists
        dump: Whether to dump the document content to a JSON file
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return

    try:
        print(f"Uploading file: {file_path}")

        # Upload the file using SDK
        upload_result = await async_upload_file(
            file_path, purpose=purpose, custom_id=custom_id, skip_exists=skip_exists
        )

        # Print upload results - using a list of File objects
        print_file_results([upload_result])

        file_id = upload_result.id
        task_id = upload_result.task_id

        # Wait for processing if there's a task ID
        if task_id:
            print(f"Waiting for file processing (task: {task_id})...")
            try:
                final_status: TaskStatus = await async_wait_for_task_completion(task_id)
                print(f"Processing completed with status: {final_status.status}")

                # Show error message if processing failed
                if final_status.status == "failed":
                    error_info = final_status.error or "Unknown error"
                    print(f"Processing failed: {error_info}")
                    return

            except Exception as e:
                print(f"Warning: Error waiting for task completion: {e}")

        # Fetch and optionally dump the processed document
        if file_id:
            await fetch_file_async(file_id, dump)

    except Exception as e:
        print(f"Error during file upload: {e}")


async def fetch_file_async(file_id: str, dump: bool = False):
    """
    Fetch a file's details and optionally dump to JSON.

    Args:
        file_id: The ID of the file to fetch
        dump: Whether to dump the document content to a JSON file
    """
    try:
        print(f"Fetching document content for ID: {file_id}")
        document = await async_fetch_file(file_id)

        if document:
            # Display document information
            print_document_info(document)

            # Dump to JSON file if requested
            if dump:
                await dump_document_to_file(document, file_id)
        else:
            print(f"Failed to fetch document with ID: {file_id}")

    except Exception as e:
        print(f"Error fetching file: {e}")


async def delete_file_async(file_id: str) -> DeleteResponse | None:
    """
    Delete a file using the SDK.

    Args:
        file_id: The ID of the file to delete
        
    Returns:
        DeleteResponse object if successful, None otherwise
    """
    try:
        print(f"Deleting file with ID: {file_id}")

        delete_response = await async_delete_file(file_id)

        if delete_response and delete_response.deleted:
            print(f"File {file_id} deleted successfully!")
        else:
            print(f"Failed to delete file with ID: {file_id}")

    except Exception as e:
        print(f"Error during file deletion: {e}")


def print_document_info(document: File):
    """
    Print key information about a document.

    Args:
        document: The File object containing document information
    """
    print("=== Document Information ===")
    print(f"Document ID: {document.id}")
    print(f"Title: {document.title or 'N/A'}")
    print(f"Filename: {document.filename}")
    print(f"File size: {document.bytes} bytes")
    print(f"Created at: {document.created_at}")

    # Display content details if available
    if document.content:
        content = document.content
        print("\n=== Content Details ===")
        print(f"Language: {content.language or 'unknown'}")
        print(f"File type: {content.file_type or 'unknown'}")
        print(f"Page count: {content.page_count or 0}")

        # Show segment count if segments exist
        if content.segments:
            print(f"Segments: {len(content.segments)}")

        # Show summary if available (first 200 chars)
        if content.summary:
            summary_display = (
                content.summary[:200] + "..." if len(content.summary) > 200 else content.summary
            )
            print(f"\nSummary: {summary_display}")


async def dump_document_to_file(document: File, file_id: str) -> None:
    """
    Dump document data to a JSON file.

    Args:
        document: The File object containing document information
        file_id: The file ID to use for the filename
    """
    try:
        # Use the document ID if available, otherwise use file_id
        doc_id = document.id or file_id
        json_file = f"{doc_id}.json"

        # Ensure we have a valid path
        output_path = Path(json_file).resolve()

        with open(output_path, "w", encoding="utf-8") as f:
            # Use model_dump_json for Pydantic models for correct serialization
            f.write(document.model_dump_json(indent=2))

        print(f"Document content dumped to: {output_path}")

    except Exception as e:
        print(f"Error dumping document to file: {e}")


if __name__ == "__main__":
    main()
