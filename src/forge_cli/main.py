"""Main entry point for forge-cli."""

import asyncio
import sys
from pathlib import Path

# Add the project root to sys.path so we can import the modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the main function from hello_file_search_refactored
def main():
    """Main entry point for the CLI."""
    try:
        # Import the refactored main function
        from hello_file_search_refactored.main import main as refactored_main
        
        # Run the refactored main function
        asyncio.run(refactored_main())
        
    except ImportError as e:
        print(f"Error: Could not import hello_file_search_refactored module. {e}")
        print("Please check your installation.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()