"""
Example demonstrating how to update thread metadata in Langbase.
"""
import os
from langbase import Langbase
from datetime import datetime

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

# Thread ID to update
thread_id = "thread_123456789"  # Replace with your actual thread ID

# New metadata to set for the thread
updated_metadata = {
    "status": "resolved",
    "priority": "high",
    "last_updated_by": "support_agent_42",
    "category": "technical_issue",
    "customer_satisfaction": "high",
    "resolution_time": "2 hours"
}

# Update the thread metadata
try:
    updated_thread = lb.threads.update(
        thread_id=thread_id,
        metadata=updated_metadata
    )

    print(f"Successfully updated thread {updated_thread['id']}")

    # Convert timestamp to readable date (if available)
    created_at = updated_thread.get('created_at')
    if created_at:
        timestamp = datetime.fromtimestamp(created_at / 1000).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Created at: {timestamp}")

    # Print updated metadata
    metadata = updated_thread.get('metadata', {})
    if metadata:
        print("Updated metadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")
    else:
        print("No metadata available")

except Exception as e:
    print(f"Error updating thread: {e}")
