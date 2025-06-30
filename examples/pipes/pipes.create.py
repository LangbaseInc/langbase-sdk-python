"""
Example demonstrating how to create a new pipe in Langbase.
"""
import os
from langbase import Langbase

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

# Define pipe configuration
pipe_config = {
    "name": "my-assistant-pipe",  # Unique name for your pipe
    "description": "An assistant that helps with general inquiries",
    "model": "openai:gpt-4o-2024-11-20",  # Adjust to your preferred model
    "temperature": 0.7,
    "max_tokens": 1000,
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant that provides concise, accurate responses."
        }
    ]
}

# Create the pipe
try:
    new_pipe = lb.pipes.create(**pipe_config)

    print(f"Successfully created pipe '{new_pipe['name']}'")
    print(f"Pipe API Key: {new_pipe.get('api_key', 'N/A')}")
    print(f"Status: {new_pipe.get('status', 'unknown')}")
    print(f"URL: {new_pipe.get('url', 'N/A')}")

except Exception as e:
    print(f"Error creating pipe: {e}")
