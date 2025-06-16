# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Literal, Required

from typing_extensions import TypedDict

__all__ = ["ListDocumentsToolParam"]


class ListDocumentsToolParam(TypedDict, total=False):
    type: Required[Literal["list_documents"]]
    """The type of the list documents tool. Always `list_documents`."""

    vector_store_ids: Required[list[str]]
    """The IDs of the vector stores to search across."""

    max_num_results: int
    """The maximum number of results to return.

    This number should be between 1 and 50 inclusive.
    """

    filters: dict[str, str | float | bool | int] | None
    """Optional metadata filters to apply during search.
    
    Filters are applied as key-value pairs where the key is the metadata field name
    and the value is the expected value for that field.
    """

    score_threshold: float
    """Minimum relevance score threshold for results.

    Results with scores below this threshold will be filtered out.
    Should be a value between 0 and 1.
    """

    deduplicate: bool
    """Whether to remove duplicate documents across vector stores.

    When True, keeps only the highest-scoring version of each document.
    """
