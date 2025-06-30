"""
Example demonstrating how to list documents in a memory in Langbase.
"""
import os
from langbase import Langbase

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

# Memory name to list documents from
memory_name = "product-knowledge"

# List documents in the memory
try:
    documents = lb.memories.documents.list(memory_name=memory_name)

    print(f"Found {len(documents)} documents in memory '{memory_name}':")
    for doc in documents:
        print(f"- {doc['name']}")
        print(f"  Status: {doc.get('status', 'unknown')}")
        print(f"  Type: {doc.get('metadata', {}).get('type', 'unknown')}")
        print(f"  Size: {doc.get('metadata', {}).get('size', 'unknown')} bytes")
        print(f"  Enabled: {doc.get('enabled', True)}")
        if doc.get('status_message'):
            print(f"  Message: {doc['status_message']}")
        print()

except Exception as e:
    print(f"Error listing documents: {e}")
