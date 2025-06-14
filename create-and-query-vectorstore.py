#!/usr/bin/env python3
import argparse
import json
import mimetypes
import os
import time
from typing import Any

import requests

# Use environment variable for server URL if available, otherwise default to localhost
default_url = os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999")

# Default IDs
DEFAULT_FILE_ID = "f8e5d7c6-b9a8-4321-9876-543210abcdef"
DEFAULT_VEC_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"


def create_vector_store(vec_id, name=None, description=None, server_url=default_url):
    """Create a new vector store collection with a specific ID.

    Args:
        vec_id (str): The ID to use for the vector store.
        name (str, optional): Name of the vector store. Defaults to a generated name.
        description (str, optional): Description of the vector store.
        server_url (str, optional): Server URL. Defaults to environment variable or localhost.

    Returns:
        dict or None: The server response if successful, None otherwise.
    """
    try:
        # Generate a default name if none provided
        if not name:
            name = f"VectorStore_{vec_id[:8] if len(vec_id) >= 8 else vec_id}"

        # Construct the URL for the POST request
        url = f"{server_url}/v1/vector_stores"
        print(f"Creating vector store with ID '{vec_id}' at: {url}")

        # Prepare request payload
        payload = {
            "id": vec_id,
            "name": name,
        }

        # Add optional description if provided
        if description:
            payload["description"] = description

        # Send the POST request
        response = requests.post(url, json=payload)

        # Check if the request was successful
        response.raise_for_status()

        # Print and return the response
        print("Vector store creation successful. Server response:")
        print(json.dumps(response.json(), indent=2))
        print(f"Successfully created vector store with ID: {response.json()['id']}")
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error during vector store creation: {e}")
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"Server error details: {json.dumps(error_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Server error response (non-JSON): {e.response.text[:500]}")  # Limit long responses
        return None


def upload_file(file_path, file_id=None, server_url=default_url):
    """Upload a file to the Knowledge Forge API with a specific ID.

    Args:
        file_path (str): Path to the file to upload.
        file_id (str, optional): Specific ID to use for the file. Must be a valid UUID.
        server_url (str, optional): Server URL. Defaults to environment variable or localhost.

    Returns:
        dict or None: The server response if successful, None otherwise.
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return None

    # Guess the MIME type of the file
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = "application/octet-stream"  # Default if guessing fails
        print(f"Warning: Could not guess MIME type for {file_path}. Using {mime_type}.")

    file_object = None  # Initialize file_object to ensure it's closed in finally
    try:
        # Prepare the multipart/form-data
        file_object = open(file_path, "rb")
        file_name = os.path.basename(file_path)

        # Send file with filename and correct content type
        files = {"file": (file_name, file_object, mime_type)}

        # Prepare form data
        data = {"purpose": "general"}

        # Add file_id if provided
        if file_id:
            data["id"] = file_id

        # Make the POST request to the API
        url = f"{server_url}/v1/files"
        print(f"Uploading '{file_name}' ({mime_type}) to: {url} with ID: {file_id if file_id else 'auto-generated'}")

        # Send the request
        response = requests.post(url, files=files, data=data)

        # Check if the request was successful
        response.raise_for_status()

        # Print the response
        print("Upload successful. Server response:")
        print(json.dumps(response.json(), indent=2))

        res = response.json()
        task_id = res["task_id"]
        file_id = res["id"]

        # Wait for file processing to complete
        if task_id:
            print("Waiting for file processing to complete...")
            for i in range(10):  # Try for up to 10 seconds
                time.sleep(1)
                task_url = f"{server_url}/v1/tasks/{task_id}"
                task_response = requests.get(task_url)
                task_response.raise_for_status()

                task_status = task_response.json()
                print(f"Task status: {task_status['status']}")

                if task_status["status"] == "completed":
                    # Get file content details
                    content_url = f"{server_url}/v1/files/{file_id}/content"
                    content_response = requests.get(content_url)
                    content_response.raise_for_status()
                    print("File processing completed. Content details:")
                    print(json.dumps(content_response.json(), indent=2))
                    return res
                elif task_status["status"] in ["failed", "cancelled"]:
                    print(f"File processing {task_status['status']}.")
                    return None

            print("Timed out waiting for file processing to complete.")
            return res  # Return the original response even if processing is still ongoing

        return res

    except requests.exceptions.RequestException as e:
        print(f"Error during upload: {e}")
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"Server error details: {json.dumps(error_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Server error response (non-JSON): {e.response.text[:500]}")
        return None
    finally:
        # Ensure the file is closed even if an error occurs
        if file_object and not file_object.closed:
            file_object.close()


def join_file_to_vector_store(vector_store_id, file_id, server_url=default_url):
    """Join a file to an existing vector store.

    Args:
        vector_store_id (str): ID of the vector store.
        file_id (str): ID of the file to join.
        server_url (str, optional): Server URL. Defaults to environment variable or localhost.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Construct the URL for the POST request
        url = f"{server_url}/v1/vector_stores/{vector_store_id}"
        print(f"Joining file {file_id} to vector store {vector_store_id}")

        # Prepare request payload
        payload = {"join_file_ids": [file_id]}

        # Send the POST request
        response = requests.post(url, json=payload)

        # Check if the request was successful
        response.raise_for_status()

        # Print and return the response
        print("File joined successfully. Server response:")
        print(json.dumps(response.json(), indent=2))
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error joining file to vector store: {e}")
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"Server error details: {json.dumps(error_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Server error response (non-JSON): {e.response.text[:500]}")
        return False


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
        if vector_store_id == DEFAULT_VEC_ID:
            print(f"Querying default vector store with: '{query}'")
        else:
            print(f"Querying vector store '{vector_store_id}' with: '{query}'")

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

        # Print the search query and results
        print(f"\nSearch query: {response_data['search_query']}")
        print(f"Found {len(response_data['data'])} results:")

        # Print each result with its score and content
        for i, result in enumerate(response_data["data"], 1):
            print(f"\n[{i}] Score: {result['score']:.4f} | File: {result['filename']} (ID: {result['file_id']})")

            # Print attributes if any
            if result["attributes"]:
                print(f"    Attributes: {json.dumps(result['attributes'])}")

            # Print content
            for content_item in result["content"]:
                if content_item["type"] == "text":
                    # Format the text content for better readability
                    text = content_item["text"].strip()
                    # Truncate long text for display
                    if len(text) > 500:
                        text = text[:500] + "..."
                    print(f"    Content: {text}")

        return response_data

    except requests.exceptions.RequestException as e:
        print(f"Error during vector store query: {e}")
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"Server error details: {json.dumps(error_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Server error response (non-JSON): {e.response.text[:500]}")  # Limit long responses
        return None


