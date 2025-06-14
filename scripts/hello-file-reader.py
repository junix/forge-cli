#!/usr/bin/env python3
"""
File reader example using the Knowledge Forge SDK.

This script demonstrates how to use the SDK to create a response that reads
from file content, enabling document-grounded conversations with the model.

Features:
- Support for multiple file IDs
- Two streaming methods: callback-based and async iterator-based
- Display of document information
- Rich command line interface with customizable options
- Pretty output formatting with optional colors
"""

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

# For error handling
import aiohttp

# Rich library for better terminal output
try:
    from rich import print as rich_print
    from rich.console import Console
    from rich.live import Live
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.text import Text

    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# Add the current directory to sys.path to allow importing from current directory
sys.path.insert(0, str(Path(__file__).parent))

# Import SDK functions from local sdk.py
from sdk import astream_response, async_create_response, async_fetch_file

# Color support for terminal output
try:
    import colorama
    from colorama import Fore, Style

    colorama.init()
    HAS_COLORS = True
except ImportError:
    HAS_COLORS = False

    # Mock color classes if colorama is not available
    class MockColor:
        def __getattr__(self, name):
            return ""

    Fore = Style = MockColor()

# Default file IDs to use if none are provided
DEFAULT_FILE_IDS = ["ad520a0c-ed3d-4e6a-8c30-7f2d398be065"]


