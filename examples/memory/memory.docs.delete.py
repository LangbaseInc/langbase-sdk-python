"""
Example demonstrating how to delete documents from a memory in Langbase.
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

    # Memory name and document ID to delete
    memory_name = "product-knowledge"  # Replace with your memory name
    document_name = "intro.txt"  # Replace with the document name you want to delete

    # Delete the document
    try:
        response = lb.memories.documents.delete(
            memory_name=memory_name, document_name=document_name
        )

        print(
            f"Document '{document_name}' deleted successfully from memory '{memory_name}'"
        )
        print(json.dumps(response, indent=2))

    except Exception as e:
        print(f"Error deleting document: {e}")


if __name__ == "__main__":
    main()
