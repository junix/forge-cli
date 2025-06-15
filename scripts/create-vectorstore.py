#!/usr/bin/env python3
"""
Create and manage vector stores in Knowledge Forge.

This script uses the sdk.py client library to create and manage vector stores.
Both name and description are required when creating a vector store to ensure
proper documentation and searchability.

Server Configuration:
- Default server URL is http://localhost:9999
- Can be overridden by setting KNOWLEDGE_FORGE_URL environment variable
- Can also be specified with --server command line argument

Example usage:
  # Create a new vector store
  ./create-vectorstore.py create --name "My Vector Store" --description "Detailed description of the vector store"

  # Add files to a vector store
  ./create-vectorstore.py add-files --id <vector_store_id> --file-ids <file_id1> <file_id2>

  # Get vector store details
  ./create-vectorstore.py get --id <vector_store_id>
"""

import argparse
import asyncio
import json
import os
from typing import Any

# Import SDK functions
from forge_cli.sdk import (
    async_create_vectorstore,
    async_get_vectorstore,
    async_join_files_to_vectorstore,
)


async def create_vector_store_async(
    name: str,
    description: str,  # Now required
    file_ids: list[str] | None = None,
    custom_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """
    Create a new vector store using the SDK.

    Args:
        name: Name of the vector store (required)
        description: Description of the vector store (required)
        file_ids: Optional list of file IDs to include
        custom_id: Optional custom ID for the vector store
        metadata: Optional additional metadata
    """
    try:
        print(f"Creating vector store: '{name}'")

        # Build metadata dictionary with required description
        combined_metadata = {"description": description}

        # Add any additional metadata if provided
        if metadata:
            combined_metadata.update(metadata)

        # Call the SDK function to create the vector store
        result = await async_create_vectorstore(
            name=name,
            description=description,
            file_ids=file_ids,
            custom_id=custom_id,
            metadata=combined_metadata if combined_metadata else None,
        )

        if result:
            # Success - print the result
            print("\nVector store creation successful:")
            print(f"ID: {result.id}")
            print(f"Name: {result.name}")
            print(f"Description: {description}")
            if file_ids:
                print(f"Associated files: {', '.join(file_ids)}")

            # Print the full JSON response if verbose
            if args.verbose:
                print("\nFull server response:")
                print(result.model_dump_json(indent=2, exclude_none=True, ensure_ascii=False))
        else:
            print("Vector store creation failed. Check server logs for details.")

    except Exception as e:
        print(f"Error creating vector store: {e}")


async def add_files_to_vectorstore_async(vector_store_id: str, file_ids: list[str]) -> None:
    """
    Add files to an existing vector store.

    Args:
        vector_store_id: ID of the vector store
        file_ids: List of file IDs to add
    """
    try:
        print(f"Adding files to vector store {vector_store_id}...")

        # Call the SDK function to join files
        result = await async_join_files_to_vectorstore(vector_store_id=vector_store_id, file_ids=file_ids)

        if result:
            print("Files added successfully to vector store.")

            # Print the full JSON response if verbose
            if args.verbose:
                print("\nUpdated vector store:")
                print(result.model_dump_json(indent=2, exclude_none=True, ensure_ascii=False))
        else:
            print("Failed to add files to vector store.")

    except Exception as e:
        print(f"Error adding files to vector store: {e}")


async def get_vectorstore_async(vector_store_id: str) -> None:
    """
    Get details of an existing vector store.

    Args:
        vector_store_id: ID of the vector store to fetch
    """
    try:
        print(f"Fetching vector store details for ID: {vector_store_id}")

        # Call the SDK function to get the vector store
        result = await async_get_vectorstore(vector_store_id)

        if result:
            print("\nVector store details:")
            print(f"ID: {result.id}")
            print(f"Name: {result.name}")
            print(f"Created at: {result.created_at}")

            # Display metadata if available
            metadata = result.metadata or {}
            if metadata.get("description"):
                print(f"Description: {metadata.get('description')}")

                # Display other metadata
                other_metadata = {k: v for k, v in metadata.items() if k != "description"}
                if other_metadata:
                    print("Additional metadata:")
                    for key, value in other_metadata.items():
                        print(f"  {key}: {value}")

            # Display associated files
            file_ids = result.file_ids or []
            if file_ids:
                print(f"Associated files ({len(file_ids)}):")
                for file_id in file_ids:
                    print(f"  - {file_id}")
            else:
                print("No files associated with this vector store.")

            # Print the full JSON response if verbose
            if args.verbose:
                print("\nFull server response:")
                print(result.model_dump_json(indent=2, exclude_none=True, ensure_ascii=False))
        else:
            print(f"Failed to fetch vector store with ID: {vector_store_id}")

    except Exception as e:
        print(f"Error fetching vector store: {e}")


if __name__ == "__main__":
    # Set up command-line argument parser
    parser = argparse.ArgumentParser(description="Knowledge Forge Vector Store Manager")

    # Server configuration - use environment variable if available
    default_server = os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999")
    parser.add_argument(
        "--server",
        default=default_server,
        help=f"Server URL (default: {default_server})",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Display verbose output including full JSON responses",
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Create vector store command
    create_parser = subparsers.add_parser("create", help="Create a new vector store")
    create_parser.add_argument("-n", "--name", required=True, help="Name of the vector store")
    create_parser.add_argument(
        "--description",
        required=True,
        help="Description of the vector store (required)",
    )
    create_parser.add_argument("--file-ids", nargs="+", help="File IDs to include in the vector store")
    create_parser.add_argument("--id", dest="custom_id", help="Custom ID for the vector store (optional)")

    # Add files command
    add_files_parser = subparsers.add_parser("add-files", help="Add files to an existing vector store")
    add_files_parser.add_argument(
        "-i",
        "--id",
        required=True,
        dest="vector_store_id",
        help="ID of the vector store",
    )
    add_files_parser.add_argument(
        "--file-ids",
        required=True,
        nargs="+",
        help="File IDs to add to the vector store",
    )

    # Get vector store command
    get_parser = subparsers.add_parser("get", help="Get details of a vector store")
    get_parser.add_argument(
        "-i",
        "--id",
        required=True,
        dest="vector_store_id",
        help="ID of the vector store to fetch",
    )

    # Parse arguments
    args = parser.parse_args()

    # Set the server URL from command line if provided
    if args.server != default_server:
        os.environ["KNOWLEDGE_FORGE_URL"] = args.server

    # Execute the appropriate command
    if args.command == "create":
        asyncio.run(
            create_vector_store_async(
                name=args.name,
                description=args.description,
                file_ids=args.file_ids,
                custom_id=args.custom_id,
            )
        )
    elif args.command == "add-files" and args.vector_store_id and args.file_ids:
        asyncio.run(add_files_to_vectorstore_async(vector_store_id=args.vector_store_id, file_ids=args.file_ids))
    elif args.command == "get" and args.vector_store_id:
        asyncio.run(get_vectorstore_async(vector_store_id=args.vector_store_id))
    else:
        # If no command or required args are provided, show help
        parser.print_help()
