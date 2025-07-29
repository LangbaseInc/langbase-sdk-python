"""
Example demonstrating how to update thread metadata in Langbase.
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

    # Thread ID to update
    thread_id = "thread_123"  # Replace with your actual thread ID

    # New metadata to set for the thread
    updated_metadata = {
        "company": "langbase",
        "about": "Langbase is the most powerful serverless platform for building AI agents with memory.",
    }

    # Update the thread metadata
    try:
        updated_thread = langbase.threads.update(
            thread_id=thread_id,
            metadata=updated_metadata,
        )

        print(json.dumps(updated_thread, indent=2))

    except Exception as e:
        print(f"Error updating thread: {e}")


if __name__ == "__main__":
    main()
