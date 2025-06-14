#!/usr/bin/env python3
import json
import os

import requests

# Use environment variable for server URL if available, otherwise default to localhost
local_url = os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999")


def send_hello_request():
    """Send a simple 'hello' request to the Knowledge Forge API."""

    # Create a request that matches the OpenAI format
    request_json = {
        "model": "qwen-max",  # Using a valid OpenAI model
        "effort": "low",  # Move effort to top level
        "store": True,
        "input": [{"role": "user", "content": "你好，Knowledge Forge!"}],
    }

    try:
        # Send the request to the API
        url = f"{local_url}/v1/responses"
        print(f"Sending request to: {url}")
        print(f"Request data: {json.dumps(request_json, ensure_ascii=False, indent=2)}")

        response = requests.post(url, json=request_json)
        response.raise_for_status()

        # Parse the response using the Response model
        response_data = response.json()
        print("\nResponse received:")
        print(json.dumps(response_data, ensure_ascii=False, indent=2))

        # Process the response directly from JSON
        print("\nResponse processed successfully")

        # Print some information from the parsed response
        response_id = response_data.get("id")
        print(f"Response ID: {response_id}")
        print(f"Model used: {response_data.get('model')}")

        # Extract and print the actual text content
        for output_item in response_data.get("output", []):
            if output_item.get("type") == "message":
                for content_item in output_item.get("content", []):
                    if content_item.get("type") == "output_text":
                        print(f"\nResponse text: {content_item.get('text', '')}")

        # If we have a response ID, try to fetch it again using the API
        if response_id:
            fetch_response_by_id(response_id)

        return response_data

    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"Server error details: {json.dumps(error_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Server error response (non-JSON): {e.response.text[:500]}")
        return None


def fetch_response_by_id(response_id):
    """Fetch a response by its ID using the Knowledge Forge API."""
    try:
        # Construct the URL to get the response by ID
        url = f"{local_url}/v1/responses/{response_id}"
        print(f"\nFetching response by ID from: {url}")

        # Send GET request to retrieve the response
        response = requests.get(url)
        response.raise_for_status()

        # Parse and display the fetched response
        fetched_response = response.json()
        print("\nFetched response by ID:")
        print(json.dumps(fetched_response, ensure_ascii=False, indent=2))

        # Verify if the fetched response matches the original
        print(f"\nVerified response ID: {fetched_response.get('id')}")

        return fetched_response

    except requests.exceptions.RequestException as e:
        print(f"Error fetching response by ID: {e}")
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"Server error details: {json.dumps(error_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Server error response (non-JSON): {e.response.text[:500]}")
        return None


if __name__ == "__main__":
    # Set OpenAI API key if needed (for testing only)
    if not os.environ.get("OPENAI_API_KEY"):
        try:
            with open(os.path.expanduser("~/.openai-api-key")) as f:
                os.environ["OPENAI_API_KEY"] = f.read().strip()
            print("Loaded OpenAI API key from ~/.openai-api-key")
        except Exception:
            print("Warning: No OPENAI_API_KEY found in environment or ~/.openai-api-key")
            print("You may need to set this manually for the API to work")

    send_hello_request()
