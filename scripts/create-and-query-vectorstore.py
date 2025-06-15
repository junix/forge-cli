#!/usr/bin/env python3
import argparse
import asyncio
import json
import os
from typing import Any

# Import SDK functions
from forge_cli.sdk import (
    async_create_vectorstore,
    async_join_files_to_vectorstore,
    async_query_vectorstore,
    async_upload_file,
)

# Default IDs
DEFAULT_FILE_ID = "f8e5d7c6-b9a8-4321-9876-543210abcdef"
DEFAULT_VEC_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"


async def create_vector_store(vec_id, name=None, description=None):
    """Create a new vector store collection with a specific ID using SDK.

    Args:
        vec_id (str): The ID to use for the vector store.
        name (str, optional): Name of the vector store. Defaults to a generated name.
        description (str, optional): Description of the vector store.

    Returns:
        dict or None: The server response if successful, None otherwise.
    """
    try:
        # Generate a default name if none provided
        if not name:
            name = f"VectorStore_{vec_id[:8] if len(vec_id) >= 8 else vec_id}"

        print(f"Creating vector store with ID '{vec_id}'")

        # Call the SDK function to create the vector store
        result = await async_create_vectorstore(
            name=name,
            description=description,
            custom_id=vec_id,
        )

        if result:
            print("Vector store creation successful. Server response:")
            print(result.model_dump_json(indent=2, exclude_none=True, ensure_ascii=False))
            print(f"Successfully created vector store with ID: {result.id}")
            return result.model_dump()
        else:
            print("Failed to create vector store.")
            return None

    except Exception as e:
        print(f"Error during vector store creation: {e}")
        return None


async def upload_file(file_path, file_id=None):
    """Upload a file to the Knowledge Forge API with a specific ID using SDK.

    Args:
        file_path (str): Path to the file to upload.
        file_id (str, optional): Specific ID to use for the file. Must be a valid UUID.

    Returns:
        dict or None: The server response if successful, None otherwise.
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return None

    try:
        file_name = os.path.basename(file_path)
        print(f"Uploading '{file_name}' with ID: {file_id if file_id else 'auto-generated'}")

        # Call the SDK function to upload the file
        result = await async_upload_file(
            file_path=file_path,
            purpose="general",
            custom_id=file_id,
        )

        if result:
            print("Upload successful. Server response:")
            print(result.model_dump_json(indent=2, exclude_none=True, ensure_ascii=False))
            return result.model_dump()
        else:
            print("Failed to upload file.")
            return None

    except Exception as e:
        print(f"Error during upload: {e}")
        return None


async def join_file_to_vector_store(vector_store_id, file_id):
    """Join a file to an existing vector store using SDK.

    Args:
        vector_store_id (str): ID of the vector store.
        file_id (str): ID of the file to join.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        print(f"Joining file {file_id} to vector store {vector_store_id}")

        # Call the SDK function to join files
        result = await async_join_files_to_vectorstore(vector_store_id=vector_store_id, file_ids=[file_id])

        if result:
            print("File joined successfully. Server response:")
            print(result.model_dump_json(indent=2, exclude_none=True, ensure_ascii=False))
            return True
        else:
            print("Failed to join file to vector store.")
            return False

    except Exception as e:
        print(f"Error joining file to vector store: {e}")
        return False


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
        if vector_store_id == DEFAULT_VEC_ID:
            print(f"Querying default vector store with: '{query}'")
        else:
            print(f"Querying vector store '{vector_store_id}' with: '{query}'")

        # Call the SDK function to query the vector store
        result = await async_query_vectorstore(
            vector_store_id=vector_store_id,
            query=query,
            top_k=top_k,
            filters=filters,
        )

        if result:
            # Print the search query and results
            print(f"\nSearch query: {result.search_query}")
            print(f"Found {len(result.data)} results:")

            # Print each result with its score and content
            for i, search_result in enumerate(result.data, 1):
                print(
                    f"\n[{i}] Score: {search_result.score:.4f} | File: {search_result.filename} (ID: {search_result.file_id})"
                )

                # Print attributes if any
                if search_result.attributes:
                    print(f"    Attributes: {json.dumps(search_result.attributes)}")

                # Print content
                for content_item in search_result.content:
                    if content_item.type == "text":
                        # Format the text content for better readability
                        text = content_item.text.strip()
                        # Truncate long text for display
                        if len(text) > 500:
                            text = text[:500] + "..."
                        print(f"    Content: {text}")

            return result.model_dump()
        else:
            print("Failed to query vector store.")
            return None

    except Exception as e:
        print(f"Error during vector store query: {e}")
        return None


async def run_full_flow(
    file_path,
    query,
    vec_id=DEFAULT_VEC_ID,
    file_id=DEFAULT_FILE_ID,
):
    """Run the complete flow: create vector store, upload file, join file to vector store, and query.

    Args:
        file_path (str): Path to the file to upload.
        query (str): The search query text.
        vec_id (str, optional): ID to use for the vector store. Defaults to DEFAULT_VEC_ID.
        file_id (str, optional): ID to use for the file. Defaults to DEFAULT_FILE_ID.

    Returns:
        bool: True if all steps completed successfully, False otherwise.
    """
    # Step 1: Create the vector store with the specified ID
    print("\n=== STEP 1: CREATING VECTOR STORE ===")
    vector_store_response = await create_vector_store(vec_id)
    if not vector_store_response:
        print("Failed to create vector store. Aborting flow.")
        return False

    # Step 2: Upload the file with the specified ID
    print("\n=== STEP 2: UPLOADING FILE ===")
    file_response = await upload_file(file_path, file_id)
    if not file_response:
        print("Failed to upload file. Aborting flow.")
        return False

    # Get the file ID from the response
    actual_file_id = file_response["id"]
    print(f"Successfully uploaded file with ID: {actual_file_id}")

    # Step 3: Join the file to the vector store
    print("\n=== STEP 3: JOINING FILE TO VECTOR STORE ===")
    success = await join_file_to_vector_store(vec_id, actual_file_id)
    if not success:
        print("Failed to join file to vector store.")
        return False

    print(f"Successfully joined file {actual_file_id} to vector store {vec_id}")

    # Step 4: Query the vector store
    print("\n=== STEP 4: QUERYING VECTOR STORE ===")
    query_response = await query_vector_store(vec_id, query, top_k=5)
    if not query_response:
        print("Failed to query vector store.")
        return False

    print("\n=== FLOW COMPLETED SUCCESSFULLY ===")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a vector store, upload a file, join them, and query the vector store using SDK"
    )

    # File and query arguments
    parser.add_argument("-f", "--file", required=True, help="Path to the file to upload")
    parser.add_argument("-q", "--query", required=True, help="Search query text")

    # Optional arguments
    parser.add_argument(
        "--vec-id",
        default=DEFAULT_VEC_ID,
        help=f"ID to use for the vector store (default: {DEFAULT_VEC_ID})",
    )
    parser.add_argument(
        "--file-id",
        default=DEFAULT_FILE_ID,
        help=f"ID to use for the file (default: {DEFAULT_FILE_ID})",
    )

    args = parser.parse_args()

    # Run the flow
    asyncio.run(run_full_flow(args.file, args.query, args.vec_id, args.file_id))
