curl -X POST "http://api-paas-dev.yunxuetang.com.cn/knowledge-forge/v1/responses" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "model": "qwen3-235b-a22b",
    "input": "What is knowledge management?",
    "effort": "low",
    "instructions": "You are a helpful assistant that provides concise and accurate information.",
    "temperature": 0.7,
    "max_output_tokens": 500,
  }'
