"""
Example demonstrating how to get thread details in Langbase.
"""
import os
from langbase import Langbase
from datetime import datetime

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

# Thread ID to get details for
thread_id = "thread_123456789"  # Replace with your actual thread ID

# Get thread details
try:
    thread = lb.threads.get(thread_id=thread_id)

    print(f"Thread ID: {thread['id']}")

    # Convert timestamp to readable date (if available)
    created_at = thread.get('created_at')
    if created_at:
        timestamp = datetime.fromtimestamp(created_at / 1000).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Created at: {timestamp}")

    # Print metadata if available
    metadata = thread.get('metadata', {})
    if metadata:
        print("Metadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")
    else:
        print("No metadata available")

except Exception as e:
    print(f"Error getting thread: {e}")
