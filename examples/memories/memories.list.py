"""
Example demonstrating how to list all memories in your Langbase account.
"""
import os
from langbase import Langbase

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

# List all memories
try:
    memories = lb.memories.list()

    print(f"Found {len(memories)} memories:")
    for memory in memories:
        print(f"- {memory['name']}: {memory.get('description', 'No description')}")
        print(f"  Embedding model: {memory.get('embedding_model', 'default')}")
        print(f"  Owner: {memory.get('owner_login', 'unknown')}")
        print()

except Exception as e:
    print(f"Error listing memories: {e}")
