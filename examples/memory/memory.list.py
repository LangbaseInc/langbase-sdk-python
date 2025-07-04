"""
Example demonstrating how to list all memories in your Langbase account.
"""
import os
from langbase import Langbase
from dotenv import load_dotenv
import json

load_dotenv()

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

# List all memories
try:
    response = lb.memories.list()

    print(json.dumps(response, indent=2))

except Exception as e:
    print(f"Error listing memories: {e}")
