# TopK Query Command

The `/topk` command allows you to query a vector store collection with top-k results directly from the chat interface.

## Usage

```
/topk <collection-id> query="<query-text>" [top_k=10]
```

### Parameters

- `<collection-id>`: The vector store ID to query (required)
- `query="<query-text>"`: The search query text in quotes (required)
- `top_k=N`: Number of results to return (optional, default: 10)

### Aliases

The command has the following aliases:
- `/query`
- `/search`

## Examples

### Basic Query
```
/topk vs_123 query="machine learning techniques"
```

### Query with Custom Top-K
```
/topk vs_456 query="neural networks" top_k=5
```

### Using Aliases
```
/query vs_789 query="artificial intelligence"
/search vs_abc query="deep learning" top_k=3
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

```
🔍 Querying collection: vs_123
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
