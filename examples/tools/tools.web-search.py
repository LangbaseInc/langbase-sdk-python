"""
Example demonstrating how to use the web search tool in Langbase.
"""

import json
import os

from dotenv import load_dotenv

from langbase import Langbase


def main():
    load_dotenv()

    # Get API key from environment variable
    langbase_api_key = os.getenv("LANGBASE_API_KEY")

    # Initialize the client
    search_api_key = os.getenv("EXA_API_KEY")

    # Initialize the client
    lb = Langbase(api_key=langbase_api_key)

    # Configure the search request
    search_query = "latest advancements in quantum computing 2025"

    # Optional: restrict to specific domains
    domains = ["arxiv.org", "nature.com", "science.org"]

    # Perform the web search
    try:
        search_results = lb.tools.web_search(
            query=search_query,
            service="exa",  # The search service to use
            total_results=5,  # Number of results to return
            domains=domains,  # Optional: restrict to specific domains
            api_key=search_api_key,  # Optional: provider-specific API key
        )

        print(json.dumps(search_results, indent=2))

    except Exception as e:
        print(f"Error performing web search: {e}")


if __name__ == "__main__":
    main()
