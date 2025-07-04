"""
Example demonstrating how to get thread details in Langbase.
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

# Thread ID to get details for
thread_id = "thread_123456789"  # Replace with your actual thread ID

# Get thread details
try:
    thread = lb.threads.get(thread_id=thread_id)
    print(json.dumps(thread, indent=2))

except Exception as e:
    print(f"Error getting thread: {e}")
