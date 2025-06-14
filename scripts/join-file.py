#!/usr/bin/env python3
import argparse
import json
import mimetypes
import os
import time  # Import the mimetypes library

import requests

# Use environment variable for server URL if available, otherwise default to localhost
default_url = os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999")


def upload_file(file_path, server_url=default_url):
    """Upload a file to the Knowledge Forge API."""
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return

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
        # Remove mime_type from data, purpose is still needed by the API endpoint
        # Using 'general' as the default purpose now, as per the latest API changes
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
        if task_id:
            for i in range(10):
                time.sleep(1)
                url = f"{server_url}/v1/tasks/{task_id}"
                response = requests.get(url)
                response.raise_for_status()
                print(json.dumps(response.json(), indent=2))
                if response.json()["status"] == "completed":
                    url = f"{server_url}/v1/files/{file_id}/content"
                    response = requests.get(url)
                    response.raise_for_status()
                    print(json.dumps(response.json(), indent=2))
                    return response.json()
                    break

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


def delete_file(file_id, server_url=default_url):
    """Delete a file from the Knowledge Forge API.

    Args:
        file_id (str): The ID of the file to delete.
        server_url (str, optional): Server URL. Defaults to "http://localhost:9999".

    Returns:
        dict or None: The server response if successful, None otherwise.
    """
    try:
        # Construct the URL for the DELETE request
        url = f"{server_url}/v1/files/{file_id}"
        print(f"Deleting file with ID '{file_id}' from: {url}")

        # Send the DELETE request
        response = requests.delete(url)

        # Check if the request was successful
        response.raise_for_status()

        # Print and return the response
        print("Delete successful. Server response:")
        print(json.dumps(response.json(), indent=2))
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error during file deletion: {e}")
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"Server error details: {json.dumps(error_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Server error response (non-JSON): {e.response.text[:500]}")  # Limit long responses
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a file to Knowledge Forge API")
    parser.add_argument("-f", "--file", help="Path to the file to upload")
    parser.add_argument(
        "--server",
        default=default_url,
        help=f"Server URL (default: {default_url})",
    )
    parser.add_argument("--delete", help="ID of the file to delete")

    args = parser.parse_args()

    if args.delete:
        delete_file(args.delete, args.server)
    elif args.file:
        upload_file(args.file, args.server)
    else:
        parser.print_help()
