"""
Example demonstrating how to retrieve memories in Langbase.

This example shows how to retrieve memories using a query. The memory parameter
expects a list of dictionaries with 'name' keys specifying which memories to search.
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
    lb = Langbase(api_key=langbase_api_key)

    # Retrieve memories using a query
    memory_name = "product-knowledge"  # Replace with your memory name
    query = "What is Langbase?"

    try:
        response = lb.memories.retrieve(
            query=query,
            memory=[{"name": memory_name}],
            top_k=5,  # Number of relevant memories to retrieve
        )

        print(f"Retrieved memories for query: '{query}'")
        print(json.dumps(response, indent=2))

    except Exception as e:
        print(f"Error retrieving memories: {e}")


if __name__ == "__main__":
    main()
