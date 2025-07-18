"""
Example demonstrating how to chunk text content using Langbase.
"""

import json
import os
import pathlib

from dotenv import load_dotenv

from langbase import Langbase

load_dotenv()

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)


def main():
    """
    Chunks text content using Langbase.
    """
    try:
        # Get the path to the document
        document_path = pathlib.Path(__file__).parent / "composable-ai.md"

        # Read the file
        with open(document_path, "r", encoding="utf-8") as file:
            document_content = file.read()
        # Chunk the content
        chunks = lb.chunker(
            content=document_content, chunk_max_length=1024, chunk_overlap=256
        )

        print(json.dumps(chunks, indent=2))

    except Exception as e:
        print(f"Error chunking content: {e}")


if __name__ == "__main__":
    main()
