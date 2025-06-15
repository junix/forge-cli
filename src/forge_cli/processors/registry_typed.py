"""Central registry for output processors with typed API support."""

from typing import Any

from .base import OutputProcessor
from .base_typed import TypedOutputProcessor


class TypedProcessorRegistry:
    """Central registry for output processors supporting typed items only."""

    def __init__(self):
        self._processors: dict[str, OutputProcessor | TypedOutputProcessor] = {}

    def register(self, output_type: str, processor: OutputProcessor | TypedOutputProcessor) -> None:
        """
        Register a processor for an output type.

        Args:
            output_type: The type of output item (e.g., "reasoning", "file_search_call")
            processor: The processor instance to handle this type
        """
        self._processors[output_type] = processor

    def get_processor(self, output_type: str) -> OutputProcessor | TypedOutputProcessor | None:
        """
        Get processor for output type.

        Args:
            output_type: The type of output item

        Returns:
            Processor instance or None if not found
        """
        return self._processors.get(output_type)

    def process_item(self, item: Any, state: Any = None, display: Any = None) -> Any:
        """
        Process an output item using appropriate processor.

        This method supports typed processors only.

        Args:
            item: Typed output item from the API
            state: StreamState instance (for typed processors)
            display: Display instance (for typed processors)

        Returns:
            None (typed processors update display directly)
        """
        # Determine item type
        if hasattr(item, "type"):
            output_type = str(item.type)
        else:
            return None

        processor = self.get_processor(output_type)

        if not processor:
            return None

        # Check if it's a typed processor
        if isinstance(processor, TypedOutputProcessor):
            # Typed processor - requires state and display
            if processor.can_process(output_type) and state and display:
                processor.process(item, state, display)
                return None  # Typed processors update display directly
        elif isinstance(processor, OutputProcessor):
            # Old-style processor
            if processor.can_process(output_type):
                # Check if it has the old signature (just item)
                import inspect

                sig = inspect.signature(processor.process)
                if len(sig.parameters) == 2:  # self, item
                    return processor.process(item)
                else:
                    # New signature with state and display
                    if state and display:
                        processor.process(item, state, display)
                        return None

        return None

    def format_item(self, item: Any) -> str | None:
        """
        Format an output item for display (for old-style processors).

        Args:
            item: Raw output item from the API

        Returns:
            Formatted string or None if no processor found
        """
        # Determine item type
        if hasattr(item, "type"):
            output_type = str(item.type)
        else:
            return None

        processor = self.get_processor(output_type)

        if processor and isinstance(processor, OutputProcessor):
            # Only old-style processors have separate format method
            if processor.can_process(output_type):
                processed = processor.process(item)
                if processed:
                    return processor.format(processed)
        return None


# Create and populate default typed registry
default_typed_registry = TypedProcessorRegistry()


def initialize_typed_registry():
    """Initialize the typed registry with both old and new processors."""
    # Import here to avoid circular imports
    from .message import MessageProcessor
    from .reasoning import ReasoningProcessor
    from .tool_calls.document_finder_typed import DocumentFinderProcessor as TypedDocumentFinderProcessor
    from .tool_calls.file_reader_typed import FileReaderProcessor as TypedFileReaderProcessor
    from .tool_calls.file_search_typed import FileSearchProcessor as TypedFileSearchProcessor
    from .tool_calls.web_search_typed import WebSearchProcessor as TypedWebSearchProcessor

    # Register processors that already support both dict and typed
    default_typed_registry.register("reasoning", ReasoningProcessor())
    default_typed_registry.register("message", MessageProcessor())

    # Register new typed tool processors
    default_typed_registry.register("file_search_call", TypedFileSearchProcessor())
    default_typed_registry.register("web_search_call", TypedWebSearchProcessor())
    default_typed_registry.register("document_finder_call", TypedDocumentFinderProcessor())
    default_typed_registry.register("file_reader_call", TypedFileReaderProcessor())
