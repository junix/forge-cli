#!/usr/bin/env python3
"""Final test of reasoning display."""

import subprocess
import time
import sys

print("Testing reasoning display...", file=sys.stderr)

# Start the chat mode with high effort and debug
proc = subprocess.Popen(
    ["python", "-m", "forge_cli", "--chat", "--effort", "high", "--debug"],
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
proc.stdin.write("Think step by step: What is 25 * 4?\n")
proc.stdin.flush()
time.sleep(10)  # Give time for reasoning and response

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

print("\n=== STDOUT (last 2000 chars) ===")
print(stdout[-2000:] if len(stdout) > 2000 else stdout)

# Check stderr for extracted reasoning text
if stderr and "DEBUG: Extracted reasoning text:" in stderr:
    print("\n✅ Reasoning text was extracted!")
    # Show the extracted text
    for line in stderr.split('\n'):
        if "DEBUG: Extracted reasoning text:" in line:
            print(f"  {line}")
else:
    print("\n⚠️  No reasoning text extraction found in debug output")

# Check for reasoning display
if "thinking" in stdout.lower() or "🤔" in stdout or "Thinking..." in stdout:
    print("\n✅ Reasoning display is working!")
else:
    print("\n⚠️  No reasoning display found in output")