"""
Example demonstrating how to create a thread in Langbase.
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

# Create a thread with metadata and initial messages
try:
    thread = lb.threads.create(
        metadata={
           "company": 'langbase'
        },
        messages=[
            {
                "role": "user",
                "content": "Hello, how are you?"
            }
        ]
    )

    print(json.dumps(thread, indent=2))

except Exception as e:
    print(f"Error creating thread: {e}")