def run_full_flow(
    file_path,
    query,
    vec_id=DEFAULT_VEC_ID,
    file_id=DEFAULT_FILE_ID,
    server_url=default_url,
):
    """Run the complete flow: create vector store, upload file, join file to vector store, and query.

    Args:
        file_path (str): Path to the file to upload.
        query (str): The search query text.
        vec_id (str, optional): ID to use for the vector store. Defaults to DEFAULT_VEC_ID.
        file_id (str, optional): ID to use for the file. Defaults to DEFAULT_FILE_ID.
        server_url (str, optional): Server URL. Defaults to environment variable or localhost.

    Returns:
        bool: True if all steps completed successfully, False otherwise.
    """
    # Step 1: Create the vector store with the specified ID
    print("\n=== STEP 1: CREATING VECTOR STORE ===")
    vector_store_response = create_vector_store(vec_id, server_url=server_url)
    if not vector_store_response:
        print("Failed to create vector store. Aborting flow.")
        return False

    # Step 2: Upload the file with the specified ID
    print("\n=== STEP 2: UPLOADING FILE ===")
    file_response = upload_file(file_path, file_id, server_url)
    if not file_response:
        print("Failed to upload file. Aborting flow.")
        return False

    # Get the file ID from the response
    actual_file_id = file_response["id"]
    print(f"Successfully uploaded file with ID: {actual_file_id}")

    # Step 3: Join the file to the vector store
    print("\n=== STEP 3: JOINING FILE TO VECTOR STORE ===")
    success = join_file_to_vector_store(vec_id, actual_file_id, server_url)
    if not success:
        print("Failed to join file to vector store.")
        return False

    print(f"Successfully joined file {actual_file_id} to vector store {vec_id}")

    # Step 4: Query the vector store
    print("\n=== STEP 4: QUERYING VECTOR STORE ===")
    query_response = query_vector_store(vec_id, query, top_k=5, server_url=server_url)
    if not query_response:
        print("Failed to query vector store.")
        return False

    print("\n=== FLOW COMPLETED SUCCESSFULLY ===")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a vector store, upload a file, join them, and query the vector store"
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
    parser.add_argument(
        "--server",
        default=default_url,
        help=f"Server URL (default: {default_url})",
    )

    args = parser.parse_args()

    # Run the flow
    run_full_flow(args.file, args.query, args.vec_id, args.file_id, args.server)
