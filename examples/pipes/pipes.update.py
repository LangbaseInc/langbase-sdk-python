"""
Example demonstrating how to update an existing pipe in Langbase.
"""
import os
from langbase import Langbase

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

# Name of the pipe to update
pipe_name = "my-assistant-pipe"

# Define update configuration
update_config = {
    "name": pipe_name,
    "description": "An updated assistant that provides more detailed responses",
    "temperature": 0.8,  # Adjust temperature
    "max_tokens": 2000,  # Increase output length
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant that provides detailed, informative responses while still being concise and to the point."
        }
    ]
}

# Update the pipe
try:
    updated_pipe = lb.pipes.update(**update_config)

    print(f"Successfully updated pipe '{updated_pipe['name']}'")
    print(f"New description: {updated_pipe.get('description', 'N/A')}")
    print(f"Status: {updated_pipe.get('status', 'unknown')}")

except Exception as e:
    print(f"Error updating pipe: {e}")
