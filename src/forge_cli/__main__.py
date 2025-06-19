from __future__ import annotations

"""Allow the module to be run with python -m hello_file_search_refactored."""

import asyncio
import sys

from .main import main

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
