#!/usr/bin/env python3
"""Test chat with specific model and debug output."""

import subprocess
import time
import sys

print("Testing chat mode with model and debug...", file=sys.stderr)

# Start the chat mode with a specific model and debug
proc = subprocess.Popen(
    ["python", "-m", "forge_cli", "--chat", "--model", "qwen-max-latest", "--debug"],
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

# Send a simple greeting
proc.stdin.write("Say hello back to me\n")
proc.stdin.flush()
time.sleep(8)  # Give more time for response

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
print(stdout[:2000] if len(stdout) > 2000 else stdout)  # Limit output

if stderr:
    print("\n=== STDERR (last 1000 chars) ===")
    print(stderr[-1000:] if len(stderr) > 1000 else stderr)