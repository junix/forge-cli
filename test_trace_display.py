#!/usr/bin/env python3
"""Test script to verify the new trace block display functionality."""

from src.forge_cli.display.v3.renderers.rich import RichRenderer
from src.forge_cli.response._types.response import Response
from src.forge_cli.response._types.response_function_file_reader import ResponseFunctionFileReader
from src.forge_cli.response._types.response_usage import ResponseUsage


def create_mock_tool_with_trace():
    """Create a mock tool call with execution trace."""
    # Create a mock file reader call with execution trace
    tool_call = ResponseFunctionFileReader(
        id="test_tool_123",
        type="file_reader_call",
        status="in_progress",
        doc_ids=["test_doc_123"],
        query="test query",
        execution_trace="[2024-01-01 10:00:01] Starting file read\n[2024-01-01 10:00:02] Processing chunks\n[2024-01-01 10:00:03] Reading content from file",
    )
    return tool_call


def create_mock_response_with_traceable_tool():
    """Create a mock response with a traceable tool."""
    tool_call = create_mock_tool_with_trace()

    # Create proper usage object with all required fields
    usage = ResponseUsage(
        input_tokens=100,
        output_tokens=50,
        total_tokens=150,
        input_tokens_details=InputTokensDetails(cached_tokens=0),
        output_tokens_details=OutputTokensDetails(reasoning_tokens=10),
    )

    response = Response(
        id="test_response_123",
        status="in_progress",
        output=[tool_call],
        usage=usage,
    )

    return response


def test_trace_block_extraction():
    """Test the _get_trace_block method."""
    renderer = RichRenderer()
    tool_call = create_mock_tool_with_trace()

    # Test trace block extraction
    trace_block = renderer._get_trace_block(tool_call)
    print("Trace block result:")
    if trace_block:
        for line in trace_block:
            print(f"  {line}")
    else:
        print("  No trace block found")

    return trace_block is not None


def test_response_rendering():
    """Test rendering a response with traceable tools."""
    renderer = RichRenderer()
    response = create_mock_response_with_traceable_tool()

    print("\nRendering response with traceable tool...")
    try:
        # This will create the rich content but not display it
        content = renderer._create_response_content(response)
        print("✓ Response rendering successful")
        return True
    except Exception as e:
        print(f"✗ Response rendering failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Testing new trace block display functionality...\n")

    # Test 1: Trace block extraction
    print("Test 1: Trace block extraction")
    test1_passed = test_trace_block_extraction()
    print(f"Result: {'✓ PASSED' if test1_passed else '✗ FAILED'}\n")

    # Test 2: Response rendering
    print("Test 2: Response rendering")
    test2_passed = test_response_rendering()
    print(f"Result: {'✓ PASSED' if test2_passed else '✗ FAILED'}\n")

    # Summary
    all_passed = test1_passed and test2_passed
    print(f"Overall result: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")

    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
