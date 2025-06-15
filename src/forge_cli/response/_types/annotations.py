# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Annotated, Literal, TypeAlias

from openai._utils import PropertyInfo

from ._models import BaseModel

if TYPE_CHECKING:
    from message._types.annotations import (
        MessageAnnotationFileCitation,
        MessageAnnotationFilePath,
        MessageAnnotationURLCitation,
    )

__all__ = [
    "Annotation",
    "AnnotationFileCitation",
    "AnnotationURLCitation",
    "AnnotationFilePath",
]


class AnnotationFileCitation(BaseModel):
    file_id: str
    """The ID of the file."""

    index: int
    """The index of the file in the list of files."""

    type: Literal["file_citation"]
    """The type of the file citation. Always `file_citation`."""

    snippet: str | None = None
    """Optional snippet of text from the web resource."""

    filename: str | None = None
    """Optional filename of the referenced file."""

    def get_short_description(self) -> str:
        """获取文件引用的简短描述。

        Returns:
            简短描述，格式如 "文档 filename" 或 "文档 file_123: '摘要内容...'"
        """
        # Use filename if available, otherwise fall back to file_id
        display_name = self.filename if self.filename else self.file_id
        base = f"{display_name}"

        if self.snippet:
            # 截断摘要到约30个字符
            snippet = self.snippet
            if len(snippet) > 30:
                snippet = snippet[:27] + "..."
            base += f": '{snippet}'"

        return base

    def get_display_text(self) -> str:
        """获取用于显示的文本。

        Returns:
            显示文本，格式如 "文档 filename, P{index}" 或 "文档 file_id, P{index}"
        """
        # Use filename if available, otherwise fall back to file_id
        display_name = self.filename if self.filename else self.file_id
        return f"{display_name}, P{self.index}"

    def __eq__(self, other) -> bool:
        """Compare AnnotationFileCitation for equality.

        Two file citations are equal if they reference the same file and index.
        Snippet and filename are not considered for equality to allow for
        different representations of the same citation.

        Args:
            other: Another object to compare with

        Returns:
            True if both citations reference the same file and index
        """
        if not isinstance(other, AnnotationFileCitation):
            return False
        return self.file_id == other.file_id and self.index == other.index and self.type == other.type

    def __ne__(self, other) -> bool:
        """Compare AnnotationFileCitation for inequality."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Make AnnotationFileCitation hashable for use in sets and dicts.

        Uses the same fields as __eq__ to ensure hash consistency.
        """
        return hash((self.file_id, self.index, self.type))

    def as_message_annotation(self) -> "MessageAnnotationFileCitation":
        """Convert to message annotation type.

        Returns:
            MessageAnnotationFileCitation: Message annotation for use in ChatMessage objects.
        """
        from message._types.annotations import MessageAnnotationFileCitation

        return MessageAnnotationFileCitation(
            file_id=self.file_id,
            index=self.index,
            type="file_citation",
            snippet=self.snippet,
            filename=self.filename,
        )


class AnnotationURLCitation(BaseModel):
    end_index: int
    """The index of the last character of the URL citation in the message."""

    start_index: int
    """The index of the first character of the URL citation in the message."""

    title: str
    """The title of the web resource."""

    type: Literal["url_citation"]
    """The type of the URL citation. Always `url_citation`."""

    url: str
    """The URL of the web resource."""

    snippet: str | None = None
    """Optional snippet of text from the web resource."""

    favicon: str | None = None

    def get_short_description(self) -> str:
        """获取网页引用的简短描述。

        Returns:
            简短描述，格式如 "网页: 标题 (domain.com)"
        """
        # 从URL中提取域名
        try:
            from urllib.parse import urlparse

            domain = urlparse(self.url).netloc
            if domain.startswith("www."):
                domain = domain[4:]
        except:
            domain = "web"

        # 使用标题，如果太长则截断
        title = self.title
        if len(title) > 25:
            title = title[:22] + "..."

        return f"网页: {title} ({domain})"

    def get_display_text(self) -> str:
        """获取用于显示的文本。

        Returns:
            显示文本，格式如 "网页标题 (domain.com)"
        """
        try:
            from urllib.parse import urlparse

            domain = urlparse(self.url).netloc
            if domain.startswith("www."):
                domain = domain[4:]
        except:
            domain = "web"

        if self.title:
            return f"[{self.title}]({domain})"
        else:
            return f"[{domain}]({domain})"

    def __eq__(self, other) -> bool:
        """Compare AnnotationURLCitation for equality.

        Two URL citations are equal if they reference the same URL.
        Title, snippet, and index positions are not considered for equality
        since the same URL might appear at different positions or with
        different titles/snippets.

        Args:
            other: Another object to compare with

        Returns:
            True if both citations reference the same URL
        """
        if not isinstance(other, AnnotationURLCitation):
            return False
        return self.url == other.url and self.type == other.type

    def __ne__(self, other) -> bool:
        """Compare AnnotationURLCitation for inequality."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Make AnnotationURLCitation hashable for use in sets and dicts.

        Uses the same fields as __eq__ to ensure hash consistency.
        """
        return hash((self.url, self.type))

    def as_message_annotation(self) -> "MessageAnnotationURLCitation":
        """Convert to message annotation type.

        Returns:
            MessageAnnotationURLCitation: Message annotation for use in ChatMessage objects.
        """
        from message._types.annotations import MessageAnnotationURLCitation

        return MessageAnnotationURLCitation(
            end_index=self.end_index,
            start_index=self.start_index,
            title=self.title,
            type="url_citation",
            url=self.url,
            snippet=self.snippet,
            favicon=self.favicon,
        )


class AnnotationFilePath(BaseModel):
    file_id: str
    """The ID of the file."""

    index: int
    """The index of the file in the list of files."""

    type: Literal["file_path"]
    """The type of the file path. Always `file_path`."""

    def __eq__(self, other) -> bool:
        """Compare AnnotationFilePath for equality.

        Two file path annotations are equal if they reference the same file and index.

        Args:
            other: Another object to compare with

        Returns:
            True if both annotations reference the same file and index
        """
        if not isinstance(other, AnnotationFilePath):
            return False
        return self.file_id == other.file_id and self.index == other.index and self.type == other.type

    def __ne__(self, other) -> bool:
        """Compare AnnotationFilePath for inequality."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Make AnnotationFilePath hashable for use in sets and dicts.

        Uses the same fields as __eq__ to ensure hash consistency.
        """
        return hash((self.file_id, self.index, self.type))

    def as_message_annotation(self) -> "MessageAnnotationFilePath":
        """Convert to message annotation type.

        Returns:
            MessageAnnotationFilePath: Message annotation for use in ChatMessage objects.
        """
        from message._types.annotations import MessageAnnotationFilePath

        return MessageAnnotationFilePath(
            file_id=self.file_id,
            index=self.index,
            type="file_path",
        )


Annotation: TypeAlias = Annotated[
    AnnotationFileCitation | AnnotationURLCitation | AnnotationFilePath,
    PropertyInfo(discriminator="type"),
]

AnnotationList: TypeAlias = list[Annotation]
