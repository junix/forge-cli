#!/usr/bin/env python3
"""Test multi-turn conversation in chat mode."""

import subprocess
import time
import sys

print("Testing multi-turn conversation...", file=sys.stderr)

# Start the chat mode
proc = subprocess.Popen(
    ["python", "-m", "forge_cli", "--chat", "--quiet"],
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

# First message
proc.stdin.write("Hello\n")
proc.stdin.flush()
time.sleep(3)

# Second message
proc.stdin.write("Who are you?\n")
proc.stdin.flush()
time.sleep(3)

# Third message
proc.stdin.write("What can you help me with?\n")
proc.stdin.flush()
time.sleep(3)

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
    
# Check for errors
if "finalized" in stderr or "RuntimeError" in stderr:
    print("\n❌ Display finalization error still present")
    sys.exit(1)
elif "Error" in stderr and "Chat interrupted" not in stderr:
    print("\n❌ Other errors found")
    sys.exit(1)
else:
    print("\n✅ Multi-turn conversation works!")