"""Migration helper utilities for transitioning from dict-based to typed API."""

from typing import Any, Union, Dict, List


class MigrationHelper:
    """Utilities to help with gradual migration from dict to typed API."""
    
    @staticmethod
    def is_typed_response(obj: Any) -> bool:
        """Check if object is a typed Response object."""
        # Check if it's from the typed API by looking for Response class attributes
        return hasattr(obj, "__class__") and hasattr(obj, "id") and hasattr(obj, "output")
    
    @staticmethod
    def is_typed_item(obj: Any) -> bool:
        """Check if object is a typed output item."""
        # Typed items have class attributes and type property
        return hasattr(obj, "__class__") and hasattr(obj, "type") and not isinstance(obj, dict)
    
    @staticmethod
    def safe_get_text(event_data: Any) -> str:
        """Extract text from both dict and typed text delta events."""
        if isinstance(event_data, dict):
            return event_data.get("text", "")
        elif hasattr(event_data, "text"):
            return str(event_data.text)
        return ""
    
    @staticmethod
    def safe_get_type(item: Any) -> str | None:
        """Extract type from both dict and typed items."""
        if isinstance(item, dict):
            return item.get("type")
        elif hasattr(item, "type"):
            return str(item.type)
        return None
    
    @staticmethod
    def safe_get_status(item: Any) -> str | None:
        """Extract status from both dict and typed items."""
        if isinstance(item, dict):
            return item.get("status")
        elif hasattr(item, "status"):
            return str(item.status)
        return None
    
    @staticmethod
    def safe_get_output_items(response: Any) -> List[Any]:
        """Extract output items from both dict and typed responses."""
        if isinstance(response, dict):
            return response.get("output", [])
        elif hasattr(response, "output"):
            return list(response.output) if response.output else []
        return []
    
    @staticmethod
    def safe_get_results(tool_call: Any) -> List[Any]:
        """Extract results from both dict and typed tool calls."""
        if isinstance(tool_call, dict):
            return tool_call.get("results", [])
        elif hasattr(tool_call, "results"):
            return list(tool_call.results) if tool_call.results else []
        elif hasattr(tool_call, "_results"):  # Some tools use private _results
            return list(tool_call._results) if tool_call._results else []
        return []
    
    @staticmethod
    def convert_tool_to_typed(tool_dict: Dict[str, Any]) -> Any:
        """Convert dict tool to typed tool."""
        from forge_cli.response._types import FileSearchTool, WebSearchTool
        
        tool_type = tool_dict.get("type")
        
        if tool_type == "file_search":
            return FileSearchTool(
                type="file_search",
                vector_store_ids=tool_dict.get("vector_store_ids", []),
                max_num_results=tool_dict.get("max_num_results", 10)
            )
        elif tool_type == "web_search":
            params = {"type": "web_search"}
            if "country" in tool_dict:
                params["country"] = tool_dict["country"]
            if "city" in tool_dict:
                params["city"] = tool_dict["city"]
            return WebSearchTool(**params)
        
        # Return original if unknown type
        return tool_dict
    
    @staticmethod
    def convert_message_to_typed(msg_dict: Dict[str, Any]) -> Any:
        """Convert dict message to typed InputMessage."""
        from forge_cli.response._types import InputMessage
        
        if isinstance(msg_dict, dict) and "role" in msg_dict and "content" in msg_dict:
            return InputMessage(
                role=msg_dict["role"],
                content=msg_dict["content"]
            )
        return msg_dict
    
    @staticmethod
    def is_reasoning_item(item: Any) -> bool:
        """Check if item is a reasoning item (both dict and typed)."""
        item_type = MigrationHelper.safe_get_type(item)
        return item_type in ["reasoning", "summary"]
    
    @staticmethod
    def is_message_item(item: Any) -> bool:
        """Check if item is a message item (both dict and typed)."""
        item_type = MigrationHelper.safe_get_type(item)
        return item_type == "message"
    
    @staticmethod
    def is_tool_call_item(item: Any) -> bool:
        """Check if item is a tool call item (both dict and typed)."""
        item_type = MigrationHelper.safe_get_type(item)
        return item_type and item_type.endswith("_call")
    
    @staticmethod
    def extract_tool_id(tool_call: Any) -> str | None:
        """Extract tool ID from both dict and typed tool calls."""
        if isinstance(tool_call, dict):
            return tool_call.get("id")
        elif hasattr(tool_call, "id"):
            return str(tool_call.id)
        return None
    
    @staticmethod
    def extract_event_type(event: Any) -> str | None:
        """Extract event type from both dict and typed events."""
        if isinstance(event, dict):
            return event.get("type") or event.get("event_type")
        elif hasattr(event, "type"):
            return str(event.type)
        elif hasattr(event, "event_type"):
            return str(event.event_type)
        return None