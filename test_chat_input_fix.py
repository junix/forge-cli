#!/usr/bin/env python3
"""Test the chat mode input fix."""

import subprocess
import time
import sys

print("Testing chat mode with fixed input...", file=sys.stderr)

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

# Try to send a message
proc.stdin.write("hello\n")
proc.stdin.flush()
time.sleep(2)

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

print("\nSTDOUT:")
print(stdout)

if stderr:
    print("\nSTDERR:")
    print(stderr)
    
# Check for the specific validation error
if "ValidationError" in stderr or "Pydantic" in stderr:
    print("\n❌ Validation error still present")
    sys.exit(1)
elif "Error" in stderr:
    print("\n❌ Other errors found")
    sys.exit(1)
else:
    print("\n✅ Chat mode works without validation errors!")