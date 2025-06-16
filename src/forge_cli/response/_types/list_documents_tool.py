# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Literal

from ._models import BaseModel

__all__ = ["ListDocumentsTool"]


class ListDocumentsTool(BaseModel):
    type: Literal["list_documents"]
    """The type of the list documents tool. Always `list_documents`."""

    vector_store_ids: list[str]
    """The IDs of the vector stores to search across."""

    max_num_results: int | None = None
    """The maximum number of results to return.

    This number should be between 1 and 50 inclusive. Defaults to 5.
    """

    filters: dict[str, str | float | bool | int] | None = None
    """Optional metadata filters to apply during search.
    
    Filters are applied as key-value pairs where the key is the metadata field name
    and the value is the expected value for that field.
    """

    score_threshold: float | None = None
    """Minimum relevance score threshold for results.

    Results with scores below this threshold will be filtered out.
    Should be a value between 0 and 1.
    """

    deduplicate: bool | None = None
    """Whether to remove duplicate documents across vector stores.

    When True, keeps only the highest-scoring version of each document.
    Defaults to True.
    """
