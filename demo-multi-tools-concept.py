#!/usr/bin/env python3
"""
Conceptual demonstration of using multiple tools in Knowledge Forge.

This script shows the concept and patterns for using multiple tools together
without requiring the full SDK setup.
"""

import json
from enum import Enum
from typing import Any


class ToolType(Enum):
    """Available tool types in Knowledge Forge."""

    FILE_SEARCH = "file_search"
    WEB_SEARCH = "web_search"


def create_multi_tool_request(
    question: str,
    vector_store_ids: list[str] | None = None,
    enable_web_search: bool = True,
    web_location: dict[str, str] | None = None,
    effort: str = "medium",
) -> dict[str, Any]:
    """
    Create a request that uses multiple tools.

    This demonstrates how to structure a request that leverages both
    file search (for searching documents in vector stores) and web search
    (for current information from the internet).
    """

    # Base request structure
    request = {
        "model": "qwen-max-latest",
        "effort": effort,
        "store": True,
        "input": [{"role": "user", "content": question}],
        "tools": [],
    }

    # Add file search tool if vector stores are provided
    if vector_store_ids:
        file_search_tool = {
            "type": "file_search",
            "vector_store_ids": vector_store_ids,
            "max_num_results": 10,  # Can be adjusted based on needs
        }
        request["tools"].append(file_search_tool)
        print(f"✅ Added file search tool for {len(vector_store_ids)} vector store(s)")

    # Add web search tool if enabled
    if enable_web_search:
        web_search_tool = {"type": "web_search"}

        # Add location context if provided
        if web_location:
            web_search_tool["user_location"] = {"type": "approximate", **web_location}

        # Can also add search context size
        # web_search_tool["search_context_size"] = "medium"  # low, medium, high

        request["tools"].append(web_search_tool)
        print("✅ Added web search tool")

    return request


def demonstrate_use_cases():
    """Show different use cases for multi-tool requests."""

    print("🎯 Multi-Tool Usage Examples\n")
    print("=" * 60)

    # Use Case 1: Research Assistant
    print("\n1️⃣ Research Assistant Mode")
    print("   Combines document knowledge with current web information")

    research_request = create_multi_tool_request(
        question="What are the latest developments in quantum computing and how do they compare to the foundational research?",
        vector_store_ids=["vec_quantum_papers_2020"],
        enable_web_search=True,
        effort="high",
    )

    print("\n   Request structure:")
    print(json.dumps(research_request, indent=4))

    # Use Case 2: Fact Checking
    print("\n\n2️⃣ Fact Checking Mode")
    print("   Verifies information across multiple sources")

    fact_check_request = create_multi_tool_request(
        question="Verify: The latest GPT model has 175 billion parameters. Is this accurate?",
        vector_store_ids=["vec_ai_papers", "vec_tech_docs"],
        enable_web_search=True,
        effort="medium",
    )

    print(f"\n   Tools configured: {len(fact_check_request['tools'])}")
    for tool in fact_check_request["tools"]:
        print(f"   - {tool['type']}")

    # Use Case 3: Local Context Search
    print("\n\n3️⃣ Location-Aware Search")
    print("   Combines documents with location-specific web results")

    local_request = create_multi_tool_request(
        question="What AI conferences or events are happening near me?",
        vector_store_ids=["vec_conference_database"],
        enable_web_search=True,
        web_location={"country": "US", "city": "San Francisco", "region": "California"},
        effort="low",
    )

    print(f"\n   Location context: {local_request['tools'][1].get('user_location', {})}")

    # Use Case 4: Document-Only Search
    print("\n\n4️⃣ Document-Focused Search")
    print("   Uses only file search for internal knowledge")

    doc_only_request = create_multi_tool_request(
        question="What does our internal documentation say about deployment procedures?",
        vector_store_ids=["vec_internal_docs", "vec_deployment_guides"],
        enable_web_search=False,
        effort="medium",
    )

    print(f"\n   Using {len(doc_only_request['tools'])} tool(s) - file search only")

    # Use Case 5: Web-Only Search
    print("\n\n5️⃣ Current Information Search")
    print("   Uses only web search for real-time information")

    web_only_request = create_multi_tool_request(
        question="What happened in the tech industry today?",
        vector_store_ids=None,
        enable_web_search=True,
        effort="low",
    )

    print(f"\n   Using {len(web_only_request['tools'])} tool(s) - web search only")


def show_response_handling():
    """Demonstrate how to handle responses from multi-tool requests."""

    print("\n\n📊 Response Handling Patterns")
    print("=" * 60)

    print("""
When processing responses from multi-tool requests, you'll receive events like:

1. Tool-specific events:
   - response.file_search_call.searching
   - response.file_search_call.completed
   - response.web_search_call.searching
   - response.web_search_call.completed

2. Tool results in the response:
   - File search results include document chunks with citations
   - Web search results include web page snippets and URLs

3. Combined response:
   - The AI model synthesizes information from all tools
   - Provides citations for both document and web sources
   - Can compare/contrast information from different sources

Example event flow:
1. response.created
2. response.file_search_call.searching
3. response.web_search_call.searching
4. response.file_search_call.completed (with results)
5. response.web_search_call.completed (with results)
6. response.output_text.delta (streaming text)
7. response.completed
""")


def show_best_practices():
    """Show best practices for multi-tool usage."""

    print("\n\n💡 Best Practices")
    print("=" * 60)

    best_practices = [
        {
            "title": "Tool Selection",
            "tips": [
                "Use file search for historical/reference information",
                "Use web search for current events and real-time data",
                "Combine both for comprehensive research",
            ],
        },
        {
            "title": "Performance Optimization",
            "tips": [
                "Limit max_num_results based on your needs",
                "Use appropriate effort levels (low for quick queries, high for research)",
                "Consider search_context_size for web searches",
            ],
        },
        {
            "title": "Query Design",
            "tips": [
                "Be specific about what information you need from each source",
                "Ask comparative questions to leverage both tools",
                "Include temporal context (e.g., 'latest', 'historical', 'current')",
            ],
        },
        {
            "title": "Result Interpretation",
            "tips": [
                "Check citations to understand source of information",
                "Note discrepancies between document and web sources",
                "Consider recency of information from each source",
            ],
        },
    ]

    for practice in best_practices:
        print(f"\n🔸 {practice['title']}:")
        for tip in practice["tips"]:
            print(f"   • {tip}")


if __name__ == "__main__":
    print("🚀 Knowledge Forge Multi-Tool Demonstration\n")

    # Show use cases
    demonstrate_use_cases()

    # Show response handling
    show_response_handling()

    # Show best practices
    show_best_practices()

    print("\n\n✅ For a working implementation with streaming and live updates,")
    print("   see hello-multi-tools.py (requires SDK dependencies)")
