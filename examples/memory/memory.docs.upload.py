"""
Example demonstrating how to upload documents to a memory in Langbase.
"""

import os

from dotenv import load_dotenv

from langbase import Langbase


def main():
    load_dotenv()

    # Get API key from environment variable
    langbase_api_key = os.getenv("LANGBASE_API_KEY")

    # Initialize the client
    langbase = Langbase(api_key=langbase_api_key)

    # Memory name to upload documents to
    memory_name = "product-knowledge"  # Replace with your memory name

    # Upload documents to the memory
    try:
        content = "Langbase is a powerful platform for building AI applications with composable AI."
        response = langbase.memories.documents.upload(
            memory_name=memory_name,
            document_name="intro.txt",
            document=content.encode("utf-8"),  # Convert string to bytes
            content_type="text/plain",
            meta={"source": "documentation", "section": "introduction"},
        )
        print("Document uploaded successfully!")
        print(f"Status: {response.status_code}")

    except Exception as e:
        print(f"Error uploading documents: {e}")


if __name__ == "__main__":
    main()
