from typing import Protocol

from rich.align import Align
from rich.columns import Columns
from rich.console import Group
from rich.json import JSON
from rich.layout import Layout
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress
from rich.rule import Rule
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.tree import Tree


class Rendable(Protocol):
    """Protocol for rendable objects."""

    def render(
        self, **kwargs
    ) -> (
        str
        | Text
        | Panel
        | Table
        | JSON
        | Markdown
        | Syntax
        | Tree
        | Rule
        | Align
        | Columns
        | Group
        | Layout
        | Progress
        | list[
            str
            | Text
            | Panel
            | JSON
            | Table
            | Markdown
            | Syntax
            | Tree
            | Rule
            | Align
            | Columns
            | Group
            | Layout
            | Progress
        ]
        | None
    ):
        """Render the object."""
        ...

    async def arender(
        self, **kwargs
    ) -> (
        str
        | Text
        | Panel
        | Table
        | JSON
        | Markdown
        | Syntax
        | Tree
        | Rule
        | Align
        | Columns
        | Group
        | Layout
        | Progress
        | list[
            str
            | Text
            | Panel
            | JSON
            | Table
            | Markdown
            | Syntax
            | Tree
            | Rule
            | Align
            | Columns
            | Group
            | Layout
            | Progress
        ]
        | None
    ):
        """Render the object."""
        return self.render(**kwargs)
