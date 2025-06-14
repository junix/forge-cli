#!/usr/bin/env python3
import argparse
import json
import mimetypes
import os
import time

import requests

from dataset import load_test_dataset

# Use environment variable for server URL if available, otherwise default to localhost
default_url = os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999")
# default_url = "https://api-paas-di.yunxuetang.com.cn/knowledge-forge"


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
            for i in range(1000):  # Try for up to 10 seconds
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

                    # Print a summary of the parsed document
                    content_json = content_response.json()
                    print("\n--- Parsed Document Summary ---")
                    print(f"Title: {content_json.get('title', 'N/A')}")
                    content = content_json.get("content", {})
                    print(f"Summary: {content.get('summary', 'N/A')}")
                    print(f"Page count: {content.get('page_count', 'N/A')}")
                    print(f"File type: {content.get('file_type', 'N/A')}")
                    # Try to get combined text from segments
                    segments = content.get("segments", [])
                    if segments:
                        all_text = "\n".join(seg.get("content", "") for seg in segments if seg.get("content"))
                        snippet = all_text[:500]
                        print(f"Text snippet (first 500 chars):\n{snippet}")
                    else:
                        print("No text segments found.")
                    print("--- End of Document Summary ---\n")

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


def delete_vector_store(vector_store_id, server_url=default_url):
    """Delete an existing vector store.

    Args:
        vector_store_id (str): ID of the vector store to delete.
        server_url (str, optional): Server URL. Defaults to environment variable or localhost.

    Returns:
        bool: True if successful or not found, False if there was an error.
    """
    try:
        # Construct the URL for the DELETE request
        url = f"{server_url}/v1/vector_stores/{vector_store_id}"
        print(f"Deleting vector store {vector_store_id} at: {url}")

        # Send the DELETE request
        response = requests.delete(url)

        # Handle different response codes
        if response.status_code == 404:
            print(f"Vector store {vector_store_id} not found (already deleted or never existed)")
            return True  # Consider this successful since our goal is to ensure it doesn't exist
        elif response.status_code == 200:
            print("Vector store deletion successful. Server response:")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            response.raise_for_status()  # This will raise an exception for other error codes
            return True

    except requests.exceptions.RequestException as e:
        print(f"Error deleting vector store: {e}")
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"Server error details: {json.dumps(error_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Server error response (non-JSON): {e.response.text[:500]}")
        return False


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


def run_dataset_flow(dataset_path, server_url=default_url):
    """Run the flow for all files in a dataset JSON file.

    Args:
        dataset_path (str): Path to the dataset JSON file.
        server_url (str, optional): Server URL. Defaults to environment variable or localhost.

    Returns:
        bool: True if all files were processed successfully, False otherwise.
    """
    try:
        # Load the dataset
        print(f"Loading dataset from: {dataset_path}")
        dataset = load_test_dataset(dataset_path)

        vec_id = dataset.vectorstore_id
        if not vec_id:
            print("Error: No vectorstore_id specified in dataset")
            return False

        print(f"Using vector store ID: {vec_id}")
        print(f"Found {len(dataset.files)} files to process")

        # Step 0: Delete existing vector store to ensure clean state
        print("\n=== STEP 0: DELETING EXISTING VECTOR STORE (IF EXISTS) ===")
        delete_success = delete_vector_store(vec_id, server_url)
        if not delete_success:
            print("Failed to delete existing vector store. Aborting flow.")
            return False

        # Step 1: Create the vector store with the specified ID
        print("\n=== STEP 1: CREATING VECTOR STORE ===")
        vector_store_response = create_vector_store(vec_id, server_url=server_url)
        if not vector_store_response:
            print("Failed to create vector store. Aborting flow.")
            return False

        # Step 2: Process each file
        successful_files = []
        failed_files = []

        for i, file_entry in enumerate(dataset.files, 1):
            print(f"\n=== PROCESSING FILE {i}/{len(dataset.files)} ===")
            print(f"File ID: {file_entry.file_id}")
            print(f"Path: {file_entry.path}")
            if file_entry.questions:
                print(f"Questions: {len(file_entry.questions)}")

            # Upload the file
            file_response = upload_file(file_entry.path, file_entry.file_id, server_url)
            if not file_response:
                print(f"Failed to upload file: {file_entry.path}")
                failed_files.append(file_entry)
                continue

            # Get the actual file ID (in case it was auto-generated)
            actual_file_id = file_response["id"]

            # Join the file to the vector store
            success = join_file_to_vector_store(vec_id, actual_file_id, server_url)
            if not success:
                print(f"Failed to join file to vector store: {file_entry.path}")
                failed_files.append(file_entry)
                continue

            successful_files.append(file_entry)
            print(f"Successfully processed file: {file_entry.path}")

        # Summary
        print("\n=== DATASET PROCESSING SUMMARY ===")
        print(f"Total files: {len(dataset.files)}")
        print(f"Successful: {len(successful_files)}")
        print(f"Failed: {len(failed_files)}")

        if failed_files:
            print("\nFailed files:")
            for file_entry in failed_files:
                print(f"  - {file_entry.path} (ID: {file_entry.file_id})")

        return len(failed_files) == 0

    except Exception as e:
        print(f"Error processing dataset: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a vector store and upload multiple files from a dataset JSON file"
    )

    # Required arguments
    parser.add_argument("--dataset", required=True, help="Path to a dataset JSON file containing files to upload")

    # Optional arguments
    parser.add_argument(
        "--server",
        default=default_url,
        help=f"Server URL (default: {default_url})",
    )

    args = parser.parse_args()

    # Run the dataset flow
    success = run_dataset_flow(args.dataset, args.server)

    # Exit with appropriate code
    exit(0 if success else 1)
