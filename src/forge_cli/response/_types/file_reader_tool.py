from typing import Literal

from pydantic import BaseModel


class FileReaderTool(BaseModel):
    """File reader tool definition.

    This class represents a file reader tool configuration that can be
    used in requests to enable file reading capabilities.

    Attributes:
        type (str): The type of the tool, always "file_reader"
    """

    type: Literal["file_reader"] = "file_reader"
