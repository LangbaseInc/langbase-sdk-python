"""
Example demonstrating how to retrieve information from memory in Langbase.
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

# Memory name to retrieve from
memory_name = "product-knowledge"

# Query to search for
query = "How do I reset my Widget Pro 2000?"

# Retrieve relevant information
try:
    results = lb.memories.retrieve(
        query=query,
        memory=[{"name": memory_name}],  # Can include multiple memories
        top_k=3  # Return top 3 most relevant chunks
    )

    print(json.dumps(results, indent=2))

except Exception as e:
    print(f"Error retrieving from memory: {e}")
