#!/usr/bin/env python3
"""Test script for ShowDocumentCommand and ShowCollectionCommand."""

def test_command_creation():
    """Test that commands can be created and have correct properties."""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    from forge_cli.chat.commands.files import ShowDocumentCommand, ShowCollectionCommand
    
    # Test ShowDocumentCommand
    doc_cmd = ShowDocumentCommand()
    assert doc_cmd.name == "show-doc"
    assert "doc" in doc_cmd.aliases
    assert "document" in doc_cmd.aliases
    assert "file-info" in doc_cmd.aliases
    print("✅ ShowDocumentCommand: Basic properties correct")
    
    # Test ShowCollectionCommand
    col_cmd = ShowCollectionCommand()
    assert col_cmd.name == "show-collection"
    assert "collection" in col_cmd.aliases
    assert "vs" in col_cmd.aliases
    assert "show-vs" in col_cmd.aliases
    print("✅ ShowCollectionCommand: Basic properties correct")

def test_utility_functions():
    """Test utility functions like file size formatting."""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    from forge_cli.chat.commands.files import ShowDocumentCommand, ShowCollectionCommand
    
    doc_cmd = ShowDocumentCommand()
    col_cmd = ShowCollectionCommand()
    
    # Test file size formatting
    assert doc_cmd._format_file_size(500) == "500 bytes"
    assert doc_cmd._format_file_size(1536) == "1.5 KB"
    assert doc_cmd._format_file_size(2097152) == "2.0 MB"
    assert doc_cmd._format_file_size(1073741824) == "1.0 GB"
    print("✅ File size formatting: All tests passed")
    
    # Test collection file size formatting (should be same function)
    assert col_cmd._format_file_size(1024) == "1.0 KB"
    print("✅ Collection file size formatting: Working correctly")
    
    # Test status emoji
    assert doc_cmd._get_status_emoji("completed") == "✅"
    assert doc_cmd._get_status_emoji("pending") == "⏳"
    assert doc_cmd._get_status_emoji("failed") == "❌"
    assert doc_cmd._get_status_emoji("unknown") == "📄"  # fallback
    print("✅ Status emoji mapping: All tests passed")

def test_datetime_formatting():
    """Test datetime formatting functions."""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    from forge_cli.chat.commands.files import ShowDocumentCommand
    from datetime import datetime
    
    cmd = ShowDocumentCommand()
    
    # Test with datetime object
    test_dt = datetime(2023, 10, 27, 14, 30, 0)
    formatted = cmd._format_datetime(test_dt)
    assert "2023-10-27 14:30:00" == formatted
    print("✅ Datetime formatting: Working correctly")
    
    # Test with string (fallback)
    formatted_str = cmd._format_datetime("2023-10-27")
    assert formatted_str == "2023-10-27"
    print("✅ Datetime string fallback: Working correctly")

def test_command_registration():
    """Test that commands are properly registered."""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    from forge_cli.chat.commands.base import CommandRegistry
    
    registry = CommandRegistry()
    
    # Test that show-doc command is registered
    show_doc_cmd = registry.get_command("show-doc")
    assert show_doc_cmd is not None
    assert show_doc_cmd.name == "show-doc"
    print("✅ show-doc command registration: Working correctly")
    
    # Test aliases
    doc_cmd = registry.get_command("doc")
    assert doc_cmd is not None
    assert doc_cmd.name == "show-doc"
    print("✅ doc alias registration: Working correctly")
    
    # Test show-collection command
    show_col_cmd = registry.get_command("show-collection")
    assert show_col_cmd is not None
    assert show_col_cmd.name == "show-collection"
    print("✅ show-collection command registration: Working correctly")
    
    # Test collection alias
    col_cmd = registry.get_command("collection")
    assert col_cmd is not None
    assert col_cmd.name == "show-collection"
    print("✅ collection alias registration: Working correctly")
    
    # Test vs alias
    vs_cmd = registry.get_command("vs")
    assert vs_cmd is not None
    assert vs_cmd.name == "show-collection"
    print("✅ vs alias registration: Working correctly")

if __name__ == "__main__":
    print("🧪 Testing ShowDocumentCommand and ShowCollectionCommand...\n")
    
    try:
        test_command_creation()
        test_utility_functions()
        test_datetime_formatting()
        test_command_registration()
        print("\n🎉 All tests passed! Show commands are ready to use.")
        print("\n📋 Available commands:")
        print("  • /show-doc <doc-id> (aliases: /doc, /document, /file-info)")
        print("  • /show-collection <collection-id> (aliases: /collection, /vs, /show-vs)")
        print("  • /show-collection <collection-id> --summary (includes summary)")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)