async def process_with_callback(
    question: str,
    file_ids: list[str],
    model: str = "qwen-max-latest",
    effort: str = "low",
    debug: bool = False,
    no_color: bool = False,
    json_output: bool = False,
    throttle_ms: int = 0,
) -> dict[str, Any] | None:
    """
    Send a request using the callback approach for streaming.

    Args:
        question: Question to ask about the file content
        file_ids: List of file IDs to read from
        model: Model to use for the response
        effort: Effort level for the response (low, medium, high)
        debug: Whether to show debug information
        no_color: Disable colored output
        json_output: Output the final response as JSON
        throttle_ms: Throttle the output by adding a delay between tokens (in milliseconds)

    Returns:
        The API response if successful, None otherwise
    """
    start_time = time.time()

    # Create file reference content for each file ID
    file_id_content = [{"type": "input_file", "file_id": file_id} for file_id in file_ids]

    # Create input messages with file references and question
    input_messages = [
        {
            "id": "1",
            "role": "user",
            "content": [
                *file_id_content,
                {"type": "input_text", "text": question},
            ],
        },
    ]

    print(f"Input messages: {input_messages}")

    # Skip pretty printing in JSON mode
    if not json_output:
        if no_color:
            print("\n📄 Request Information:")
            print(f"  💬 Question: {question}")
            print(f"  📚 File IDs: {', '.join(file_ids)}")
            print(f"  🤖 Model: {model}")
            print(f"  ⚙️ Effort Level: {effort}")
            print("\n🔄 Streaming response (please wait):")
            print("=" * 80)
        else:
            print(f"\n{Fore.CYAN}📄 Request Information:{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}💬 Question:{Style.RESET_ALL} {question}")
            print(f"  {Fore.GREEN}📚 File IDs:{Style.RESET_ALL} {', '.join(file_ids)}")
            print(f"  {Fore.GREEN}🤖 Model:{Style.RESET_ALL} {model}")
            print(f"  {Fore.GREEN}⚙️ Effort Level:{Style.RESET_ALL} {effort}")
            if throttle_ms > 0:
                print(f"  {Fore.GREEN}⏱️ Throttle:{Style.RESET_ALL} {throttle_ms}ms per token")
            print(f"\n{Fore.YELLOW}🔄 Streaming response (please wait):{Style.RESET_ALL}")
            print(f"{Fore.BLUE}{'=' * 80}{Style.RESET_ALL}")

    # Track complete response text for callback method
    complete_text = ""

    # Create a custom streaming callback that handles throttling and colors
    async def custom_callback(event):
        nonlocal complete_text
        event_type = event["type"]
        data = event["data"] or {}

        # Print debug information if requested
        if debug and not json_output:
            debug_prefix = f"{Fore.MAGENTA}DEBUG:{Style.RESET_ALL} " if not no_color else "DEBUG: "
            print(f"\n{debug_prefix}{event_type}")
            print(f"{debug_prefix}{json.dumps(data, indent=2, ensure_ascii=False)}")

        # Handle text streaming for user display
        if event_type == "response.output_text.delta" and data and "text" in data:
            if not json_output:  # Only print streaming output in normal mode
                text_content = data["text"]

                # Extract the actual text from the event data, which can be nested
                fragment = ""
                if isinstance(text_content, dict) and "text" in text_content:
                    fragment = text_content["text"]
                elif isinstance(text_content, str):
                    fragment = text_content

                # Now handle output for the output field structure (data["id"] is the response ID)
                # Get the text from the response output if available
                if "output" in data and isinstance(data["output"], list):
                    for msg in data["output"]:
                        if msg.get("role") == "assistant" and isinstance(msg.get("content"), list):
                            for item in msg["content"]:
                                if item.get("type") == "output_text" and isinstance(item.get("text"), str):
                                    fragment = item["text"]

                # Add fragment to complete text and print it
                if fragment:
                    # Determine if this fragment is a completely new text or an addition to the existing text
                    is_new_text = False
                    if len(fragment) >= len(complete_text):
                        # This is likely a new complete text rather than an incremental update
                        is_new_text = True

                    if is_new_text:
                        # Clear the current line completely by going to the beginning and printing spaces
                        # Then reprint the entire fragment
                        print("\r", end="")
                        # Use ANSI escape to clear the line
                        print("\033[K", end="")
                        if not no_color:
                            print(
                                f"{Fore.WHITE}{fragment}{Style.RESET_ALL}",
                                end="",
                                flush=True,
                            )
                        else:
                            print(f"{fragment}", end="", flush=True)
                        complete_text = fragment
                    elif not complete_text or fragment.startswith(complete_text):
                        # Only print the new part if fragment is a superset of complete_text
                        new_part = fragment[len(complete_text) :]
                        if not no_color:
                            print(
                                f"{Fore.WHITE}{new_part}{Style.RESET_ALL}",
                                end="",
                                flush=True,
                            )
                        else:
                            print(new_part, end="", flush=True)
                        complete_text = fragment
                    else:
                        # If the new fragment doesn't seem to be related to the existing text,
                        # clear the line and start fresh
                        print("\r", end="")
                        print("\033[K", end="")
                        if not no_color:
                            print(
                                f"{Fore.WHITE}{fragment}{Style.RESET_ALL}",
                                end="",
                                flush=True,
                            )
                        else:
                            print(f"{fragment}", end="", flush=True)
                        complete_text = fragment

                    # Apply throttling if requested
                    if throttle_ms > 0:
                        await asyncio.sleep(throttle_ms / 1000)

        # Handle error events
        if event_type == "response.error" and not json_output:
            error_prefix = f"{Fore.RED}Error:{Style.RESET_ALL} " if not no_color else "Error: "
            print(f"\n{error_prefix}{data.get('message', 'Unknown error occurred')}")

    # Send the request using the SDK with callback for streaming
    try:
        response = await async_create_response(
            input_messages=input_messages,
            model=model,
            effort=effort,
            store=True,
            callback=custom_callback,
        )

        end_time = time.time()
        duration = end_time - start_time

        if json_output:
            # In JSON mode, just output the raw response
            print(json.dumps(response, indent=2, ensure_ascii=False))
            return response

        if response:
            # Check if there's actual text content in the response
            has_content = False
            content_text = ""

            # Log the response structure for debugging
            if debug:
                print(f"\nResponse structure: {json.dumps(response, indent=2, ensure_ascii=False)}")

            # Extract text content based on the response structure
            if isinstance(response, dict):
                # The output field contains the messages
                if "output" in response and isinstance(response["output"], list):
                    for msg in response["output"]:
                        if msg.get("role") == "assistant" and isinstance(msg.get("content"), list):
                            # Process each content item in the message
                            for item in msg["content"]:
                                if item.get("type") == "output_text" and isinstance(item.get("text"), str):
                                    has_content = True
                                    content_text += item["text"]

            if no_color:
                print("\n" + "=" * 80)
                print("\n✅ Response completed successfully!")
                print(f"  🆔 Response ID: {response.get('id')}")
                print(f"  🤖 Model used: {response.get('model')}")
                print(f"  ⏱️ Time taken: {duration:.2f} seconds")
            else:
                print(f"\n{Fore.BLUE}{'=' * 80}{Style.RESET_ALL}")
                print(f"\n{Fore.GREEN}✅ Response completed successfully!{Style.RESET_ALL}")
                print(f"  {Fore.YELLOW}🆔 Response ID:{Style.RESET_ALL} {response.get('id')}")
                print(f"  {Fore.YELLOW}🤖 Model used:{Style.RESET_ALL} {response.get('model')}")
                print(f"  {Fore.YELLOW}⏱️ Time taken:{Style.RESET_ALL} {duration:.2f} seconds")

            # Display document info for better context
            await display_file_info(file_ids, no_color)

            # Show content if found, or a warning if not
            if has_content:
                if no_color:
                    print("\n📃 Response Content:")
                    print(f"{content_text}")
                else:
                    print(f"\n{Fore.CYAN}📃 Response Content:{Style.RESET_ALL}")
                    print(f"{Fore.WHITE}{content_text}{Style.RESET_ALL}")
            else:
                if no_color:
                    print("\n⚠️  Warning: No text content found in the response.")
                else:
                    print(f"\n{Fore.YELLOW}⚠️  Warning:{Style.RESET_ALL} No text content found in the response.")

            return response
        else:
            if no_color:
                print("\n❌ Failed to get response")
            else:
                print(f"\n{Fore.RED}❌ Failed to get response{Style.RESET_ALL}")
            return None

    except Exception as e:
        if no_color:
            print(f"\n❌ Error sending request: {e}")
        else:
            print(f"\n{Fore.RED}❌ Error sending request: {e}{Style.RESET_ALL}")
        return None


