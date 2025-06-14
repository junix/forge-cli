#!/usr/bin/env python3
"""Quick test of chat mode."""

import subprocess
import time

# Start the chat mode
proc = subprocess.Popen(
    ["python", "-m", "forge_cli", "--chat", "--quiet"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Give it a moment to start
time.sleep(0.5)

# Try to exit immediately
proc.stdin.write("/exit\n")
proc.stdin.flush()

# Wait a bit
time.sleep(0.5)

# Terminate if still running
proc.terminate()

# Get output
stdout, stderr = proc.communicate(timeout=2)

print("STDOUT:")
print(stdout)
print("\nSTDERR:")
print(stderr)

if "AttributeError" in stderr:
    print("\n❌ Error found: AttributeError")
else:
    print("\n✅ No AttributeError found")