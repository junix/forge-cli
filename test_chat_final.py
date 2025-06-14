#!/usr/bin/env python3
"""Final test of chat mode."""

import subprocess
import time
import sys

print("Testing chat mode...", file=sys.stderr)

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

# Try to send a command
proc.stdin.write("/help\n")
proc.stdin.flush()
time.sleep(0.5)

# Exit
proc.stdin.write("/exit\n")
proc.stdin.flush()
time.sleep(0.5)

# Get output
try:
    stdout, stderr = proc.communicate(timeout=2)
except subprocess.TimeoutExpired:
    proc.terminate()
    stdout, stderr = proc.communicate()

print("\nSTDOUT:")
print(stdout)

if stderr:
    print("\nSTDERR:")
    print(stderr)
    
# Check for errors
if "AttributeError" in stderr or "Error" in stderr:
    print("\n❌ Errors found in chat mode")
    sys.exit(1)
else:
    print("\n✅ Chat mode works without errors!")