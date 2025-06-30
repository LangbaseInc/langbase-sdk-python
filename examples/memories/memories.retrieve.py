"""
Example demonstrating how to retrieve information from memory in Langbase.
"""
import os
from langbase import Langbase

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

    print(f"Found {len(results)} results for query: '{query}'")
    print()

    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"Similarity score: {result['similarity']:.4f}")
        print(f"Metadata: {result.get('meta', {})}")
        print("Content:")
        print("-" * 80)
        print(result['text'])
        print("-" * 80)
        print()

except Exception as e:
    print(f"Error retrieving from memory: {e}")
