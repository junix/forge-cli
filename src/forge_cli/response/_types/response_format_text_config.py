# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union

from openai._utils import PropertyInfo
from openai.types.shared.response_format_json_object import ResponseFormatJSONObject
from openai.types.shared.response_format_text import ResponseFormatText
from typing_extensions import Annotated, TypeAlias

from .response_format_text_json_schema_config import ResponseFormatTextJSONSchemaConfig

__all__ = ["ResponseFormatTextConfig"]

ResponseFormatTextConfig: TypeAlias = Annotated[
    Union[ResponseFormatText, ResponseFormatTextJSONSchemaConfig, ResponseFormatJSONObject],
    PropertyInfo(discriminator="type"),
]
