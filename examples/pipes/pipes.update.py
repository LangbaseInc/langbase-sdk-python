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
    langbase = Langbase(api_key=langbase_api_key)

    # Define updated configuration
    updates = {
        "description": "Updated description for the text summarization pipe",
        "model": "openai:gpt-4",
    }

    # Update the pipe
    try:
        response = langbase.pipes.update(
            name="summary-agent",
            description="An agent that summarizes text",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes text clearly and concisely.",
                }
            ],
        )

        print("Pipe updated successfully!")
        print(json.dumps(response, indent=2))

    except Exception as e:
        print(f"Error updating pipe: {e}")


if __name__ == "__main__":
    main()
