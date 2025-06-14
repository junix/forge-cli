"""JSON output display implementation."""

import json
from typing import Dict, Any, Optional
from .base import BaseDisplay


class JsonDisplay(BaseDisplay):
    """JSON output display for programmatic use."""

    def __init__(self):
        self.final_output: Dict[str, Any] = {}
        self.silent = True  # No intermediate output

    async def show_request_info(self, info: Dict[str, Any]) -> None:
        """Store request info for final output."""
        self.final_output["request"] = info

    async def update_content(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Store content updates."""
        # In JSON mode, we don't show intermediate updates
        pass

    async def show_status(self, status: str) -> None:
        """Status updates are not shown in JSON mode."""
        pass

    async def show_error(self, error: str) -> None:
        """Store error for final output."""
        self.final_output["error"] = error

    async def finalize(self, response: Dict[str, Any], state: Any) -> None:
        """Output final JSON."""
        if response:
            self.final_output["response"] = response

        # Add state information if useful
        if hasattr(state, "citations") and state.citations:
            self.final_output["citations_summary"] = {
                "total_citations": len(state.citations),
                "citations": state.citations,
            }

        # Output JSON
        print(json.dumps(self.final_output, indent=2, ensure_ascii=False))
