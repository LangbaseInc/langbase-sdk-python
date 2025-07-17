"""
Example demonstrating how to chunk text content using Langbase.
"""

import json
import os

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
        # Sample text content to chunk
        content = """Langbase is the most powerful serverless AI platform for building AI agents with memory.
        Build, deploy, and scale AI agents with tools and memory (RAG). Simple AI primitives with
        a world-class developer experience without using any frameworks.

        With Langbase, you can compose multiple models together into pipelines. It's easier to
        think about, easier to develop for, and each pipe lets you choose which model to use for
        each task. You can see cost of every step. And allow your customers to hyper-personalize.

        Maybe you want to use a smaller, domain-specific model for one task, and a larger
        general-purpose model for another task. Langbase makes it easy to use the right primitives
        and tools for each part of the job and provides developers with a zero-config composable
        AI infrastructure."""

        # Chunk the content
        chunks = lb.chunker(content=content, chunk_max_length=1024, chunk_overlap=256)

        print(json.dumps(chunks, indent=2))

    except Exception as e:
        print(f"Error chunking content: {e}")


if __name__ == "__main__":
    main()
