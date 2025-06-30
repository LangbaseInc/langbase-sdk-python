"""
Example demonstrating how to create a thread in Langbase.
"""
import os
from langbase import Langbase

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

# Create a thread with metadata and initial messages
try:
    thread = lb.threads.create(
        metadata={
            "user_id": "user_12345",
            "session_id": "session_67890",
            "topic": "technical_support",
            "product": "Widget Pro 2000"
        },
        messages=[
            {
                "role": "user",
                "content": "Hello, I'm having trouble with my Widget Pro 2000."
            }
        ]
    )

    print(f"Successfully created thread with ID: {thread['id']}")
    print(f"Creation timestamp: {thread.get('created_at')}")
    print(f"Metadata: {thread.get('metadata', {})}")

    # Save the thread ID for later use
    thread_id = thread['id']
    print(f"\nSave this thread ID for future interactions: {thread_id}")

except Exception as e:
    print(f"Error creating thread: {e}")
