"""
Example demonstrating how to retrieve memories in Langbase.
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
    query = "What are the main features of the product?"

    try:
        response = lb.memories.retrieve(
            name=memory_name,
            query=query,
            top_k=5,  # Number of relevant memories to retrieve
        )

        print(f"Retrieved memories for query: '{query}'")
        print(json.dumps(response, indent=2))

    except Exception as e:
        print(f"Error retrieving memories: {e}")


if __name__ == "__main__":
    main()
