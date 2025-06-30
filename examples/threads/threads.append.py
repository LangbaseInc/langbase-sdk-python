"""
Example demonstrating how to append messages to a thread in Langbase.
"""
import os
from langbase import Langbase

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)
# Thread ID to append messages to
thread_id = "thread_123456789"  # Replace with your actual thread ID

# Messages to append
messages = [
    {
        "role": "assistant",
        "content": "I'm sorry to hear you're having trouble with your Widget Pro 2000. What specific issue are you experiencing?"
    },
    {
        "role": "user",
        "content": "The power button is flashing red and the device won't turn on."
    }
]

# Append messages to the thread
try:
    response = lb.threads.append(
        thread_id=thread_id,
        messages=messages
    )

    print(f"Successfully appended {len(response)} messages to thread '{thread_id}'")

    # Print the appended messages
    for i, message in enumerate(response, 1):
        print(f"\nMessage {i}:")
        print(f"Role: {message.get('role')}")
        print(f"Content: {message.get('content')}")
        print(f"Created at: {message.get('created_at')}")

except Exception as e:
    print(f"Error appending messages to thread: {e}")
