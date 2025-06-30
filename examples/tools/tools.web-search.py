"""
Example demonstrating how to use the web search tool in Langbase.
"""
import os
from langbase import Langbase

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
search_api_key = os.environ.get("EXA_API_KEY", "your-exa-key")  # Optional: search provider API key

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

# Configure the search request
search_query = "latest advancements in quantum computing 2025"

# Optional: restrict to specific domains
domains = ["arxiv.org", "nature.com", "science.org", "research.google.com"]

# Perform the web search
try:
    search_results = lb.tools.web_search(
        query=search_query,
        service="exa",  # The search service to use
        total_results=5,  # Number of results to return
        domains=domains,  # Optional: restrict to specific domains
        api_key=search_api_key  # Optional: provider-specific API key
    )

    print(f"Found {len(search_results)} results for query: '{search_query}'")
    print()

    # Display the search results
    for i, result in enumerate(search_results, 1):
        print(f"Result {i}:")
        print(f"URL: {result['url']}")
        print(f"Content snippet:")
        # Display a preview of the content (first 200 characters)
        content_preview = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
        print(content_preview)
        print("-" * 80)

except Exception as e:
    print(f"Error performing web search: {e}")
