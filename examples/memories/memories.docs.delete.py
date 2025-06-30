"""
Example demonstrating how to delete a document from memory in Langbase.
"""
import os
from langbase import Langbase

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

# Memory and document to delete
memory_name = "product-knowledge"
document_name = "product-manual.pdf"

# Delete the document
try:
    response = lb.memories.documents.delete(
        memory_name=memory_name,
        document_name=document_name
    )

    if response.get('success', False):
        print(f"Successfully deleted document '{document_name}' from memory '{memory_name}'")
    else:
        print(f"Failed to delete document '{document_name}' from memory '{memory_name}'")

except Exception as e:
    print(f"Error deleting document: {e}")
