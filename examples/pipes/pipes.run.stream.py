"""
Example demonstrating how to run a pipe with streaming in Langbase.
"""
import os
import json
from langbase import Langbase

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

# Name of the pipe to run
pipe_name = "my-assistant-pipe"

# Define messages for the conversation
messages = [
    {
        "role": "user",
        "content": "Write a short story about a robot learning to paint."
    }
]

# Run the pipe with streaming enabled
try:
    stream_response = lb.pipes.run(
        name=pipe_name,
        messages=messages,
        stream=True
    )

    print("Thread ID:", stream_response['thread_id'])

    print("STREAMING RESPONSE:")

    # Process each chunk as it arrives
    for chunk in stream_response["stream"]:
        if chunk:
            try:
                # Try to decode as JSON
                chunk_data = json.loads(chunk.decode('utf-8'))
                if "completion" in chunk_data:
                    print(chunk_data["completion"], end="", flush=True)
            except json.JSONDecodeError:
                # If not JSON, print raw decoded chunk
                print(chunk.decode('utf-8'), end="", flush=True)

    print("\n\nStream completed")

except Exception as e:
    print(f"Error streaming from pipe: {e}")
