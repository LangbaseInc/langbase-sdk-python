"""
Example demonstrating how to retry embedding generation for a document in Langbase.

This is useful when document embedding generation has failed or needs to be refreshed.
"""
import os
from langbase import Langbase
from dotenv import load_dotenv

load_dotenv()

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

# Memory and document to retry embeddings for
memory_name = "product-knowledge"
document_name = "product-manual.pdf"

# Retry embedding generation
try:
    response = lb.memories.documents.embeddings.retry(
        memory_name=memory_name,
        document_name=document_name
    )

    if response.get('success', False):
        print(f"Successfully triggered embedding retry for document '{document_name}' in memory '{memory_name}'")
        print("The embedding generation will run asynchronously in the background.")
        print("Check the document status later to confirm completion.")
    else:
        print(f"Failed to trigger embedding retry for document '{document_name}' in memory '{memory_name}'")
        if 'message' in response:
            print(f"Message: {response['message']}")

except Exception as e:
    print(f"Error retrying embeddings: {e}")

# Optionally, check document status after triggering the retry
try:
    print("\nChecking document status...")
    documents = lb.memories.documents.list(memory_name=memory_name)

    for doc in documents:
        if doc['name'] == document_name:
            print(f"Document: {doc['name']}")
            print(f"Status: {doc.get('status', 'unknown')}")
            if doc.get('status_message'):
                print(f"Status message: {doc['status_message']}")
            print(f"Enabled: {doc.get('enabled', True)}")
            break
    else:
        print(f"Document '{document_name}' not found in memory '{memory_name}'")

except Exception as e:
    print(f"Error checking document status: {e}")
