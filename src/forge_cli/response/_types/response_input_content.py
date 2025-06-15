# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from typing import Annotated, TypeAlias

from openai._utils import PropertyInfo

from .response_input_file import ResponseInputFile
from .response_input_image import ResponseInputImage
from .response_input_text import ResponseInputText

__all__ = ["ResponseInputContent"]

ResponseInputContent: TypeAlias = Annotated[
    ResponseInputText | ResponseInputImage | ResponseInputFile, PropertyInfo(discriminator="type")
]
