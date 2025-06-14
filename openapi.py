#!/usr/bin/env python3
import json
import os

import requests
from rich.console import Console
from rich.syntax import Syntax

# Use environment variable for server URL if available, otherwise default to localhost
local_url = os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999")


def fetch_openapi_json():
    """Fetch the OpenAPI JSON specification from the Knowledge Forge API."""
    try:
        # Construct the URL for the OpenAPI JSON
        url = f"{local_url}/openapi.json"
        print(f"Fetching OpenAPI specification from: {url}")

        # Send the GET request
        response = requests.get(url)
        response.raise_for_status()

        # Parse the response
        openapi_data = response.json()

        # Display the OpenAPI JSON using rich for better formatting
        console = Console()
        console.print("\nOpenAPI Specification:")

        # Convert to formatted JSON string
        formatted_json = json.dumps(openapi_data, indent=2)

        # Display with syntax highlighting
        syntax = Syntax(formatted_json, "json", theme="monokai", line_numbers=True)
        console.print(syntax)

        # Just print to console, don't write to file

        return openapi_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching OpenAPI specification: {e}")
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"Server error details: {json.dumps(error_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Server error response (non-JSON): {e.response.text[:500]}")
        return None


if __name__ == "__main__":
    fetch_openapi_json()
