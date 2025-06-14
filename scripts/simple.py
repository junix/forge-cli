#!/usr/bin/env python3
"""
Simple client for Knowledge Forge API.
Sends a basic request matching the specified format.
"""

import json
import os

import requests

BASE_URL = os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999")


def send_simple_request():
    """Send the exact request format specified by the user."""
    request_data = {
        "model": "qwen-max",
        "input": [
            {
                "id": "msg_acb219c0-cbef-4e8a-94dc-1eca0ad623de",
                "role": "user",
                "content": [{"text": "北京六月份平均气温", "type": "input_text"}],
            }
        ],
        "effort": "low",
        "tools": [{"type": "web_search"}],
        "instructions": "You are a helpful assistant that provides concise and accurate information.",
        "temperature": 0.7,
        "maxOutputTokens": 500,
        "store": True,
    }

    print("Sending request to:", f"{BASE_URL}/v1/responses")
    print("Request payload:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))

    try:
        response = requests.post(f"{BASE_URL}/v1/responses", json=request_data, stream=True, timeout=30)

        print(f"\nResponse status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")

        if response.status_code == 200:
            print("\nResponse stream:")
            for line in response.iter_lines():
                if line:
                    line_str = line.decode("utf-8")
                    # Parse Server-Sent Events format
                    if line_str.startswith("data: "):
                        try:
                            # Extract JSON from data field
                            json_str = line_str[6:]  # Remove "data: " prefix
                            json_data = json.loads(json_str)
                            print(json.dumps(json_data, indent=2, ensure_ascii=False))
                        except json.JSONDecodeError:
                            # If it's not valid JSON, print as is
                            print(line_str)
                    else:
                        # Print event lines and other non-data lines as is
                        print(line_str)
        else:
            print(f"Error response: {response.text}")

    except Exception as e:
        print(f"Request failed: {e}")


if __name__ == "__main__":
    send_simple_request()
