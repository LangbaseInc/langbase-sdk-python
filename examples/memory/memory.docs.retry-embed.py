"""
Example demonstrating how to retry embedding for documents in a memory in Langbase.
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

    # Memory name to retry embedding for
    memory_name = "product-knowledge"  # Replace with your memory name

    # Retry embedding for failed documents
    try:
        response = lb.memories.docs.retry_embed(name=memory_name)

        print(f"Retry embedding initiated for memory '{memory_name}'")
        print(json.dumps(response, indent=2))

    except Exception as e:
        print(f"Error retrying embedding: {e}")


if __name__ == "__main__":
    main()