async def process_with_streaming(
    question: str,
    file_ids: list[str],
    model: str = "qwen-max-latest",
    effort: str = "low",
    debug: bool = False,
    no_color: bool = False,
    json_output: bool = False,
    throttle_ms: int = 0,
) -> dict[str, Any] | None:
    """
    Send a request using the astream_response approach for streaming.

    Args:
        question: Question to ask about the file content
        file_ids: List of file IDs to read from
        model: Model to use for the response
        effort: Effort level for the response (low, medium, high)
        debug: Whether to show debug information
        no_color: Disable colored output
        json_output: Output the final response as JSON
        throttle_ms: Throttle the output by adding a delay between tokens (in milliseconds)

    Returns:
        The API response if successful, None otherwise
    """
    start_time = time.time()

    # Create file reference content for each file ID
    file_id_content = [{"type": "input_file", "file_id": file_id} for file_id in file_ids]

    # Create input messages with file references and question
    input_messages = [
        {
            "role": "user",
            "id": "user_message_1",  # Add required ID field
            "content": [
                *file_id_content,
                {"type": "input_text", "text": question},
            ],
        },
    ]

    # Setup display - use rich if available, fallback to standard output
    use_rich = HAS_RICH and not no_color and not json_output
    rich_console = Console() if use_rich else None

    # Print request information
    if not json_output:
        if use_rich:
            # Create a rich panel for request information
            request_info = Text()
            request_info.append("\n📄 Request Information:\n", style="cyan bold")
            request_info.append("  💬 Question: ", style="green")
            request_info.append(f"{question}\n")
            request_info.append("  📚 File IDs: ", style="green")
            request_info.append(f"{', '.join(file_ids)}\n")
            request_info.append("  🤖 Model: ", style="green")
            request_info.append(f"{model}\n")
            request_info.append("  ⚙️ Effort Level: ", style="green")
            request_info.append(f"{effort}\n")
            request_info.append("  🔄 Method: ", style="green")
            request_info.append("Direct streaming with Rich Live Display\n")
            if throttle_ms > 0:
                request_info.append("  ⏱️ Throttle: ", style="green")
                request_info.append(f"{throttle_ms}ms per token\n")

            rich_console.print(request_info)
            rich_console.print(Text("\n🔄 Streaming response (please wait):", style="yellow bold"))
            rich_console.print("=" * 80, style="blue")
        elif no_color:
            print("\n📄 Request Information:")
            print(f"  💬 Question: {question}")
            print(f"  📚 File IDs: {', '.join(file_ids)}")
            print(f"  🤖 Model: {model}")
            print(f"  ⚙️ Effort Level: {effort}")
            print("  🔄 Method: Direct streaming")
            print("\n🔄 Streaming response (please wait):")
            print("=" * 80)
        else:
            print(f"\n{Fore.CYAN}📄 Request Information:{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}💬 Question:{Style.RESET_ALL} {question}")
            print(f"  {Fore.GREEN}📚 File IDs:{Style.RESET_ALL} {', '.join(file_ids)}")
            print(f"  {Fore.GREEN}🤖 Model:{Style.RESET_ALL} {model}")
            print(f"  {Fore.GREEN}⚙️ Effort Level:{Style.RESET_ALL} {effort}")
            print(f"  {Fore.GREEN}🔄 Method:{Style.RESET_ALL} Direct streaming")
            if throttle_ms > 0:
                print(f"  {Fore.GREEN}⏱️ Throttle:{Style.RESET_ALL} {throttle_ms}ms per token")
            print(f"\n{Fore.YELLOW}🔄 Streaming response (please wait):{Style.RESET_ALL}")
            print(f"{Fore.BLUE}{'=' * 80}{Style.RESET_ALL}")

    # Variables to track streaming progress
    complete_text = ""
    final_response = None

    # Set up Rich Live display if available
    if use_rich:
        # Create a live display context
        live_display = Live(Panel(""), refresh_per_second=10, console=rich_console, transient=False)
        live_display.start()
    else:
        live_display = None

    try:
        # Process the streaming response
        async for event_type, event_data in astream_response(
            input_messages=input_messages,
            model=model,
            effort=effort,
            store=True,
            debug=debug,
        ):
            # Print debug information if requested
            if debug and event_data and not json_output:
                debug_prefix = f"{Fore.MAGENTA}DEBUG:{Style.RESET_ALL} " if not no_color else "DEBUG: "
                print(f"\n{debug_prefix}{event_type}")
                print(f"{debug_prefix}{json.dumps(event_data, indent=2, ensure_ascii=False)}")

            # Handle text delta events to build the response
            if event_type == "response.output_text.delta" and event_data and "text" in event_data:
                if not json_output:  # Only print streaming output in normal mode
                    text_content = event_data["text"]

                    # Extract the actual text from the event data, which can be nested
                    fragment = ""
                    if isinstance(text_content, dict) and "text" in text_content:
                        fragment = text_content["text"]
                    elif isinstance(text_content, str):
                        fragment = text_content

                    # Now handle output for the output field structure (event_data["id"] is the response ID)
                    # Get the text from the response output if available
                    if "output" in event_data and isinstance(event_data["output"], list):
                        for msg in event_data["output"]:
                            if msg.get("role") == "assistant" and isinstance(msg.get("content"), list):
                                for item in msg["content"]:
                                    if item.get("type") == "output_text" and isinstance(item.get("text"), str):
                                        fragment = item["text"]

                    # Process the fragment
                    if fragment:
                        # Determine if this is a completely new text
                        is_new_text = len(fragment) >= len(complete_text)

                        # Update the complete text
                        if is_new_text:
                            complete_text = fragment
                        elif not complete_text or fragment.startswith(complete_text):
                            complete_text = fragment
                        else:
                            complete_text = fragment

                        # Update display based on method
                        if use_rich:
                            # Update the Rich Live display with the complete text
                            live_display.update(
                                Panel(
                                    Text(complete_text),
                                    title="AI Response",
                                    border_style="green",
                                )
                            )
                        else:
                            # Use the previous approach for terminal without Rich
                            if is_new_text:
                                print("\r", end="")
                                print("\033[K", end="")  # Clear line
                                if not no_color:
                                    print(
                                        f"{Fore.WHITE}{fragment}{Style.RESET_ALL}",
                                        end="",
                                        flush=True,
                                    )
                                else:
                                    print(f"{fragment}", end="", flush=True)
                            elif not complete_text or fragment.startswith(complete_text):
                                new_part = fragment[len(complete_text) :]
                                if not no_color:
                                    print(
                                        f"{Fore.WHITE}{new_part}{Style.RESET_ALL}",
                                        end="",
                                        flush=True,
                                    )
                                else:
                                    print(new_part, end="", flush=True)
                            else:
                                print("\r", end="")
                                print("\033[K", end="")
                                if not no_color:
                                    print(
                                        f"{Fore.WHITE}{fragment}{Style.RESET_ALL}",
                                        end="",
                                        flush=True,
                                    )
                                else:
                                    print(f"{fragment}", end="", flush=True)

                        # Apply throttling if requested
                        if throttle_ms > 0:
                            await asyncio.sleep(throttle_ms / 1000)

            # Handle error events
            if event_type == "error" and event_data and not json_output:
                error_message = event_data.get("message", "Unknown error occurred")
                if use_rich:
                    error_panel = Panel(
                        Text(f"Error: {error_message}", style="red bold"),
                        title="Error",
                        border_style="red",
                    )
                    live_display.update(error_panel)
                else:
                    error_prefix = f"{Fore.RED}Error:{Style.RESET_ALL} " if not no_color else "Error: "
                    print(f"\n{error_prefix}{error_message}")

            # Save final response when completed
            if event_type == "final_response":
                final_response = event_data

            # Exit on done event
            if event_type == "done":
                break

        # Stop the live display if it's running
        if use_rich and live_display:
            live_display.stop()

        end_time = time.time()
        duration = end_time - start_time

        if json_output and final_response:
            # In JSON mode, just output the raw response
            print(json.dumps(final_response, indent=2, ensure_ascii=False))
            return final_response

        if not json_output and not use_rich:
            if no_color:
                print("=" * 80)
            else:
                print(f"{Fore.BLUE}{'=' * 80}{Style.RESET_ALL}")

        if final_response:
            # Check if there's actual text content in the response
            has_content = False
            content_text = ""

            # Log the response structure for debugging
            if debug:
                print(f"\nResponse structure: {json.dumps(final_response, indent=2, ensure_ascii=False)}")

            # Extract text content based on the response structure
            if isinstance(final_response, dict):
                # The output field contains the messages
                if "output" in final_response and isinstance(final_response["output"], list):
                    for msg in final_response["output"]:
                        if msg.get("role") == "assistant" and isinstance(msg.get("content"), list):
                            # Process each content item in the message
                            for item in msg["content"]:
                                if item.get("type") == "output_text" and isinstance(item.get("text"), str):
                                    has_content = True
                                    content_text += item["text"]

            if not json_output:
                # Display completion information
                if use_rich:
                    completion_info = Text()
                    completion_info.append("\n✅ Response completed successfully!\n", style="green bold")
                    completion_info.append("  🆔 Response ID: ", style="yellow")
                    completion_info.append(f"{final_response.get('id')}\n")
                    completion_info.append("  🤖 Model used: ", style="yellow")
                    completion_info.append(f"{final_response.get('model')}\n")
                    completion_info.append("  ⏱️ Time taken: ", style="yellow")
                    completion_info.append(f"{duration:.2f} seconds\n")

                    rich_console.print(completion_info)
                elif no_color:
                    print("\n✅ Response completed successfully!")
                    print(f"  🆔 Response ID: {final_response.get('id')}")
                    print(f"  🤖 Model used: {final_response.get('model')}")
                    print(f"  ⏱️ Time taken: {duration:.2f} seconds")
                else:
                    print(f"\n{Fore.GREEN}✅ Response completed successfully!{Style.RESET_ALL}")
                    print(f"  {Fore.YELLOW}🆔 Response ID:{Style.RESET_ALL} {final_response.get('id')}")
                    print(f"  {Fore.YELLOW}🤖 Model used:{Style.RESET_ALL} {final_response.get('model')}")
                    print(f"  {Fore.YELLOW}⏱️ Time taken:{Style.RESET_ALL} {duration:.2f} seconds")

                # Display document info for better context
                await display_file_info(file_ids, no_color or use_rich)

                # Show content if found, or a warning if not
                if has_content:
                    if use_rich:
                        rich_console.print(Text("\n📃 Response Content:", style="cyan bold"))
                        # Try to show as markdown if possible
                        try:
                            rich_console.print(Markdown(content_text))
                        except Exception:
                            # Fallback to plain text if markdown parsing fails
                            rich_console.print(Text(content_text))
                    elif no_color:
                        print("\n📃 Response Content:")
                        print(f"{content_text}")
                    else:
                        print(f"\n{Fore.CYAN}📃 Response Content:{Style.RESET_ALL}")
                        print(f"{Fore.WHITE}{content_text}{Style.RESET_ALL}")
                else:
                    warning_msg = "⚠️  Warning: No text content found in the response."
                    if use_rich:
                        rich_console.print(Text(warning_msg, style="yellow"))
                    elif no_color:
                        print(f"\n{warning_msg}")
                    else:
                        print(f"\n{Fore.YELLOW}{warning_msg}{Style.RESET_ALL}")

            return final_response
        else:
            error_msg = "❌ No final response received."
            if not json_output:
                if use_rich:
                    rich_console.print(Text(error_msg, style="red bold"))
                elif no_color:
                    print(f"\n{error_msg}")
                else:
                    print(f"\n{Fore.RED}{error_msg}{Style.RESET_ALL}")
            return None

    except Exception as e:
        if not json_output:
            error_msg = f"❌ Error during streaming request: {e}"
            if use_rich:
                # Make sure to stop the live display before showing error
                if live_display:
                    live_display.stop()
                rich_console.print(Text(error_msg, style="red bold"))
            elif no_color:
                print(f"\n{error_msg}")
            else:
                print(f"\n{Fore.RED}{error_msg}{Style.RESET_ALL}")
        return None


