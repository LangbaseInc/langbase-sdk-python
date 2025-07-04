"""
Example demonstrating how to create a memory in Langbase.
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

# Create the memory
try:
    response = lb.memories.create(
        name = "product-knowledge",
        description = "Memory store for product documentation and information",
        embedding_model = "openai:text-embedding-3-large"
    )

    print(json.dumps(response, indent=2))

except Exception as e:
    print(f"Error creating memory: {e}")
