"""
Example demonstrating how to list documents in a memory in Langbase.
"""
import os
from langbase import Langbase
import json
from dotenv import load_dotenv

load_dotenv()

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

# List documents in the memory
try:
    response = lb.memories.documents.list()

    print(json.dumps(response, indent=2))

except Exception as e:
    print(f"Error listing documents: {e}")
