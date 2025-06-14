#!/usr/bin/env python3
"""Interactive test of chat mode with debug output."""

import subprocess
import time
import sys

print("Testing chat mode interactively with debug...", file=sys.stderr)

# Start the chat mode with debug
proc = subprocess.Popen(
    ["python", "-m", "forge_cli", "--chat", "--debug"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

# Give it a moment to start
time.sleep(1)

# Check if process is still running
if proc.poll() is not None:
    stdout, stderr = proc.communicate()
    print("Process exited immediately!")
    print("STDOUT:", stdout)
    print("STDERR:", stderr)
    sys.exit(1)

print("Chat mode started successfully!", file=sys.stderr)

# Try to send a simple message
proc.stdin.write("Say hello\n")
proc.stdin.flush()
time.sleep(5)  # Give more time for response

# Exit
proc.stdin.write("/exit\n")
proc.stdin.flush()
time.sleep(0.5)

# Get output
try:
    stdout, stderr = proc.communicate(timeout=3)
except subprocess.TimeoutExpired:
    proc.terminate()
    stdout, stderr = proc.communicate()

print("\n=== STDOUT ===")
print(stdout)

if stderr:
    print("\n=== STDERR ===")
    print(stderr)