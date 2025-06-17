from forge_cli.response._types import Response

# Import typed API functions for example_response_usage
from .types import File


def print_file_results(upload_result: File) -> None:
    """Print formatted file upload results."""
    if upload_result:
        print(f"File uploaded: {upload_result.filename}")
        print(f"File ID: {upload_result.id}")
        print(f"Size: {upload_result.bytes} bytes")
        if upload_result.task_id:
            print(f"Processing task: {upload_result.task_id}")


def has_tool_calls(response: Response) -> bool:
    """Check if the response contains any tool calls."""
    if not response or not response.output:
        return False
    return any(
        hasattr(item, "type") and ("tool_call" in item.type or item.type == "function_call") for item in response.output
    )


def has_uncompleted_tool_calls(response: Response) -> bool:
    """Check if the response has any uncompleted tool calls."""
    if not response or not response.output:
        return False

    # Check for tool calls that are not completed
    for item in response.output:
        if hasattr(item, "type") and ("tool_call" in item.type or item.type == "function_call"):
            if hasattr(item, "status") and (item.status is None or item.status in ["in_progress", "incomplete"]):
                return True
    return False
