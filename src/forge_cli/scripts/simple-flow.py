#!/usr/bin/env python3
import argparse
import json
import mimetypes
import os
import time

import requests

# Use environment variable for server URL if available, otherwise default to localhost
local_url = os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999")


def upload_file(file_path, server_url=local_url):
    """Upload a file to the Knowledge Forge API."""
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
        # Using 'general' as the default purpose
        data = {"purpose": "general"}

        # Make the POST request to the API
        url = f"{server_url}/v1/files"
        print(f"Uploading '{file_name}' ({mime_type}) to: {url} with purpose: {data['purpose']}")

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

        # Wait for the task to complete
        if task_id:
            print("Waiting for file processing to complete...")
            for i in range(10):
                time.sleep(1)
                url = f"{server_url}/v1/tasks/{task_id}"
                response = requests.get(url)
                response.raise_for_status()
                task_status = response.json()
                if task_status["status"] == "completed":
                    print("File processing completed.")
                    return file_id
                elif task_status["status"] in ["failed", "cancelled"]:
                    print(f"File processing {task_status['status']}.")
                    return None

            print("Timed out waiting for file processing.")
            return file_id  # Return the file ID anyway, it might still be usable

        return file_id

    except requests.exceptions.RequestException as e:
        print(f"Error during upload: {e}")
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"Server error details: {json.dumps(error_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Server error response (non-JSON): {e.response.text[:500]}")  # Limit long responses
        return None
    finally:
        # Ensure the file is closed even if an error occurs
        if file_object and not file_object.closed:
            file_object.close()


def create_vector_store(name, description=None, server_url=local_url):
    """Create a new vector store collection.

    Args:
        name (str): Name of the vector store.
        description (str, optional): Description of the vector store.
        server_url (str, optional): Server URL. Defaults to "http://localhost:9999".

    Returns:
        str or None: The vector store ID if successful, None otherwise.
    """
    try:
        # Construct the URL for the POST request
        url = f"{server_url}/v1/vector_stores"
        print(f"Creating vector store '{name}' at: {url}")

        # Prepare request payload
        payload = {
            "name": name,
        }

        # Add description as metadata if provided
        if description:
            payload["metadata"] = {"description": description}

        # Send the POST request
        response = requests.post(url, json=payload)

        # Check if the request was successful
        response.raise_for_status()

        # Print and return the response
        print("Vector store creation successful. Server response:")
        print(json.dumps(response.json(), indent=2))
        vector_store_id = response.json()["id"]
        print(f"Successfully created vector store with ID: {vector_store_id}")
        return vector_store_id

    except requests.exceptions.RequestException as e:
        print(f"Error during vector store creation: {e}")
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"Server error details: {json.dumps(error_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Server error response (non-JSON): {e.response.text[:500]}")
        return None


def join_file_to_vector_store(vector_store_id, file_id, server_url=local_url):
    """Join a file to an existing vector store.

    Args:
        vector_store_id (str): ID of the vector store.
        file_id (str): ID of the file to join.
        server_url (str, optional): Server URL. Defaults to "http://localhost:9999".

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


def run_simple_flow(file_path, collection_name, server_url=local_url):
    """Run the simple flow: upload file, create collection, join file to collection.

    Args:
        file_path (str): Path to the file to upload.
        collection_name (str): Name for the vector store collection.
        server_url (str, optional): Server URL. Defaults to "http://localhost:9999".

    Returns:
        bool: True if the entire flow was successful, False otherwise.
    """
    # Step 1: Upload the file
    print("\n=== STEP 1: UPLOADING FILE ===")
    file_id = upload_file(file_path, server_url)
    if not file_id:
        print("Failed to upload file. Aborting flow.")
        return False

    print(f"Successfully uploaded file with ID: {file_id}")

    # Step 2: Create the vector store
    print("\n=== STEP 2: CREATING VECTOR STORE ===")
    vector_store_id = create_vector_store(collection_name, server_url=server_url)
    if not vector_store_id:
        print("Failed to create vector store. Aborting flow.")
        return False

    print(f"Successfully created vector store with ID: {vector_store_id}")

    # Step 3: Join the file to the vector store
    print("\n=== STEP 3: JOINING FILE TO VECTOR STORE ===")
    success = join_file_to_vector_store(vector_store_id, file_id, server_url)
    if not success:
        print("Failed to join file to vector store.")
        return False

    print(f"Successfully joined file {file_id} to vector store {vector_store_id}")
    print("\n=== FLOW COMPLETED SUCCESSFULLY ===")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Knowledge Forge Simple Flow")

    # Required arguments
    parser.add_argument("-f", "--file", required=True, help="Path to the file to upload")
    parser.add_argument("-n", "--name", required=True, help="Name of the vector store to create")

    # Optional arguments
    parser.add_argument(
        "--server",
        default=local_url,
        help="Server URL (default: http://localhost:9999)",
    )

    args = parser.parse_args()

    # Run the simple flow
    run_simple_flow(args.file, args.name, args.server)
