"""
Example demonstrating how to upload documents to a memory in Langbase.
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

    # Memory name to upload documents to
    memory_name = "product-knowledge"  # Replace with your memory name

    # Upload documents to the memory
    try:
        response = lb.memories.docs.upload(
            name=memory_name,
            documents=[
                {
                    "content": "Langbase is a powerful platform for building AI applications with composable AI.",
                    "metadata": {"source": "documentation", "section": "introduction"},
                },
                {
                    "content": "The platform supports various AI models and provides tools for memory management.",
                    "metadata": {"source": "documentation", "section": "features"},
                },
            ],
        )

        print("Documents uploaded successfully!")
        print(json.dumps(response, indent=2))

    except Exception as e:
        print(f"Error uploading documents: {e}")


if __name__ == "__main__":
    main()
