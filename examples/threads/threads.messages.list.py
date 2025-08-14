"""
Example demonstrating how to list threads in Langbase.
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

    # List all threads
    try:
        threads = langbase.threads.messages.list(thread_id="thread_123")

        print(json.dumps(threads, indent=2))

    except Exception as e:
        print(f"Error listing threads: {e}")


if __name__ == "__main__":
    main()
