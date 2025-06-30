"""
Example demonstrating how to create a memory in Langbase.
"""
import os
from langbase import Langbase

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

# Define memory configuration
memory_config = {
    "name": "product-knowledge",
    "description": "Memory store for product documentation and information",
    "embedding_model": "openai:text-embedding-3-large"  # Optional: Specify embedding model
}

# Create the memory
try:
    new_memory = lb.memories.create(**memory_config)

    print(f"Successfully created memory '{new_memory['name']}'")
    print(f"Description: {new_memory.get('description', 'N/A')}")
    print(f"Embedding model: {new_memory.get('embedding_model', 'default')}")
    print(f"URL: {new_memory.get('url', 'N/A')}")

except Exception as e:
    print(f"Error creating memory: {e}")
