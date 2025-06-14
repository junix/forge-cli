#!/usr/bin/env python3
"""Simple test to see actual output."""

import subprocess
import time

# Start the chat mode
proc = subprocess.Popen(
    ["python", "-m", "forge_cli", "--chat", "-t", "file-search", "--vec-id", "test_id"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

time.sleep(2)

# Send a simple message
proc.stdin.write("Hello\n")
proc.stdin.flush()
time.sleep(5)

# Exit
proc.stdin.write("/exit\n") 
proc.stdin.flush()
time.sleep(1)

# Terminate and get output
proc.terminate()
stdout, stderr = proc.communicate()

# Show the actual output
print("=== STDOUT (last 1500 chars) ===")
print(stdout[-1500:] if len(stdout) > 1500 else stdout)