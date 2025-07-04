"""
Example demonstrating how to list messages in a thread in Langbase.
"""
import os
from langbase import Langbase
from datetime import datetime
from dotenv import load_dotenv
import json

load_dotenv()

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

# Thread ID to list messages from
thread_id = "thread_123456789"  # Replace with your actual thread ID

# List messages from the thread
try:
    response = lb.threads.messages.list(thread_id=thread_id)

    print(json.dumps(response, indent=2))

except Exception as e:
    print(f"Error listing messages from thread: {e}")
