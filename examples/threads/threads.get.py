"""
Example demonstrating how to get a specific thread in Langbase.
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

    # Thread ID to retrieve
    thread_id = "thread_123"  # Replace with your thread ID

    # Get the specific thread
    try:
        thread = lb.threads.get(thread_id=thread_id)

        print(json.dumps(thread, indent=2))

    except Exception as e:
        print(f"Error getting thread: {e}")


if __name__ == "__main__":
    main()
