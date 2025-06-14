#!/usr/bin/env python3
"""Test reasoning with rich display."""

import subprocess
import time
import sys

print("Testing reasoning with rich display...", file=sys.stderr)

# Start the chat mode with high effort, NO quiet mode to use rich display
proc = subprocess.Popen(
    ["python", "-m", "forge_cli", "--chat", "--effort", "high"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

# Give it a moment to start
time.sleep(2)

# Check if process is still running
if proc.poll() is not None:
    stdout, stderr = proc.communicate()
    print("Process exited immediately!")
    print("STDOUT:", stdout)
    print("STDERR:", stderr)
    sys.exit(1)

print("Chat mode started successfully!", file=sys.stderr)

# Ask a question that should trigger reasoning
proc.stdin.write("Step by step, calculate 25 * 4\n")
proc.stdin.flush()
time.sleep(10)  # Give more time for reasoning and response

# Exit
proc.stdin.write("/exit\n") 
proc.stdin.flush()
time.sleep(1)

# Get output
try:
    stdout, stderr = proc.communicate(timeout=5)
except subprocess.TimeoutExpired:
    proc.terminate()
    stdout, stderr = proc.communicate()

print("\n=== STDOUT (first 4000 chars) ===")
print(stdout[:4000] if len(stdout) > 4000 else stdout)

# Check for reasoning indicators
if "thinking" in stdout.lower() or "🤔" in stdout or "reasoning" in stdout.lower():
    print("\n✅ Reasoning display is working!")
else:
    print("\n⚠️  No reasoning display found")