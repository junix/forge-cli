from __future__ import annotations

"""Type guards for annotation types."""

from typing import Any, TypeGuard

from .._types.annotations import AnnotationFileCitation, AnnotationFilePath, AnnotationURLCitation


def is_file_citation(annotation: Any) -> TypeGuard[AnnotationFileCitation]:
    """Check if the given annotation is an AnnotationFileCitation.

    Args:
        annotation: The annotation object to check.

    Returns:
        True if the annotation is an AnnotationFileCitation, False otherwise.
    """
    return hasattr(annotation, "type") and annotation.type == "file_citation"


def is_url_citation(annotation: Any) -> TypeGuard[AnnotationURLCitation]:
    """Check if the given annotation is an AnnotationURLCitation.

    Args:
        annotation: The annotation object to check.

    Returns:
        True if the annotation is an AnnotationURLCitation, False otherwise.
    """
    return hasattr(annotation, "type") and annotation.type == "url_citation"


def is_file_path(annotation: Any) -> TypeGuard[AnnotationFilePath]:
    """Check if the given annotation is an AnnotationFilePath.

    Args:
        annotation: The annotation object to check.

    Returns:
        True if the annotation is an AnnotationFilePath, False otherwise.
    """
    return hasattr(annotation, "type") and annotation.type == "file_path"
