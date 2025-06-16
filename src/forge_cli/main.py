"""Main entry point - refactored for better organization and type safety."""

import asyncio
import os
import sys

from forge_cli.chat.session import ChatSessionManager
from forge_cli.cli.parser import CLIParser
from forge_cli.config import AppConfig
from forge_cli.dataset import TestDataset
from forge_cli.display.factory import DisplayFactory


def create_config_from_args(args) -> AppConfig:
    """Create and configure AppConfig from parsed arguments.

    Args:
        args: Parsed command line arguments

    Returns:
        Configured AppConfig instance
    """
    # Create base configuration
    config = AppConfig.from_args(args)

    # Handle dataset configuration if provided
    dataset = None
    if getattr(args, "dataset", None):
        dataset = TestDataset.from_json(args.dataset)
        if not config.quiet:
            print(f"Loaded dataset from {args.dataset}")
            print(f"  Vector Store ID: {dataset.vectorstore_id}")
            print(f"  Files: {len(dataset.files)}")

    # Apply dataset-specific configuration
    config.apply_dataset_config(dataset, args)

    # Update environment if server specified
    if config.server_url != os.environ.get("KNOWLEDGE_FORGE_URL"):
        os.environ["KNOWLEDGE_FORGE_URL"] = config.server_url
        if not config.quiet and config.render_format != "json":
            print(f"🔗 Using server: {config.server_url}")

    return config


async def main():
    """Main function - simplified and refactored for better organization."""
    # Parse command line arguments with help and version handling
    args = CLIParser.parse_args()

    # Create and configure AppConfig
    config = create_config_from_args(args)

    # Create display
    display = DisplayFactory.create_display(config)

    # Create and start chat session
    session_manager = ChatSessionManager(config, display)
    await session_manager.start_session(initial_question=None, resume_conversation_id=getattr(args, "resume", None))


def run_main_async():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == "__main__":
    run_main_async()
