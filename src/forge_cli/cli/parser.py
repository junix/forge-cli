"""Command line argument parser for forge-cli."""

import argparse
import os
import sys


class CLIParser:
    """Handles command line argument parsing and help display."""

    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        """Create and configure the argument parser."""
        parser = argparse.ArgumentParser(
            description="Refactored multi-tool search using Knowledge Forge SDK (typed API)",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        # Query argument
        parser.add_argument(
            "--question",
            "-q",
            type=str,
            default="What information can you find in the documents?",
            help="Question to ask",
        )

        # Vector store arguments
        parser.add_argument(
            "--vec-id",
            action="append",
            default=None,
            help="Vector store ID(s) to search in (can specify multiple)",
        )
        # Dataset argument
        parser.add_argument(
            "--dataset",
            type=str,
            help="Path to dataset JSON file with vectorstore ID and file configurations",
        )

        # Model arguments
        parser.add_argument(
            "--model",
            "-m",
            type=str,
            default="qwen-max-latest",
            help="Model to use for the response",
        )
        parser.add_argument(
            "--effort",
            "-e",
            type=str,
            choices=["low", "medium", "high", "dev"],
            default="low",
            help="Effort level for the response",
        )

        # Search arguments
        parser.add_argument(
            "--max-results",
            type=int,
            default=10,
            help="Maximum number of search results per vector store",
        )

        # Tool arguments
        parser.add_argument(
            "--tool",
            "-t",
            action="append",
            choices=["file-search", "web-search", "page-reader"],
            help="Enable specific tools (can specify multiple)",
        )

        # Web search location
        parser.add_argument(
            "--country",
            type=str,
            help="Country for web search location context",
        )
        parser.add_argument(
            "--city",
            type=str,
            help="City for web search location context",
        )

        # Display arguments
        parser.add_argument(
            "--debug",
            "-d",
            action="store_true",
            help="Enable debug output",
        )
        parser.add_argument(
            "--render",
            type=str,
            choices=["json", "rich", "plaintext"],
            default="rich",
            help="Output rendering format",
        )
        parser.add_argument(
            "--quiet",
            "-Q",
            action="store_true",
            help="Quiet mode - minimal output",
        )
        parser.add_argument(
            "--throttle",
            type=int,
            default=0,
            help="Throttle output (milliseconds between tokens)",
        )

        # Server argument
        parser.add_argument(
            "--server",
            default=os.environ.get("KNOWLEDGE_FORGE_URL", "http://localhost:9999"),
            help="Server URL",
        )

        # Resume conversation argument
        parser.add_argument(
            "--resume",
            "-r",
            type=str,
            help="Resume an existing conversation by ID",
        )

        # Other arguments
        parser.add_argument(
            "--version",
            "-v",
            action="store_true",
            help="Show version and exit",
        )

        return parser

    @staticmethod
    def should_show_help() -> bool:
        """Check if help should be shown (no arguments provided)."""
        return len(sys.argv) == 1 and not any(arg in sys.argv for arg in ["-h", "--help"])

    @staticmethod
    def show_help_and_examples(parser: argparse.ArgumentParser) -> None:
        """Show help and usage examples."""
        parser.print_help()
        print("\nExample usage:")
        print("  # Start interactive chat (default mode):")
        print("  python -m forge_cli")
        print()
        print("  # Start chat with specific model:")
        print("  python -m forge_cli -m qwen3-235b-a22b")
        print()
        print("  # Start chat with file search enabled:")
        print("  python -m forge_cli --vec-id vec_123 -t file-search")
        print()
        print("  # Start chat with web search enabled:")
        print("  python -m forge_cli -t web-search")
        print()
        print("  # Start chat with initial question:")
        print('  python -m forge_cli -q "What information is in these documents?"')
        print()
        print("  # Resume existing conversation:")
        print("  python -m forge_cli --resume conv_123")

    @staticmethod
    def show_version() -> None:
        """Show version information."""
        try:
            from forge_cli import __version__

            print(f"Knowledge Forge File Search Refactored v{__version__}")
        except ImportError:
            print("Knowledge Forge File Search Refactored (version unknown)")

    @classmethod
    def parse_args(cls) -> argparse.Namespace:
        """Parse command line arguments with help and version handling."""
        parser = cls.create_parser()

        # Show help if no arguments
        if cls.should_show_help():
            cls.show_help_and_examples(parser)
            sys.exit(0)

        args = parser.parse_args()

        # Handle version
        if args.version:
            cls.show_version()
            sys.exit(0)

        return args
