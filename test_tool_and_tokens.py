#!/usr/bin/env python3
"""Test tool messages and token statistics display."""

import subprocess
import time
import sys

print("Testing tool messages and token display...", file=sys.stderr)

# Start the chat mode with file search enabled
proc = subprocess.Popen(
    ["python", "-m", "forge_cli", "--chat", "-t", "file-search", "--vec-id", "test_vec_id"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

# Give it a moment to start
time.sleep(2)

print("Chat mode started!", file=sys.stderr)

# Send a message that should trigger file search
proc.stdin.write("Search for information about Python.\n")
proc.stdin.flush()
time.sleep(8)  # Give time for tool execution and response

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

print("\n=== CHECKING OUTPUT ===")

# Check for tool messages
tool_indicators = ["Searching documents", "file_search", "📄", "🔧"]
found_tool_msgs = []
for indicator in tool_indicators:
    if indicator in stdout:
        found_tool_msgs.append(indicator)

if found_tool_msgs:
    print(f"✅ Found tool indicators: {found_tool_msgs}")
else:
    print("⚠️  No tool messages found")

# Check for continuous token display
lines_with_tokens = []
for line in stdout.split('\n'):
    if "↑" in line and "↓" in line and "∑" in line:
        # Extract the part with tokens
        if "───" in line:  # Panel header
            lines_with_tokens.append(line.strip())

if len(lines_with_tokens) > 1:
    print(f"\n✅ Token stats appear in {len(lines_with_tokens)} panel headers!")
    print("First few occurrences:")
    for line in lines_with_tokens[:3]:
        # Show just the token part
        if "↑" in line:
            token_part = line[line.find("↑"):line.find("─", line.find("∑"))]
            print(f"  {token_part}")
else:
    print("\n⚠️  Token stats not continuously displayed")