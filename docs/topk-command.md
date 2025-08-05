# TopK Query Command

The `/topk` command allows you to query a vector store collection with top-k results directly from the chat interface.

## Usage

The command supports two formats:

### Simple Format (Recommended)

```bash
/topk <query-text>
```

### Flag Format (Advanced)

```bash
/topk --collection=<collection-id> --query="<query-text>" [--top-k=N]
```

### Parameters

**Simple Format:**

- `<query-text>`: The search query (can contain spaces, uses current collection and default top-k=5)

**Flag Format:**

- `--collection=<collection-id>`: The vector store ID to query (optional, uses current collection if not set)
- `--query="<query-text>"`: The search query text in quotes (required)
- `--top-k=N`: Number of results to return (optional, default: 5)

### Aliases

The command has the following aliases:

- `/query`
- `/search`

## Examples

### Simple Format Examples

```bash
/topk machine learning techniques
/topk neural networks and deep learning
/query artificial intelligence
/search natural language processing
```

### Flag Format Examples

```bash
/topk --collection=my_collection --query="machine learning techniques"
/topk --collection=my_collection --query="neural networks" --top-k=10
/topk --query="artificial intelligence"  # uses current collection
/query --collection=vs_789 --query="deep learning" --top-k=3
```

## Output Format

The command displays:

1. Query information (collection ID, query text, top-k value)
2. Results with:
   - Result number and relevance score
   - Chunk ID
   - Source file ID (if available)
   - Text content (truncated if longer than 200 characters)
   - Metadata (if available)

## Example Output

```text
🔍 Querying collection: my_collection
📝 Query: machine learning techniques
🔢 Top-K: 5

✅ Found 2 results:

📄 Result 1 (Score: 0.9500)
   ID: chunk_1
   File: file_123
   Text: Machine learning is a subset of artificial intelligence...
   Metadata: {'source': 'ml_paper.pdf'}

📄 Result 2 (Score: 0.8700)
   ID: chunk_2
   File: file_456
   Text: Neural networks are computational models inspired by biological neural networks...
   Metadata: {'source': 'nn_paper.pdf'}
```

## Error Handling

The command provides helpful error messages for:

- Missing arguments
- Invalid argument format
- Query execution failures
- Empty results

## Integration

The command is automatically registered in the chat system and available in all chat sessions. It uses the same vector store SDK as other file search functionality in the system.
