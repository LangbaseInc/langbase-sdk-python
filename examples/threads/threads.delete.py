"""
Example demonstrating how to delete a thread in Langbase.
"""
import os
from langbase import Langbase
from dotenv import load_dotenv

load_dotenv()

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

# Thread ID to delete
thread_id = "431bac51-929c-4257-8251-baefcd251d3a"  # Replace with your actual thread ID

# Delete the thread
try:
    response = lb.threads.delete(thread_id=thread_id)

    if response.get('success', False):
        print(f"Successfully deleted thread {thread_id}")
    else:
        print(f"Failed to delete thread {thread_id}")
        if 'message' in response:
            print(f"Message: {response['message']}")

except Exception as e:
    print(f"Error deleting thread: {e}")
