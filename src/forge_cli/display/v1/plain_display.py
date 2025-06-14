"""Plain text display implementation."""

from typing import Dict, Any, Optional
from .base import BaseDisplay


class PlainDisplay(BaseDisplay):
    """Plain text display for terminals without Rich support."""

    def __init__(self):
        self.last_content = ""

    async def show_request_info(self, info: Dict[str, Any]) -> None:
        """Display request information in plain text."""
        print("\n📄 Request Information:")

        if "question" in info:
            print(f"  💬 Question: {info['question']}")

        if "vec_ids" in info and info["vec_ids"]:
            print(f"  🔍 Vector Store IDs: {', '.join(info['vec_ids'])}")

        if "model" in info:
            print(f"  🤖 Model: {info['model']}")

        if "effort" in info:
            print(f"  ⚙️ Effort Level: {info['effort']}")

        if "tools" in info and info["tools"]:
            print(f"  🛠️ Enabled Tools: {', '.join(info['tools'])}")

        print("\n🔄 Streaming response (please wait):")
        print("=" * 80)

    async def update_content(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Update display with new content."""
        # In plain mode, we only print deltas or status updates
        # Full content is shown at the end
        self.last_content = content

    async def show_status(self, status: str) -> None:
        """Show a status message."""
        print(f"\n⏳ {status}")

    async def show_error(self, error: str) -> None:
        """Show an error message."""
        print(f"\n❌ Error: {error}")

    async def finalize(self, response: Dict[str, Any], state: Any) -> None:
        """Finalize the display."""
        print("=" * 80)

        # Show final content
        if self.last_content:
            print("\n📃 Response Content:")
            print(self.last_content)

        # Show completion info
        print("\n✅ Response completed successfully!")

        if response:
            if "id" in response:
                print(f"  🆔 Response ID: {response['id']}")

            if "model" in response:
                print(f"  🤖 Model used: {response['model']}")
