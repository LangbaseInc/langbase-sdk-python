"""
Example demonstrating how to delete a thread in Langbase.
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

    # Thread ID to delete
    thread_id = "thread_123"  # Replace with your actual thread ID

    # Delete the thread
    try:
        response = langbase.threads.delete(thread_id=thread_id)

        if response.get("success", False):
            print(f"Successfully deleted thread {thread_id}")
        else:
            print(f"Failed to delete thread {thread_id}")
            if "message" in response:
                print(f"Message: {response['message']}")

    except Exception as e:
        print(f"Error deleting thread: {e}")


if __name__ == "__main__":
    main()
