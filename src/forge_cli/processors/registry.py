"""Central registry for output processors."""

from .base import OutputProcessor


class ProcessorRegistry:
    """Central registry for output processors."""

    def __init__(self):
        self._processors: dict[str, OutputProcessor] = {}

    def register(self, output_type: str, processor: OutputProcessor) -> None:
        """
        Register a processor for an output type.

        Args:
            output_type: The type of output item (e.g., "reasoning", "file_search_call")
            processor: The processor instance to handle this type
        """
        self._processors[output_type] = processor

    def get_processor(self, output_type: str) -> OutputProcessor | None:
        """
        Get processor for output type.

        Args:
            output_type: The type of output item

        Returns:
            Processor instance or None if not found
        """
        return self._processors.get(output_type)

    def process_item(
        self, item: dict[str, str | int | float | bool | list | dict]
    ) -> dict[str, str | int | float | bool | list | dict] | None:
        """
        Process an output item using appropriate processor.

        Args:
            item: Raw output item from the API

        Returns:
            Processed data or None if no processor found
        """
        output_type = item.get("type", "")
        processor = self.get_processor(output_type)

        if processor and processor.can_process(output_type):
            return processor.process(item)
        return None

    def format_item(self, item: dict[str, str | int | float | bool | list | dict]) -> str | None:
        """
        Format an output item for display.

        Args:
            item: Raw output item from the API

        Returns:
            Formatted string or None if no processor found
        """
        output_type = item.get("type", "")
        processor = self.get_processor(output_type)

        if processor and processor.can_process(output_type):
            processed = processor.process(item)
            if processed:
                return processor.format(processed)
        return None


# Create and populate default registry
default_registry = ProcessorRegistry()


def initialize_default_registry():
    """Initialize the default registry with all processors."""
    # Import here to avoid circular imports
    from .message import MessageProcessor
    from .reasoning import ReasoningProcessor
    from .tool_calls.document_finder import DocumentFinderProcessor
    from .tool_calls.file_reader import FileReaderProcessor
    from .tool_calls.file_search import FileSearchProcessor
    from .tool_calls.web_search import WebSearchProcessor

    # Register all processors
    default_registry.register("reasoning", ReasoningProcessor())
    default_registry.register("message", MessageProcessor())
    default_registry.register("file_search_call", FileSearchProcessor())
    default_registry.register("document_finder_call", DocumentFinderProcessor())
    default_registry.register("web_search_call", WebSearchProcessor())
    default_registry.register("file_reader_call", FileReaderProcessor())
