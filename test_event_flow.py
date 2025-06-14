#!/usr/bin/env python3
"""Test to show event flow."""

import subprocess
import time
import sys

# Start the chat mode with debug to see event numbers
proc = subprocess.Popen(
    ["python", "-m", "forge_cli", "--chat", "--effort", "high", "--debug", "--quiet"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

time.sleep(1)

# Send a message
proc.stdin.write("Calculate 10 + 5\n")
proc.stdin.flush()
time.sleep(5)

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

# Extract event numbers from stderr
print("Event sequence:")
for line in stderr.split('\n'):
    if line.strip().startswith('[') and '] response.' in line:
        print(line.strip())

# Check if reasoning events were in the sequence
reasoning_count = sum(1 for line in stderr.split('\n') if 'response.reasoning_summary_text' in line)
print(f"\nReasoning events: {reasoning_count}")