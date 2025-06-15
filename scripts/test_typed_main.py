#!/usr/bin/env python3
"""Test script to verify the typed main.py works correctly."""

import subprocess
import sys
from pathlib import Path

# Test commands
test_commands = [
    # Basic help
    ["python", "-m", "forge_cli.main_updated", "--help"],
    # Version check
    ["python", "-m", "forge_cli.main_updated", "--version"],
    # Basic query (would need server running)
    # ["python", "-m", "forge_cli.main_updated", "-q", "test query", "--debug"],
]


def run_test(cmd):
    """Run a test command and report results."""
    print(f"\n{'=' * 60}")
    print(f"Running: {' '.join(cmd)}")
    print("=" * 60)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Command succeeded")
            if result.stdout:
                print("\nOutput:")
                print(result.stdout)
        else:
            print(f"❌ Command failed with code {result.returncode}")
            if result.stderr:
                print("\nError:")
                print(result.stderr)
            if result.stdout:
                print("\nOutput:")
                print(result.stdout)

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def main():
    """Run all tests."""
    print("Testing Typed Main.py")
    print("====================")

    # Change to project root
    project_root = Path(__file__).parent.parent
    import os

    os.chdir(project_root)

    success_count = 0
    total_count = len(test_commands)

    for cmd in test_commands:
        if run_test(cmd):
            success_count += 1

    print(f"\n{'=' * 60}")
    print(f"Test Summary: {success_count}/{total_count} tests passed")

    if success_count == total_count:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
