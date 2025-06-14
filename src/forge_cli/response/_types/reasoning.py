
from typing import Literal

from openai.types.shared import ReasoningEffort

from ._models import BaseModel

__all__ = ["Reasoning"]


class Reasoning(BaseModel):
    effort: ReasoningEffort | None = None
    """**o-series models only**

    Constrains effort on reasoning for
    [reasoning models](https://platform.openai.com/docs/guides/reasoning). Currently
    supported values are `low`, `medium`, and `high`. Reducing reasoning effort can
    result in faster responses and fewer tokens used on reasoning in a response.
    """

    generate_summary: Literal["auto", "concise", "detailed"] | None = None
    """**Deprecated:** use `summary` instead.

    A summary of the reasoning performed by the model. This can be useful for
    debugging and understanding the model's reasoning process. One of `auto`,
    `concise`, or `detailed`.
    """

    # summary: Optional[Literal["auto", "concise", "detailed"]] = None
    summary: Literal["auto", "concise", "detailed"] | None = None
    summary_detail: str | None = None
    """A summary of the reasoning performed by the model.

    This can be useful for debugging and understanding the model's reasoning
    process. One of `auto`, `concise`, or `detailed`.
    """