async def display_file_info(file_ids: list[str], no_color: bool = False) -> None:
    """
    Display information about the files being used in the response.

    Args:
        file_ids: List of file IDs to display information for
        no_color: Whether to disable colored output
    """
    # Check if we should use rich for display
    use_rich = HAS_RICH and not no_color
    rich_console = Console() if use_rich else None

    if use_rich:
        rich_console.print(Text("\n📚 Document Information:", style="cyan bold"))
    elif no_color:
        print("\n📚 Document Information:")
    else:
        print(f"\n{Fore.CYAN}📚 Document Information:{Style.RESET_ALL}")

    for i, file_id in enumerate(file_ids, 1):
        try:
            file_info = await async_fetch_file(file_id)
            if file_info:
                if use_rich:
                    # Create a rich table for file info
                    file_table = Text()
                    file_table.append(f"  📄 Document #{i}:\n", style="blue bold")
                    file_table.append("    🔑 ID: ", style="yellow")
                    file_table.append(f"{file_id}\n")
                    file_table.append("    📝 Title: ", style="yellow")
                    file_table.append(f"{file_info.get('title', 'Unknown')}\n")
                    file_table.append("    📂 Filename: ", style="yellow")
                    file_table.append(f"{file_info.get('filename', 'Unknown')}\n")
                    file_table.append("    📊 Size: ", style="yellow")
                    file_table.append(f"{format_size(file_info.get('bytes', 0))}\n")

                    # Show content type if available
                    if file_info.get("content") and file_info["content"].get("file_type"):
                        file_table.append("    🔖 Type: ", style="yellow")
                        file_table.append(f"{file_info['content']['file_type']}\n")

                    # Show creation date if available
                    if file_info.get("created_at"):
                        file_table.append("    🕒 Created: ", style="yellow")
                        file_table.append(f"{file_info.get('created_at')}\n")

                    rich_console.print(file_table)
                elif no_color:
                    print(f"  📄 Document #{i}:")
                    print(f"    🔑 ID: {file_id}")
                    print(f"    📝 Title: {file_info.get('title', 'Unknown')}")
                    print(f"    📂 Filename: {file_info.get('filename', 'Unknown')}")
                    print(f"    📊 Size: {format_size(file_info.get('bytes', 0))}")
                else:
                    print(f"  {Fore.BLUE}📄 Document #{i}:{Style.RESET_ALL}")
                    print(f"    {Fore.YELLOW}🔑 ID:{Style.RESET_ALL} {file_id}")
                    print(f"    {Fore.YELLOW}📝 Title:{Style.RESET_ALL} {file_info.get('title', 'Unknown')}")
                    print(f"    {Fore.YELLOW}📂 Filename:{Style.RESET_ALL} {file_info.get('filename', 'Unknown')}")
                    print(f"    {Fore.YELLOW}📊 Size:{Style.RESET_ALL} {format_size(file_info.get('bytes', 0))}")

                # Show content type if available (for non-rich display)
                if not use_rich and file_info.get("content") and file_info["content"].get("file_type"):
                    if no_color:
                        print(f"    🔖 Type: {file_info['content']['file_type']}")
                    else:
                        print(f"    {Fore.YELLOW}🔖 Type:{Style.RESET_ALL} {file_info['content']['file_type']}")

                # Show creation date if available (for non-rich display)
                if not use_rich and file_info.get("created_at"):
                    if no_color:
                        print(f"    🕒 Created: {file_info.get('created_at')}")
                    else:
                        print(f"    {Fore.YELLOW}🕒 Created:{Style.RESET_ALL} {file_info.get('created_at')}")
            else:
                if use_rich:
                    error_text = Text()
                    error_text.append(f"  ❓ Document #{i}:\n", style="yellow")
                    error_text.append(f"    🔑 ID: {file_id}\n")
                    error_text.append("    ⚠️ Status: Unable to fetch file details\n", style="red")
                    rich_console.print(error_text)
                elif no_color:
                    print(f"  ❓ Document #{i}:")
                    print(f"    🔑 ID: {file_id}")
                    print("    ⚠️ Status: Unable to fetch file details")
                else:
                    print(f"  {Fore.YELLOW}❓ Document #{i}:{Style.RESET_ALL}")
                    print(f"    {Fore.YELLOW}🔑 ID:{Style.RESET_ALL} {file_id}")
                    print(f"    {Fore.RED}⚠️ Status:{Style.RESET_ALL} Unable to fetch file details")
        except Exception as e:
            if use_rich:
                error_text = Text()
                error_text.append(f"  ❌ Document #{i}:\n", style="red bold")
                error_text.append(f"    🔑 ID: {file_id}\n")
                error_text.append(f"    🚫 Error: {e}\n", style="red")
                rich_console.print(error_text)
            elif no_color:
                print(f"  ❌ Document #{i}:")
                print(f"    🔑 ID: {file_id}")
                print(f"    🚫 Error: {e}")
            else:
                print(f"  {Fore.RED}❌ Document #{i}:{Style.RESET_ALL}")
                print(f"    {Fore.YELLOW}🔑 ID:{Style.RESET_ALL} {file_id}")
                print(f"    {Fore.RED}🚫 Error:{Style.RESET_ALL} {e}")


