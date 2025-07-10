"""
Example demonstrating how to create a pipe in Langbase.
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

    # Create the pipe
    try:
        response = lb.pipes.create(
            name="summary-agent",
            description="A pipe for text summarization",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes text clearly and concisely.",
                }
            ],
            upsert=True
        )

        print("Pipe created successfully!")
        print(json.dumps(response, indent=2))

    except Exception as e:
        print(f"Error creating pipe: {e}")


if __name__ == "__main__":
    main()
