from rich.text import Text
from rich.panel import Panel
from rich.table import Table

class Rendable:
    """Base class for rendable objects."""

    def render(self) -> str | Text | Panel | Table | list[str | Text | Panel | Table] | None :
        """Render the object."""
        raise NotImplementedError("Subclasses must implement this method")
