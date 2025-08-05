"""Top-K query command for vector stores."""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class TopKQueryCommand(ChatCommand):
    """Query a vector store collection with top-k results.

    Usage:
        /topk <query-text>                                              (simple format)
        /topk --collection=<id> --query="<text>" [--top-k=N] [--json]  (flag format)

    Examples:
        /topk machine learning techniques
        /topk --collection=my_collection --query="neural networks" --top-k=10
        /topk --query="python functions" --json
    """

    name = "topk"
    description = "Query a collection with top-k results"
    aliases = ["query", "search"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the top-k query command.

        Args:
            args: Command arguments in format: --collection=<id> --query="<query>" [--top-k=N]
            controller: The ChatController instance

        Returns:
            True, indicating the chat session should continue
        """
        if not args.strip():
            controller.display.show_error("Usage:")
            controller.display.show_status(
                "  /topk <query-text>                                              (simple format)"
            )
            controller.display.show_status(
                '  /topk --collection=<id> --query="<text>" [--top-k=N] [--json]  (flag format)'
            )
            controller.display.show_status("")
            controller.display.show_status("Examples:")
            controller.display.show_status("  /topk machine learning techniques")
            controller.display.show_status('  /topk --collection=my_vs --query="neural networks" --top-k=10')
            controller.display.show_status('  /topk --query="python functions" --json')
            controller.display.show_status("")
            controller.display.show_status("💡 Use '/use-collection <collection-id>' to set an active collection")
            return True

        try:
            # Parse arguments
            collection_id, query, top_k, json_output = self._parse_args(args, controller)

            # Validate query
            if not query:
                controller.display.show_error("Query is required")
                return True

            # Show query info (unless JSON output is requested)
            if not json_output:
                print(f"🔍 Querying collection: {collection_id}")
                print(f"📝 Query: {query}")
                print(f"🔢 Top-K: {top_k}")
                print()

            # Execute the query
            await self._execute_query(collection_id, query, top_k, json_output, controller)

        except ValueError as e:
            controller.display.show_error(f"Argument parsing error: {e}")
            controller.display.show_status("Usage:")
            controller.display.show_status(
                "  /topk <query-text>                                              (simple format)"
            )
            controller.display.show_status(
                '  /topk --collection=<id> --query="<text>" [--top-k=N] [--json]  (flag format)'
            )
        except Exception as e:
            controller.display.show_error(f"Error executing query: {e}")

        return True

    def _parse_args(self, args: str, controller: ChatController) -> tuple[str, str, int, bool]:
        """Parse command arguments.

        Supports two formats:
        1. Simple: "query text here" (uses current collection, default top-k)
        2. Flag-based: "--collection=id --query='text' --top-k=N --json"

        Args:
            args: Raw argument string
            controller: Chat controller to get current collection

        Returns:
            Tuple of (collection_id, query, top_k, json_output)

        Raises:
            ValueError: If parsing fails
        """
        args = args.strip()

        # Check if this looks like flag-based format (starts with --)
        if args.startswith("--"):
            return self._parse_flag_format(args, controller)
        else:
            return self._parse_simple_format(args, controller)

    def _parse_simple_format(self, args: str, controller: ChatController) -> tuple[str, str, int, bool]:
        """Parse simple format: just the query text."""
        query = args.strip()
        if not query:
            raise ValueError("Query text is required")

        # Get current collection
        current_collections = controller.conversation.get_current_vector_store_ids()
        if not current_collections:
            raise ValueError(
                "No current collection set\n" + "💡 Use '/use-collection <collection-id>' to set an active collection"
            )

        collection_id = current_collections[0]
        if len(current_collections) > 1:
            # Inform user which collection is being used
            controller.display.show_status(f"ℹ️ Using first active collection: {collection_id}")
            controller.display.show_status(f"   (You have {len(current_collections)} active collections)")

        # Use default top_k and no JSON output for simple format
        top_k = 5
        json_output = False

        return collection_id, query, top_k, json_output

    def _parse_flag_format(self, args: str, controller: ChatController) -> tuple[str, str, int, bool]:
        """Parse flag-based format: --collection=id --query='text' --top-k=N --json"""
        # Parse flag-based parameters
        params = self._parse_flag_parameters(args)

        # Extract query (required)
        query = params.get("query", "").strip()
        if not query:
            raise ValueError("--query parameter is required")

        # Extract collection_id (optional, use current if not provided)
        collection_id = params.get("collection", "").strip()
        if not collection_id:
            # Try to get current collection from conversation state
            current_collections = controller.conversation.get_current_vector_store_ids()
            if current_collections:
                # Use the first collection if multiple are active
                collection_id = current_collections[0]
                if len(current_collections) > 1:
                    # Inform user which collection is being used
                    controller.display.show_status(f"ℹ️ Using first active collection: {collection_id}")
                    controller.display.show_status(f"   (You have {len(current_collections)} active collections)")
            else:
                raise ValueError(
                    "--collection parameter is required (no current collection set)\n"
                    + "💡 Use '/use-collection <collection-id>' to set an active collection"
                )

        # Extract top_k (optional, default 5)
        top_k_str = params.get("top-k", "5")
        try:
            top_k = int(top_k_str)
            if top_k <= 0:
                raise ValueError("--top-k must be a positive integer")
        except ValueError:
            raise ValueError(f"Invalid --top-k value: {top_k_str}")

        # Extract json flag (optional, default False)
        json_output = "json" in params

        return collection_id, query, top_k, json_output

    def _parse_flag_parameters(self, args: str) -> dict[str, str]:
        """Parse command arguments in flag format.

        Supports flag-based arguments:
        - --collection=my_collection --query="machine learning techniques" --top-k=5 --json
        - --query="simple query" --top-k=10

        Args:
            args: Argument string to parse

        Returns:
            Dictionary of parsed parameters

        Raises:
            ValueError: If parsing fails
        """
        params = {}

        # Regular expression to match --flag=value pairs with optional quotes
        # Supports: --flag="quoted value" or --flag=unquoted_value
        pattern = r'--(\w+(?:-\w+)*)=(?:"([^"]*)"|([^\s]+))'

        matches = re.findall(pattern, args)

        for match in matches:
            key = match[0]
            # Use quoted value if present, otherwise unquoted value
            value = match[1] if match[1] else match[2]
            params[key] = value

        # Also check for boolean flags (flags without values like --json)
        bool_pattern = r"--(\w+(?:-\w+)*)(?=\s|$)"
        bool_matches = re.findall(bool_pattern, args)

        for flag in bool_matches:
            # Only add if it's not already in params (to avoid overriding --flag=value with --flag)
            if flag not in params:
                params[flag] = "true"

        if not params:
            raise ValueError("No valid --flag parameters found")

        return params

    async def _execute_query(
        self, collection_id: str, query: str, top_k: int, json_output: bool, controller: ChatController
    ) -> None:
        """Execute the vector store query.

        Args:
            collection_id: Vector store ID to query
            query: Search query text
            top_k: Number of results to return
            json_output: Whether to output results in JSON format
            controller: Chat controller instance
        """
        try:
            from forge_cli.sdk.vectorstore import async_query_vectorstore

            # Execute the query
            result = await async_query_vectorstore(
                vector_store_id=collection_id, query=query, top_k=top_k, filters=None
            )

            if result is None:
                if json_output:
                    print(json.dumps({"error": "Query failed - no results returned"}, indent=2))
                else:
                    print("❌ Query failed - no results returned")
                return

            # Display results
            if hasattr(result, "data") and result.data:
                if json_output:
                    # Output the native chunk data as JSON
                    print(json.dumps(result.model_dump(), indent=2))
                else:
                    print(f"✅ Found {len(result.data)} results:")
                    print()

                    for i, item in enumerate(result.data, 1):
                        print(f"--- Result {i} ---")

                        # Print core fields with color formatting
                        print(f"\033[33mscore\033[0m: \033[32m{item.score:.4f}\033[0m")
                        print(f"\033[33mfile\033[0m: \033[32m{item.filename}\033[0m")
                        print(f"\033[33mdoc_id\033[0m: \033[32m{item.file_id}\033[0m")

                        # Extract text from content array
                        text_content = ""
                        for content_item in item.content:
                            if content_item.type == "text":
                                text_content = content_item.text.strip()
                                break

                        # Show full text content without delimiters
                        if text_content:
                            print(f"\033[33mtext\033[0m: \033[32m{text_content}\033[0m")

                        # Flatten and show all attributes with color formatting
                        if item.attributes:
                            for key, value in item.attributes.items():
                                print(f"\033[33m{key}\033[0m: \033[32m{value}\033[0m")

                        print()

            else:
                if json_output:
                    print(json.dumps({"message": "No results found for the query", "data": []}, indent=2))
                else:
                    print("📭 No results found for the query")

        except ImportError:
            if json_output:
                print(json.dumps({"error": "Vector store SDK not available"}, indent=2))
            else:
                print("❌ Vector store SDK not available")
        except Exception as e:
            if json_output:
                print(json.dumps({"error": f"Query execution failed: {e}"}, indent=2))
            else:
                print(f"❌ Query execution failed: {e}")
