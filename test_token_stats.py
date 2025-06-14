#!/usr/bin/env python3
"""Test token statistics display."""

import subprocess
import time
import sys

print("Testing token statistics display...", file=sys.stderr)

# Start the chat mode
proc = subprocess.Popen(
    ["python", "-m", "forge_cli", "--chat"],
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

# Send a message
proc.stdin.write("Hello, please give me a brief response.\n")
proc.stdin.flush()
time.sleep(5)  # Give time for response

# Exit
proc.stdin.write("/exit\n") 
proc.stdin.flush()
time.sleep(1)

# Get output
try:
    stdout, stderr = proc.communicate(timeout=3)
except subprocess.TimeoutExpired:
    proc.terminate()
    stdout, stderr = proc.communicate()

print("\n=== CHECKING FOR TOKEN STATS ===")

# Look for token indicators in output
token_indicators = ["↑", "↓", "∑", "input_tokens", "output_tokens", "total_tokens"]
found_indicators = []

for indicator in token_indicators:
    if indicator in stdout:
        found_indicators.append(indicator)

if found_indicators:
    print(f"✅ Found token indicators: {found_indicators}")
    # Try to extract the token counts
    lines = stdout.split('\n')
    for line in lines:
        if any(indicator in line for indicator in ["↑", "↓", "∑"]):
            print(f"Token line: {line}")
else:
    print("⚠️  No token statistics found in output")

# Also check if they appear in the panel headers
if "───" in stdout and any(char in stdout for char in ["↑", "↓", "∑"]):
    print("\n✅ Token stats appear to be in panel headers!")
else:
    print("\n⚠️  Token stats not found in panel headers")