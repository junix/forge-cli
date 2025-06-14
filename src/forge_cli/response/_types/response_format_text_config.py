# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from typing import Annotated, TypeAlias

from openai._utils import PropertyInfo
from openai.types.shared.response_format_json_object import ResponseFormatJSONObject
from openai.types.shared.response_format_text import ResponseFormatText

from .response_format_text_json_schema_config import ResponseFormatTextJSONSchemaConfig

__all__ = ["ResponseFormatTextConfig"]

ResponseFormatTextConfig: TypeAlias = Annotated[
    ResponseFormatText | ResponseFormatTextJSONSchemaConfig | ResponseFormatJSONObject,
    PropertyInfo(discriminator="type"),
]
