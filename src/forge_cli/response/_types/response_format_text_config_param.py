# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import TypeAlias

from openai.types.shared_params.response_format_json_object import (
    ResponseFormatJSONObject,
)
from openai.types.shared_params.response_format_text import ResponseFormatText

from .response_format_text_json_schema_config_param import (
    ResponseFormatTextJSONSchemaConfigParam,
)

__all__ = ["ResponseFormatTextConfigParam"]

ResponseFormatTextConfigParam: TypeAlias = ResponseFormatText | ResponseFormatTextJSONSchemaConfigParam | ResponseFormatJSONObject
