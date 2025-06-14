#!/usr/bin/env python3
"""Test reasoning display in chat mode."""

import subprocess
import time
import sys

print("Testing reasoning display...", file=sys.stderr)

# Start the chat mode with effort=high to trigger reasoning
proc = subprocess.Popen(
    ["python", "-m", "forge_cli", "--chat", "--effort", "high", "--debug"],
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

# Ask a complex question to trigger reasoning
proc.stdin.write("What are the implications of quantum computing on cryptography?\n")
proc.stdin.flush()
time.sleep(10)  # Give more time for reasoning

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

print("\n=== STDOUT (first 3000 chars) ===")
print(stdout[:3000] if len(stdout) > 3000 else stdout)

# Check for reasoning indicators
if "reasoning" in stdout.lower() or "thinking" in stdout.lower() or "🤔" in stdout:
    print("\n✅ Reasoning display appears to be working!")
else:
    print("\n⚠️  No reasoning indicators found in output")
    
# Check debug output for reasoning events
if stderr and "response.reasoning_summary_text" in stderr:
    print("\n✅ Reasoning events were fired")
else:
    print("\n⚠️  No reasoning events found in debug output")