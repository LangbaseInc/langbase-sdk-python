"""
Example demonstrating how to list documents in a memory in Langbase.
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
    langbase = Langbase(api_key=langbase_api_key)

    # Memory name to list documents from
    memory_name = "product-knowledge"  # Replace with your memory name

    # List documents in the memory
    try:
        response = langbase.memories.documents.list(memory_name=memory_name)

        print(f"Documents in memory '{memory_name}':")
        print(json.dumps(response, indent=2))

    except Exception as e:
        print(f"Error listing documents: {e}")


if __name__ == "__main__":
    main()
