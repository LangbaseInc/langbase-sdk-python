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
    lb = Langbase(api_key=langbase_api_key)

    # List all threads
    try:
        threads = lb.threads.messages.list(
            thread_id="3a958893-6175-4d96-9053-876ff1b37227"
        )

        print(json.dumps(threads, indent=2))

    except Exception as e:
        print(f"Error listing threads: {e}")


if __name__ == "__main__":
    main()
