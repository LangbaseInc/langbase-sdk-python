"""
Example demonstrating how to append messages to a thread in Langbase.
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

    # Thread ID to append messages to
    thread_id = "thread_123"  # Replace with your actual thread ID

    # Messages to append
    messages = [
        {"role": "assistant", "content": "Nice to meet you"},
    ]

    # Append messages to the thread
    try:
        response = langbase.threads.append(thread_id=thread_id, messages=messages)

        print(f"Successfully appended {len(response)} messages to thread '{thread_id}'")

        # Print the appended messages
        for i, message in enumerate(response, 1):
            print(f"\nMessage {i}:")
            print(f"Role: {message.get('role')}")
            print(f"Content: {message.get('content')}")
            print(f"Created at: {message.get('created_at')}")

    except Exception as e:
        print(f"Error appending messages to thread: {e}")


if __name__ == "__main__":
    main()
