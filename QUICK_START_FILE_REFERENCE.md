# Quick Start: @ File Reference in Chat Mode

## Prerequisites

1. **Start chat with vector store ID**:
   ```bash
   forge-cli --chat --vec-id YOUR_VECTOR_STORE_ID
   ```

2. **Or enable file search in chat**:
   ```
   /enable-file-search
   ```

3. **Set vector store IDs if not done**:
   ```bash
   # In your environment or when starting
   export VEC_IDS=your_vector_store_id
   ```

## Using @ File References

### Step 1: Check if file search is enabled
```
/tools
```
You should see:
```
🔧 Tool Status:
  File Search: ✅ Enabled
```

### Step 2: Type @ and wait
When you type `@`, you should see available files:
- If no files appear, your vector store might be empty
- Try `/refresh-files` to refresh the file list

### Step 3: Common issues and solutions

**No completions appearing?**

1. **Check vector store has files**:
   - Use the API or web interface to verify your vector store contains files
   - The vector store ID must be valid and accessible

2. **Refresh the cache**:
   ```
   /refresh-files
   ```
   Or use aliases:
   ```
   /rf
   /refresh
   ```

3. **Upload a file first**:
   ```bash
   # Upload a file to your conversation
   forge-cli upload /path/to/file.pdf
   ```

4. **Verify terminal support**:
   - Make sure you're in an interactive terminal (not piped)
   - Some terminals may not support auto-completion

## Example Session

```bash
# Start with vector store
forge-cli --chat --vec-id vs_abc123

# In chat:
>>> /tools
🔧 Tool Status:
  File Search: ✅ Enabled
📁 Vector Stores: vs_abc123

>>> @[TAB or just wait after typing @]
# You should see file completions here

>>> @file_123 What is this document about?
# The system will analyze the specific file
```

## Troubleshooting

1. **Enable debug mode** to see what's happening:
   ```bash
   forge-cli --chat --debug --vec-id YOUR_ID
   ```

2. **Test with a known file ID**:
   If you know a file ID exists, try typing it directly:
   ```
   @known_file_id test
   ```

3. **Check server connection**:
   Make sure KNOWLEDGE_FORGE_URL is set correctly:
   ```bash
   echo $KNOWLEDGE_FORGE_URL
   ```

## Important Notes

- Files must exist in the vector store or be uploaded to the current conversation
- The @ completion shows files from:
  - Vector stores configured with `--vec-id`
  - Files uploaded during the current chat session
- File IDs are case-sensitive
- Completion requires an interactive terminal with prompt_toolkit support