# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Annotated, Generic, TypeAlias, TypeVar

from openai._utils import PropertyInfo
from openai._utils._transform import PropertyInfo

from ._models import GenericModel
from .response import Response
from .response_computer_tool_call import ResponseComputerToolCall
from .response_file_search_tool_call import ResponseFileSearchToolCall
from .response_function_tool_call import ResponseFunctionToolCall
from .response_function_web_search import ResponseFunctionWebSearch
from .response_list_documents_tool_call import ResponseListDocumentsToolCall
from .response_output_message import ResponseOutputMessage
from .response_output_refusal import ResponseOutputRefusal
from .response_output_text import ResponseOutputText
from .response_reasoning_item import ResponseReasoningItem

__all__ = ["ParsedResponse", "ParsedResponseOutputMessage", "ParsedResponseOutputText"]

ContentType = TypeVar("ContentType")

# we need to disable this check because we're overriding properties
# with subclasses of their types which is technically unsound as
# properties can be mutated.
# pyright: reportIncompatibleVariableOverride=false


class ParsedResponseOutputText(ResponseOutputText, GenericModel, Generic[ContentType]):
    parsed: ContentType | None = None


ParsedContent: TypeAlias = Annotated[
    ParsedResponseOutputText[ContentType] | ResponseOutputRefusal,
    PropertyInfo(discriminator="type"),
]


class ParsedResponseOutputMessage(ResponseOutputMessage, GenericModel, Generic[ContentType]):
    if TYPE_CHECKING:
        content: list[ParsedContent[ContentType]]  # type: ignore[assignment]
    else:
        content: list[ParsedContent]


class ParsedResponseFunctionToolCall(ResponseFunctionToolCall):
    parsed_arguments: object = None


ParsedResponseOutputItem: TypeAlias = Annotated[
    ParsedResponseOutputMessage[ContentType]
    | ParsedResponseFunctionToolCall
    | ResponseFileSearchToolCall
    | ResponseListDocumentsToolCall
    | ResponseFunctionWebSearch
    | ResponseComputerToolCall
    | ResponseReasoningItem,
    PropertyInfo(discriminator="type"),
]


class ParsedResponse(Response, GenericModel, Generic[ContentType]):
    if TYPE_CHECKING:
        output: list[ParsedResponseOutputItem[ContentType]]  # type: ignore[assignment]
    else:
        output: list[ParsedResponseOutputItem]

    @property
    def output_parsed(self) -> ContentType | None:
        for output in self.output:
            if output.type == "message":
                for content in output.content:
                    if content.type == "output_text" and content.parsed:
                        return content.parsed

        return None
