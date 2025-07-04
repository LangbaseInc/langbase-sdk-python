"""
Example demonstrating how to create a new pipe in Langbase.
"""
import os
import json
from langbase import Langbase
from dotenv import load_dotenv

# Get API key from environment variable
load_dotenv()

langbase_api_key = os.getenv("LANGBASE_API_KEY")


# Initialize the client
lb = Langbase(api_key=langbase_api_key)


# Create the pipe
try:
    response = lb.pipes.create(
        name="summary-agent",
        description="A summary agent that helps user to summarize text.",
        model="openai:gpt-4o-mini",
        temperature=0.7,
        max_tokens=1000,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that helps user to summarize text."
            }
        ],
        upsert=True
    )

    print(json.dumps(response, indent=2))

except Exception as e:
    print(f"Error creating pipe: {e}")
