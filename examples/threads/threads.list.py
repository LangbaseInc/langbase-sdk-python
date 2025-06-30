"""
Example demonstrating how to list messages in a thread in Langbase.
"""
import os
from langbase import Langbase
from datetime import datetime

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

# Thread ID to list messages from
thread_id = "thread_123456789"  # Replace with your actual thread ID

# List messages from the thread
try:
    messages = lb.threads.messages.list(thread_id=thread_id)

    print(f"Found {len(messages)} messages in thread '{thread_id}':")
    print()

    # Format and print the conversation
    for message in messages:
        # Convert timestamp to readable date (if available)
        created_at = message.get('created_at')
        if created_at:
            timestamp = datetime.fromtimestamp(created_at / 1000).strftime('%Y-%m-%d %H:%M:%S')
        else:
            timestamp = "Unknown time"

        # Get role and format for display
        role = message.get('role', 'unknown').upper()

        print(f"[{timestamp}] {role}:")
        print(message.get('content', 'No content'))
        print("-" * 50)

except Exception as e:
    print(f"Error listing messages from thread: {e}")
