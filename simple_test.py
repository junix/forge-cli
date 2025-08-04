#!/usr/bin/env python3
"""Simple test to check imports."""

import sys

sys.path.insert(0, ".")

try:
    print("Testing imports...")

    # Test config import
    from src.forge_cli.config import AppConfig

    print("✅ AppConfig imported")

    # Test conversation import
    from src.forge_cli.models.conversation import ConversationState

    print("✅ ConversationState imported")

    # Test basic creation
    config = AppConfig()
    print(f"✅ AppConfig created with model: {config.model}")

    # Test conversation creation
    conversation = ConversationState()
    print(f"✅ ConversationState created with model: {conversation.model}")

    print("🎉 Basic functionality works!")

except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")
    import traceback

    traceback.print_exc()
