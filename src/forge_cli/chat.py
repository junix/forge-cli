#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path

import requests
from json_live import JsonLive
from rich.align import Align
from rich.box import SIMPLE
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.text import Text

# Use environment variable for server URL if available, otherwise default to localhost
BASE_URL = os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999")

# Fields that shouldn't be displayed in the JSON output
NO_DISPLAY_FIELDS = (
    "id",
    "usage",
    "text",
    "parallel_tool_calls",
    "temperature",
    "tool_choice",
    "tools",
    "top_p",
    "max_output_tokens",
    "previous_response_id",
    "reasoning",
    "service_tier",
    "status",
    "truncation",
    "user",
    "effort",
    "top_logprobs",
    "created_at",
    "metadata",
    "model",
    "object",
    # Additional fields from the sample
    "format",
    "filters",
    "vector_store_ids",
    "max_num_results",
    "ranking_options",
    "generate_summary",
    "summary",
    "summary_detail",
    "input_tokens",
    "input_tokens_details",
    "output_tokens",
    "output_tokens_details",
    "total_tokens",
    "type",
)


class Chat:
    def __init__(self, console=None, effort="low"):
        self.console = console or Console()
        self.json_live = None
        self.current_event_type = ""
        self.events = []  # List to store all events
        self.usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
        self.chat_history = []
        self.effort = effort

    def process_event_type(self, line):
        """Process the event type from an SSE line.

        Args:
            line (str): The SSE line starting with 'event:'

        Returns:
            str: The event type
            bool: True if the event is 'done', False otherwise
        """
        raw_event_type = line[6:].strip()
        event_type = raw_event_type
        self.current_event_type = event_type

        # If we get the 'done' event, signal to stop processing
        if event_type == "response.output_text.done" or event_type == "done":
            # Only update the live view with important completion messages
            if self.json_live:
                self.json_live.update(
                    content=None,
                    panel_style="red",
                    title="Stream Complete",
                )
            return event_type, True

        return event_type, False

    def _format_usage_text(self, event_index, event_type):
        """Format the usage information into a rich Text object.

        Args:
            event_index (int): The current event index
            status (str): The status text to display

        Returns:
            Text: Formatted text with event index, status, and token usage
        """
        status_text = Text()
        status_text.append(f"{event_index:05d}", style="cyan bold")
        status_text.append(" / ")
        status_text.append(f"{event_type}", style="green")
        status_text.append(" / ")
        status_text.append("  ↑ ", style="blue")
        status_text.append(f"{self.usage['input_tokens']}", style="blue bold")
        status_text.append("  ↓ ", style="magenta")
        status_text.append(f"{self.usage['output_tokens']}", style="magenta bold")
        status_text.append("  ∑ ", style="yellow")
        status_text.append(f"{self.usage['total_tokens']}", style="yellow bold")
        return status_text

    def _reset_usage(self):
        """Reset the usage statistics to zero."""
        self.usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

    def _collect_usage(self, usage_data):
        """Update the usage statistics from the provided usage data.

        Args:
            usage_data (dict): Dictionary containing usage information
        """
        if not usage_data:
            return

        # Extract token information
        input_tokens = usage_data.get("input_tokens", 0)
        output_tokens = usage_data.get("output_tokens", 0)
        total_tokens = usage_data.get("total_tokens", 0)

        # Update usage tracking
        self.usage["input_tokens"] = input_tokens
        self.usage["output_tokens"] = output_tokens
        self.usage["total_tokens"] = total_tokens

    def _add_event(self, event_data):
        """Add a new event to the events list and update the display.

        Args:
            event_data (dict): The event data to add

        Returns:
            dict: The processed event data
        """
        # Store the event with its metadata
        event = {
            "data": event_data,
            "status": self.current_event_type,
            "index": len(self.events),  # Current index is the length before adding
        }
        self.events.append(event)

        # Format the status text with usage information
        status_text = self._format_usage_text(event["index"], self.current_event_type)

        # Initialize json_live if needed
        if not self.json_live:
            self.json_live = JsonLive(self.console)

        # Update with event info as subtitle
        display_data = event_data if event_data else None
        self.json_live.update(display_data, subtitle=status_text)

        return event_data

    def parse_event_data(self, data_str):
        """Parse the JSON data from an SSE event.

        Args:
            data_str (str): The data string from the SSE event
            status (str): The type of the event

        Returns:
            dict: The parsed JSON data
        """
        data = json.loads(data_str)

        # Extract and process usage data if present
        self._collect_usage(data.pop("usage", None))

        # Use the NO_DISPLAY_FIELDS tuple
        for key in NO_DISPLAY_FIELDS:
            data.pop(key, None)

        # Add the event and update the display
        return self._add_event(data)

    def collect_response(self, response, user_query=None):
        """Handle the Server-Sent Events (SSE) stream.

        Args:
            response (Response): The requests response object with stream=True
            user_query (str, optional): The user query for display purposes

        Returns:
            dict: The final response data
        """
        final_response = None
        is_done = False

        # Reset usage at the beginning of a new response
        self._reset_usage()

        # Initialize and start the live display if not already started
        if not self.json_live:
            self.json_live = JsonLive(self.console)

        # Show initial message
        display_title = user_query if user_query else "Stream Started"
        self.json_live.update(
            '{"status": "started", "message": "SSE stream started. Receiving events..."}',
            title=display_title,
            panel_style="blue",
        )

        for line in response.iter_lines():
            if not line:
                continue

            line = line.decode("utf-8")

            if line.startswith("event:"):
                event_type, is_done = self.process_event_type(line)
                self.current_event_type = event_type
                continue

            # Skip non-data lines
            if not line.startswith("data:"):
                continue

            data_str = line[5:].strip()
            if not data_str:
                continue

            # Only try to parse as JSON if it looks like a JSON object
            if data_str.startswith("{") or data_str.startswith("["):
                data = self.parse_event_data(data_str)
                if not data:
                    continue

                final_response = data
            if is_done:
                break

        # Update the live display with a completion message
        # Include final usage information in completion message
        completion_message = f"Stream Complete | Final Usage: {self.usage['input_tokens']}↓ {self.usage['output_tokens']}↑ {self.usage['total_tokens']}∑"
        if self.json_live:
            self.json_live.update(content=None, title=completion_message, panel_style="red")
            self.json_live.done()
            self.json_live = None

        return final_response

    def create_response(self, messages, user_query=None):
        """Send a chat request to the Knowledge Forge API using SSE.

        Args:
            messages (list): List of message objects with role and content
            user_query (str, optional): The user query for display purposes

        Returns:
            dict: The final response data
        """
        # Create a request that matches the OpenAI format
        request_json = {
            "model": "qwen3-235b-a22b",  # Using a valid OpenAI model
            "effort": self.effort,  # Move effort to top level
            "store": True,
            "input": messages,
        }

        # Send the request to the API
        url = f"{BASE_URL}/v1/responses"
        # Create a syntax highlighted JSON panel with POST URL as title
        json_str = json.dumps(request_json, ensure_ascii=False, indent=2)
        json_syntax = Syntax(json_str, "json", theme="github-dark", word_wrap=True, padding=(1, 2))
        panel = Panel(
            json_syntax,
            title=f"POST {url}",
            border_style="blue",
            width=150,
            box=SIMPLE,
        )
        self.console.print(Align.center(panel))

        # Use stream=True for SSE
        response = requests.post(url, json=request_json, stream=True)

        response.raise_for_status()
        # Process the SSE stream
        return self.collect_response(response, user_query)

    def fetch_response_by_id(self, response_id):
        """Fetch a response by its ID using the Knowledge Forge API."""
        # Construct the URL to get the response by ID
        url = f"{BASE_URL}/v1/responses/{response_id}"
        self.console.print(f"\nFetching response by ID from: {url}")

        # Send GET request to retrieve the response
        response = requests.get(url)

        response.raise_for_status()

        # Parse and display the fetched response
        fetched_response = response.json()
        self.console.print("\nFetched response by ID:")
        self.console.print(json.dumps(fetched_response, ensure_ascii=False, indent=2))

        # Verify if the fetched response matches the original
        self.console.print(f"\nVerified response ID: {fetched_response.get('id')}")

        return fetched_response

    def get_user_input(self, prompt_text):
        """Get user input in a way that handles both interactive and non-interactive environments.
        Supports command history navigation with up/down arrow keys when in an interactive terminal.

        Args:
            prompt_text (str): The prompt text to display

        Returns:
            str: User input or None if EOF encountered
        """
        self.console.print(prompt_text, end=" ")
        history_file = str(Path.home() / ".knowledge-forge-history.txt")

        # First try with prompt_toolkit which supports history navigation
        try:
            import sys

            is_interactive = sys.stdin.isatty()

            if is_interactive:
                from prompt_toolkit import prompt
                from prompt_toolkit.history import FileHistory

                user_input = prompt("", history=FileHistory(history_file))

                # Save command to history file directly when using Rich's Prompt as fallback
                if user_input and user_input.strip():
                    with open(history_file, "a") as f:
                        f.write(user_input + "\n")

                return user_input
        except (ImportError, EOFError, KeyboardInterrupt, Exception):
            # Fall back to Rich's Prompt or basic input
            sys.exit(1)

        try:
            # Try Rich's prompt as a fallback
            return Prompt.ask("")
        except (EOFError, KeyboardInterrupt):
            return None

    def chat(self, initial_query=None):
        """Run an interactive chat session with the Knowledge Forge API.

        Args:
            initial_query (str, optional): The initial query to start the conversation with
        """
        # Initialize chat history
        self.chat_history = []

        self.console.print("\n[bold cyan]Welcome to Knowledge Forge Chat![/bold cyan]")
        self.console.print("Type 'exit' or 'quit' to end the conversation.\n")

        # Process initial query if provided
        if initial_query:
            self.console.print(f"[bold green]󰶻[/bold green] {initial_query}")
            current_query = initial_query
        else:
            # Try to get initial input
            current_query = self.get_user_input("[bold green]󰶻 [/bold green]")
            if current_query is None:
                # If we can't get interactive input, use a default query
                current_query = "Hello, Knowledge Forge!"
                self.console.print(f"[bold green]󰶻 [/bold green] {current_query} [italic](default query)[/italic]")

        # Main chat loop
        while current_query and current_query.lower() not in ["exit", "quit"]:
            # Add user message to chat history
            self.chat_history.append({"role": "user", "content": current_query})

            # Send the chat request with the full history
            final_response = self.create_response(
                messages=self.chat_history,
                user_query=current_query,  # Pass current user query to use as title
            )

            assert final_response is not None
            self.chat_history += final_response["output"]
            current_query = self.get_user_input("\n[bold green]󰶻 [/bold green] ")

        self.console.print("\n[bold cyan]Goodbye![/bold cyan]")


def main(initial_query=None, effort="low"):
    """Run an interactive chat session with the Knowledge Forge API.

    Args:
        initial_query (str, optional): The initial query to start the conversation with
        effort (str): Effort level for the response (low, medium, high)
    """
    chat = Chat(effort=effort)
    chat.chat(initial_query)


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Interactive chat with Knowledge Forge API")
    parser.add_argument("--query", "-q", type=str, help="Initial query to start the conversation")
    parser.add_argument(
        "--effort",
        "-e",
        type=str,
        choices=["low", "medium", "high", "dev"],
        default="low",
        help="Effort level for the response (default: low)",
    )
    args = parser.parse_args()

    main(args.query, args.effort)
