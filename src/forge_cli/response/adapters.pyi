from typing import Any, Union, List, Dict, TypeAlias

from forge_cli.response._types import (
    FileSearchTool as FileSearchTool,
    InputMessage as InputMessage,
    Request as Request,
    Response as Response,
    ResponseStreamEvent as ResponseStreamEvent,
    WebSearchTool as WebSearchTool,
)

# Forward reference for Tool, assuming it's a type defined elsewhere or a generic dict
Tool: TypeAlias = Union[Dict[str, Any], Any]  # Replace Any with actual Tool type if available

class ResponseAdapter:
    @staticmethod
    def from_dict(response_dict: Dict[str, Any]) -> Response: ...
    @staticmethod
    def to_dict(response: Response) -> Dict[str, Any]: ...
    @staticmethod
    def create_request(
        input_messages: Union[str, List[Dict[str, Any]], List[InputMessage]],
        model: str = ...,
        tools: Union[List[Tool], None] = ...,
        **kwargs: Any,
    ) -> Request: ...
    @staticmethod
    def request_to_openai_format(request: Request) -> Dict[str, Any]: ...

class StreamEventAdapter:
    @staticmethod
    def parse_event(event_data: Dict[str, Any]) -> ResponseStreamEvent: ...

class ToolAdapter:
    @staticmethod
    def create_file_search_tool(vector_store_ids: List[str], max_search_results: int = ...) -> FileSearchTool: ...
    @staticmethod
    def create_web_search_tool() -> WebSearchTool: ...
    @staticmethod
    def tools_to_openai_format(tools: List[Tool]) -> List[Dict[str, Any]]: ...
