"""Top-K query command for vector stores."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from ..base import ChatCommand

if TYPE_CHECKING:
    from ...controller import ChatController


class TopKQueryCommand(ChatCommand):
    """Query a vector store collection with top-k results.
    
    Usage: /topk <collection-id> query="<query-text>" [top_k=10]
    
    Examples:
        /topk vs_123 query="machine learning techniques"
        /topk vs_456 query="neural networks" top_k=5
    """
    
    name = "topk"
    description = "Query a collection with top-k results"
    aliases = ["query", "search"]

    async def execute(self, args: str, controller: ChatController) -> bool:
        """Execute the top-k query command.
        
        Args:
            args: Command arguments in format: <collection-id> query="<query>" [top_k=N]
            controller: The ChatController instance
            
        Returns:
            True, indicating the chat session should continue
        """
        if not args.strip():
            controller.display.show_error("Usage: /topk <collection-id> query=\"<query-text>\" [top_k=10]")
            controller.display.show_status("Example: /topk vs_123 query=\"machine learning techniques\"")
            return True
            
        try:
            # Parse arguments
            collection_id, query, top_k = self._parse_args(args)
            
            # Validate collection ID
            if not collection_id:
                controller.display.show_error("Collection ID is required")
                return True
                
            # Validate query
            if not query:
                controller.display.show_error("Query is required")
                return True
                
            # Show query info
            controller.display.show_status(f"🔍 Querying collection: {collection_id}")
            controller.display.show_status(f"📝 Query: {query}")
            controller.display.show_status(f"🔢 Top-K: {top_k}")
            controller.display.show_status("")
            
            # Execute the query
            await self._execute_query(collection_id, query, top_k, controller)
            
        except ValueError as e:
            controller.display.show_error(f"Argument parsing error: {e}")
            controller.display.show_status("Usage: /topk <collection-id> query=\"<query-text>\" [top_k=10]")
        except Exception as e:
            controller.display.show_error(f"Error executing query: {e}")
            
        return True
        
    def _parse_args(self, args: str) -> tuple[str, str, int]:
        """Parse command arguments.
        
        Args:
            args: Raw argument string
            
        Returns:
            Tuple of (collection_id, query, top_k)
            
        Raises:
            ValueError: If parsing fails
        """
        # Split args to get collection ID first
        parts = args.strip().split(maxsplit=1)
        if len(parts) < 2:
            raise ValueError("Both collection ID and query are required")
            
        collection_id = parts[0]
        remaining_args = parts[1]
        
        # Parse key=value parameters from remaining args
        params = self._parse_parameters(remaining_args)
        
        # Extract query (required)
        query = params.get("query", "").strip()
        if not query:
            raise ValueError("query parameter is required")
            
        # Extract top_k (optional, default 10)
        top_k_str = params.get("top_k", "10")
        try:
            top_k = int(top_k_str)
            if top_k <= 0:
                raise ValueError("top_k must be a positive integer")
        except ValueError:
            raise ValueError(f"Invalid top_k value: {top_k_str}")
            
        return collection_id, query, top_k
        
    def _parse_parameters(self, args: str) -> dict[str, str]:
        """Parse command arguments in key=value format.
        
        Supports both quoted and unquoted values:
        - query="machine learning techniques" top_k=5
        - query=simple top_k=10
        
        Args:
            args: Argument string to parse
            
        Returns:
            Dictionary of parsed parameters
            
        Raises:
            ValueError: If parsing fails
        """
        params = {}
        
        # Regular expression to match key=value pairs with optional quotes
        # Supports: key="quoted value" or key=unquoted_value
        pattern = r'(\w+)=(?:"([^"]*)"|([^\s]+))'
        
        matches = re.findall(pattern, args)
        
        if not matches:
            raise ValueError("No valid key=value parameters found")
            
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
                vector_store_id=collection_id,
                query=query,
                top_k=top_k,
                filters=None
            )
            
            if result is None:
                controller.display.show_error("❌ Query failed - no results returned")
                return
                
            # Display results
            if hasattr(result, 'data') and result.data:
                controller.display.show_status(f"✅ Found {len(result.data)} results:")
                controller.display.show_status("")
                
                for i, item in enumerate(result.data, 1):
                    controller.display.show_status(f"📄 Result {i} (Score: {item.score:.4f})")
                    controller.display.show_status(f"   ID: {item.id}")
                    if item.file_id:
                        controller.display.show_status(f"   File: {item.file_id}")
                    
                    # Show text content (truncated if too long)
                    text = item.text.strip()
                    if len(text) > 200:
                        text = text[:200] + "..."
                    controller.display.show_status(f"   Text: {text}")
                    
                    # Show metadata if available
                    if item.metadata:
                        controller.display.show_status(f"   Metadata: {item.metadata}")
                    controller.display.show_status("")
                    
            else:
                controller.display.show_status("📭 No results found for the query")
                
        except ImportError:
            controller.display.show_error("❌ Vector store SDK not available")
        except Exception as e:
            controller.display.show_error(f"❌ Query execution failed: {e}")
