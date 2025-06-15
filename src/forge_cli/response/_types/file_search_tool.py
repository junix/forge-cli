# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from typing import Literal, TypeAlias

from openai.types.shared.comparison_filter import ComparisonFilter
from openai.types.shared.compound_filter import CompoundFilter

from ._models import BaseModel

__all__ = ["FileSearchTool", "Filters", "RankingOptions"]

Filters: TypeAlias = ComparisonFilter | CompoundFilter | None


class RankingOptions(BaseModel):
    ranker: Literal["auto", "default-2024-11-15"] | None = None
    """The ranker to use for the file search."""

    score_threshold: float | None = None
    """The score threshold for the file search, a number between 0 and 1.

    Numbers closer to 1 will attempt to return only the most relevant results, but
    may return fewer results.
    """


class FileSearchTool(BaseModel):
    type: Literal["file_search"]
    """The type of the file search tool. Always `file_search`."""

    vector_store_ids: list[str]
    """The IDs of the vector stores to search."""

    filters: Filters | None = None
    """A filter to apply."""

    max_num_results: int | None = None
    """The maximum number of results to return.

    This number should be between 1 and 50 inclusive.
    """

    ranking_options: RankingOptions | None = None
    """Ranking options for search."""
