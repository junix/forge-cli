#!/usr/bin/env python3
"""Example usage of the JSON renderer for v3 display system."""

import io

from forge_cli.display.v3.base import Display
from forge_cli.display.v3.renderers.json import JsonDisplayConfig, JsonRenderer


def demo_json_renderer():
    """Demonstrate JSON renderer with different configurations."""
    print("=== JSON Renderer v3 Demo ===\n")

    # Example 1: Basic JSON output to stdout
    print("1. Basic JSON output (pretty printed):")
    config = JsonDisplayConfig(pretty_print=True, include_metadata=True)
    renderer = JsonRenderer(config=config)
    display = Display(renderer)

    # Mock response data - in real usage this comes from the API
    from types import SimpleNamespace

    mock_response = SimpleNamespace(
        id="resp_12345",
        status="completed",
        model="claude-3-sonnet",
        output=[
            SimpleNamespace(
                type="message",
                content=[
                    SimpleNamespace(
                        type="output_text",
                        text="# Hello World\n\nThis is a test response with **markdown** formatting.",
                        annotations=[],
                    )
                ],
            )
        ],
        usage=SimpleNamespace(input_tokens=50, output_tokens=25, total_tokens=75),
    )

    display.handle_response(mock_response)
    display.complete()
    print()

    # Example 2: Compact JSON output
    print("2. Compact JSON output (no indentation):")
    config = JsonDisplayConfig(pretty_print=False, include_usage=True)
    renderer = JsonRenderer(config=config)
    display = Display(renderer)

    display.handle_response(mock_response)
    display.complete()
    print()

    # Example 3: JSON to string buffer (for testing/processing)
    print("3. JSON to string buffer:")
    output_buffer = io.StringIO()
    config = JsonDisplayConfig(pretty_print=True, include_timing=True)
    renderer = JsonRenderer(config=config, output_stream=output_buffer)
    display = Display(renderer)

    display.handle_response(mock_response)
    display.complete()

    json_output = output_buffer.getvalue()
    print(f"Captured JSON output ({len(json_output)} chars):")
    print(json_output)

    # Example 4: File output
    print("4. JSON to file output:")
    import os
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
        temp_filename = temp_file.name

    try:
        config = JsonDisplayConfig(
            pretty_print=True, include_metadata=True, include_timing=True, output_file=temp_filename
        )
        renderer = JsonRenderer(config=config)
        display = Display(renderer)

        display.handle_response(mock_response)
        display.complete()

        # Read back and display
        with open(temp_filename) as f:
            file_content = f.read()
        print(f"File output to {temp_filename}:")
        print(file_content)

    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)

    print("=== Demo Complete ===")


if __name__ == "__main__":
    demo_json_renderer()
