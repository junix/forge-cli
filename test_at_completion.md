# Test @ File Completion

## Test Steps:

1. Start chat mode with a vector store ID:
```bash
uv run -m forge_cli --chat --vec-id a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

2. In chat mode, check if file search is enabled:
```
/tools
```

3. If not enabled, enable it:
```
/enable-file-search
```

4. Try refreshing the file cache:
```
/refresh-files
```

5. Type @ and see if auto-completion appears

## Troubleshooting:

- Make sure the vector store ID is valid and contains files
- Check if the terminal supports interactive features
- Try in a proper terminal (not in VSCode integrated terminal)

## Expected Behavior:

When typing @, you should see a dropdown list of available files from:
1. Files in the specified vector store
2. Any files uploaded during the current chat session

The completion should show:
- File ID (what you'll use after @)
- Filename (for easy identification)