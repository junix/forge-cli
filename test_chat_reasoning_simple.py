#!/usr/bin/env python3
"""Simple test of reasoning in chat mode."""

import subprocess
import time
import sys

print("Testing reasoning with simple math question...", file=sys.stderr)

# Start the chat mode with high effort
proc = subprocess.Popen(
    ["python", "-m", "forge_cli", "--chat", "--effort", "high", "--model", "qwen-max-latest"],
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

# Ask a simple math question
proc.stdin.write("What is 15 + 27?\n")
proc.stdin.flush()
time.sleep(8)  # Give time for response

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

# Check for reasoning or thinking indicators
if "thinking" in stdout.lower() or "🤔" in stdout:
    print("\n✅ Reasoning display is working!")
else:
    print("\n⚠️  No reasoning display found, but reasoning may have occurred in background")