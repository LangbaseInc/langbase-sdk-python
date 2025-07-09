"""
Example demonstrating how to list memories in Langbase.
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

    # List all memories
    try:
        response = lb.memories.list()

        print(json.dumps(response, indent=2))

    except Exception as e:
        print(f"Error listing memories: {e}")


if __name__ == "__main__":
    main()
