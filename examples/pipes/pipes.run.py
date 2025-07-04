"""
Example demonstrating how to run a pipe in non-streaming mode in Langbase.
"""
import os
import json
from langbase import Langbase
from dotenv import load_dotenv
from langbase.errors import APIError

load_dotenv()

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

# Name of the pipe to run
pipe_name = "summary-agent-14"  # Replace with your pipe name

# Define messages for the conversation
messages = [
    {
        "role": "user",
        "content": "Who is an AI Engineer?"
    }
]

# Run the pipe with explicit stream=False
try:
    response = lb.pipes.run(
        name=pipe_name,
        messages=messages,
        stream=False
    )

    # Print the entire response as is
    print(json.dumps(response, indent=2))

except APIError as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