def format_size(size_bytes: int) -> str:
    """
    Format file size from bytes to a human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Human-readable size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


async def main():
    """Main function to handle command line arguments and run the request."""
    # Check if no arguments provided
    show_help = len(sys.argv) == 1

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Send requests to Knowledge Forge API with file reading capabilities",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--file-id",
        nargs="+",
        default=DEFAULT_FILE_IDS,
        help="File ID(s) to read from (can specify multiple)",
    )
    parser.add_argument(
        "--question",
        "-q",
        type=str,
        default="What information can you find in the document?",
        help="Question to ask about the file content",
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default="qwen-max-latest",
        help="Model to use for the response",
    )
    parser.add_argument(
        "--effort",
        "-e",
        type=str,
        choices=["low", "medium", "high", "dev"],
        default="low",
        help="Effort level for the response",
    )
    parser.add_argument(
        "--method",
        type=str,
        choices=["callback", "stream"],
        default="stream",
        help="Method to use for streaming (callback or stream)",
    )
    parser.add_argument(
        "--server",
        default=os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999"),
        help="Server URL (default: from env or http://localhost:9999)",
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Enable debug output with detailed event information",
    )
    parser.add_argument(
        "--info",
        "-i",
        action="store_true",
        help="Only display file information without sending a query",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the response as JSON",
    )
    parser.add_argument(
        "--throttle",
        type=int,
        default=0,
        help="Throttle the output by adding a delay between tokens (in milliseconds)",
    )
    parser.add_argument(
        "--save",
        type=str,
        help="Save the response to a file",
    )
    parser.add_argument(
        "--quiet",
        "-Q",
        action="store_true",
        help="Quiet mode - minimal output (implies --no-color)",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="store_true",
        help="Show version information and exit",
    )

    args = parser.parse_args()

    # Show help if no arguments provided and not asking for help directly
    if show_help and not any(arg in sys.argv for arg in ["-h", "--help"]):
        parser.print_help()
        print("\nExample usage:")
        print('  python -m commands.hello-file-reader -q "Summarize this document"')
        print("  python -m commands.hello-file-reader --file-id file_id1 file_id2 --model qwen-max --effort medium")
        print("  python -m commands.hello-file-reader --file-id file_id1 --effort dev --debug")
        print("  python -m commands.hello-file-reader --method callback --debug")
        return

    # Handle version display
    if args.version:
        version = "1.0.0"  # You can use a more sophisticated version management
        print(f"Knowledge Forge File Reader v{version}")
        print("Part of the Knowledge Forge SDK toolkit")
        return

    # Handle quiet mode
    if args.quiet:
        args.no_color = True

    # Handle color disabling if not supported or requested
    if not HAS_COLORS or args.no_color:
        args.no_color = True

    # Set server URL if provided
    if args.server != os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999"):
        os.environ["KNOWLEDGE_FORGE_URL"] = args.server
        if not args.quiet:
            print(f"🔗 Using server: {args.server}")

    # If info mode, just display file information
    if args.info:
        if not args.quiet:
            print(f"ℹ️ File Information Mode - Fetching details for {len(args.file_id)} file(s)")
        await display_file_info(args.file_id, args.no_color)
        return

    # Run the appropriate method
    response = None

    if args.method == "callback":
        if not args.quiet and not args.json:
            print("🔄 Using callback streaming method")
        response = await process_with_callback(
            question=args.question,
            file_ids=args.file_id,
            model=args.model,
            effort=args.effort,
            debug=args.debug,
            no_color=args.no_color,
            json_output=args.json,
            throttle_ms=args.throttle,
        )
    else:
        if not args.quiet and not args.json:
            print("🔄 Using direct streaming method")
        response = await process_with_streaming(
            question=args.question,
            file_ids=args.file_id,
            model=args.model,
            effort=args.effort,
            debug=args.debug,
            no_color=args.no_color,
            json_output=args.json,
            throttle_ms=args.throttle,
        )

    # Save response to file if requested
    if args.save and response:
        try:
            with open(args.save, "w", encoding="utf-8") as f:
                if args.json:
                    # Save the full response
                    json.dump(response, f, indent=2, ensure_ascii=False)
                else:
                    # Save just the text response
                    for msg in response.get("output", []):
                        if msg.get("role") == "assistant" and "content" in msg:
                            content = msg["content"]
                            if isinstance(content, list):
                                for item in content:
                                    if item.get("type") == "text":
                                        f.write(f"{item.get('text', '')}\n")
                            else:
                                f.write(f"{content}\n")

            if not args.quiet and not args.json:
                print(f"\n💾 Response saved to: {args.save}")
        except Exception as e:
            if not args.quiet and not args.json:
                if args.no_color:
                    print(f"\n❌ Error saving response to file: {e}")
                else:
                    print(f"\n{Fore.RED}❌ Error saving response to file: {e}{Style.RESET_ALL}")


def handle_exceptions(func):
    """
    Decorator to handle exceptions gracefully.

    Args:
        func: The async function to wrap

    Returns:
        A wrapper function that handles exceptions
    """

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\n\nOperation canceled by user.")
            return None
        except aiohttp.ClientConnectorError as e:
            print(
                f"\n❌ Connection error: Could not connect to server. Is the server running at {os.environ.get('KNOWLEDGE_FORGE_URL')}?"
            )
            print(f"  Error details: {e}")
            return None
        except aiohttp.ClientResponseError as e:
            print(f"\n❌ Server error: The server returned an error: {e.status} {e.message}")
            return None
        except Exception as e:
            print(f"\n❌ Unexpected error: {type(e).__name__}: {e}")
            if "--debug" in sys.argv or "-d" in sys.argv:
                import traceback

                traceback.print_exc()
            return None

    return wrapper


if __name__ == "__main__":
    # Apply the exception handler decorator to main
    wrapped_main = handle_exceptions(main)

    try:
        asyncio.run(wrapped_main())
    except KeyboardInterrupt:
        print("\n\nOperation canceled by user.")
    except Exception as e:
        print(f"\n❌ Fatal error: {type(e).__name__}: {e}")
        if "--debug" in sys.argv or "-d" in sys.argv:
            import traceback

            traceback.print_exc()
        sys.exit(1)
