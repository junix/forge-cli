"""Top-K query command for vector stores."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class TopKQueryCommand(ChatCommand):
    """Query a vector store collection with top-k results.

    Usage:
        /topk <query-text>                                    (simple format)
        /topk --collection=<id> --query="<text>" [--top-k=N] (flag format)

    Examples:
        /topk machine learning techniques
        /topk --collection=my_collection --query="neural networks" --top-k=10
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
            controller.display.show_status("  /topk <query-text>                                    (simple format)")
            controller.display.show_status('  /topk --collection=<id> --query="<text>" [--top-k=N] (flag format)')
            controller.display.show_status("")
            controller.display.show_status("Examples:")
            controller.display.show_status("  /topk machine learning techniques")
            controller.display.show_status('  /topk --collection=my_vs --query="neural networks" --top-k=10')
            controller.display.show_status("")
            controller.display.show_status("💡 Use '/use-collection <collection-id>' to set an active collection")
            return True

        try:
            # Parse arguments
            collection_id, query, top_k = self._parse_args(args, controller)

            # Validate query
            if not query:
                controller.display.show_error("Query is required")
                return True

            # Show query info
            print(f"🔍 Querying collection: {collection_id}")
            print(f"📝 Query: {query}")
            print(f"🔢 Top-K: {top_k}")
            print()

            # Execute the query
            await self._execute_query(collection_id, query, top_k, controller)

        except ValueError as e:
            controller.display.show_error(f"Argument parsing error: {e}")
            controller.display.show_status("Usage:")
            controller.display.show_status("  /topk <query-text>                                    (simple format)")
            controller.display.show_status('  /topk --collection=<id> --query="<text>" [--top-k=N] (flag format)')
        except Exception as e:
            controller.display.show_error(f"Error executing query: {e}")

        return True

    def _parse_args(self, args: str, controller: ChatController) -> tuple[str, str, int]:
        """Parse command arguments.

        Supports two formats:
        1. Simple: "query text here" (uses current collection, default top-k)
        2. Flag-based: "--collection=id --query='text' --top-k=N"

        Args:
            args: Raw argument string
            controller: Chat controller to get current collection

        Returns:
            Tuple of (collection_id, query, top_k)

        Raises:
            ValueError: If parsing fails
        """
        args = args.strip()

        # Check if this looks like flag-based format (starts with --)
        if args.startswith("--"):
            return self._parse_flag_format(args, controller)
        else:
            return self._parse_simple_format(args, controller)

    def _parse_simple_format(self, args: str, controller: ChatController) -> tuple[str, str, int]:
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

        # Use default top_k
        top_k = 5

        return collection_id, query, top_k

    def _parse_flag_format(self, args: str, controller: ChatController) -> tuple[str, str, int]:
        """Parse flag-based format: --collection=id --query='text' --top-k=N"""
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

        return collection_id, query, top_k

    def _parse_flag_parameters(self, args: str) -> dict[str, str]:
        """Parse command arguments in flag format.

        Supports flag-based arguments:
        - --collection=my_collection --query="machine learning techniques" --top-k=5
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

        if not matches:
            raise ValueError("No valid --flag=value parameters found")

        for match in matches:
            key = match[0]
            # Use quoted value if present, otherwise unquoted value
            value = match[1] if match[1] else match[2]
            params[key] = value

        return params

    async def _execute_query(self, collection_id: str, query: str, top_k: int, controller: ChatController) -> None:
        """Execute the vector store query.

        Args:
            collection_id: Vector store ID to query
            query: Search query text
            top_k: Number of results to return
            controller: Chat controller instance
        """
        try:
            from forge_cli.sdk.vectorstore import async_query_vectorstore

            # Execute the query
            result = await async_query_vectorstore(
                vector_store_id=collection_id, query=query, top_k=top_k, filters=None
            )

            if result is None:
                print("❌ Query failed - no results returned")
                return

            # Display results
            if hasattr(result, "data") and result.data:
                print(f"✅ Found {len(result.data)} results:")
                print()

                for i, item in enumerate(result.data, 1):
                    # Add separator line before each result (except the first)
                    if i > 1:
                        print("─" * 80)
                        print()

                    print(f"📄 Result {i} (Score: {item.score:.4f})")
                    print(f"   File: {item.filename} (ID: {item.file_id})")

                    # Extract text from content array
                    text_content = ""
                    for content_item in item.content:
                        if content_item.type == "text":
                            text_content = content_item.text.strip()
                            break

                    # Show text content (truncated if too long)
                    if text_content:
                        if len(text_content) > 200:
                            text_content = text_content[:200] + "..."
                        print(f"   Text: {text_content}")

                    # Show attributes if available
                    if item.attributes:
                        print(f"   Attributes: {item.attributes}")
                    print()

            else:
                print("📭 No results found for the query")

        except ImportError:
            print("❌ Vector store SDK not available")
        except Exception as e:
            print(f"❌ Query execution failed: {e}")
