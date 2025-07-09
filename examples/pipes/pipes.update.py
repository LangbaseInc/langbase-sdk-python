"""
Example demonstrating how to update a pipe in Langbase.
"""

import json
import os

from dotenv import load_dotenv

from langbase import Langbase


def main():
    load_dotenv()

    # Get API key from environment variable
    langbase_api_key = os.getenv("LANGBASE_API_KEY")

    # Initialize the client
    lb = Langbase(api_key=langbase_api_key)

    # Name of the pipe to update
    pipe_name = "my-summary-pipe"  # Replace with your pipe name

    # Define updated configuration
    updates = {
        "description": "Updated description for the text summarization pipe",
        "system_prompt": "You are an expert assistant that provides detailed and structured summaries.",
        "model": "openai:gpt-4",
    }

    # Update the pipe
    try:
        response = lb.pipes.update(name=pipe_name, **updates)

        print("Pipe updated successfully!")
        print(json.dumps(response, indent=2))

    except Exception as e:
        print(f"Error updating pipe: {e}")


if __name__ == "__main__":
    main()
