"""
Example demonstrating how to upload documents to a memory in Langbase.
"""

import os
import pathlib

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
        document_path = pathlib.Path(__file__).parent / "document.pdf"

        # Read the file
        with open(document_path, "rb") as file:
            document_content = file.read()

        content = "Langbase is a powerful platform for building AI applications with composable AI."
        response = lb.memories.documents.upload(
            memory_name=memory_name,
            document_name="document.pdf",
            document=document_content,  # Convert string to bytes
            content_type="application/pdf",
        )
        print("Document uploaded successfully!")
        print(f"Status: {response.status_code}")

    except Exception as e:
        print(f"Error uploading documents: {e}")


if __name__ == "__main__":
    main()
