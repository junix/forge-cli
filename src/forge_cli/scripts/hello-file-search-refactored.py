#!/usr/bin/env python3
"""
Refactored multi-tool search example using the Knowledge Forge SDK.

This is a thin wrapper that runs the refactored modular implementation.
The actual implementation is in the hello_file_search_refactored package.
"""

import asyncio
import sys

# Import and run the main function from the refactored module
from hello_file_search_refactored.main import main


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nOperation canceled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {type(e).__name__}: {e}")
        if "--debug" in sys.argv or "-d" in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)