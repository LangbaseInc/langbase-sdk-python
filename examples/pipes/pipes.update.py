"""
Example demonstrating how to update an existing pipe in Langbase.
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

# Update the pipe
try:
    response = lb.pipes.update(
        name = "summary-agent",
        description = "An updated assistant that provides more detailed responses",
        temperature = 0.8,
        max_tokens = 2000,
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that provides detailed, informative responses while still being concise and to the point."
            }
        ]
    )

    print(json.dumps(response, indent=2))

except Exception as e:
    print(f"Error updating pipe: {e}")
