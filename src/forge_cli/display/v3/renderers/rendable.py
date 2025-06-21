from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.json import JSON

class Rendable:
    """Base class for rendable objects."""

    def render(self) -> str | Text | Panel | Table |JSON| list[str | Text | Panel | JSON| Table] | None :
        """Render the object."""
        raise NotImplementedError("Subclasses must implement this method")
