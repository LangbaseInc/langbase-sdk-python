"""
Example demonstrating how to run a pipe in streaming mode in Langbase.
"""

import os

from dotenv import load_dotenv

from langbase import Langbase


def main():
    load_dotenv()

    # Get API key from environment variable
    langbase_api_key = os.getenv("LANGBASE_API_KEY")

    # Initialize the client
    lb = Langbase(api_key=langbase_api_key)

    # Name of the pipe to run
    pipe_name = "summary-agent"  # Replace with your pipe name

    # Define messages for the conversation
    messages = [{"role": "user", "content": "Who is an AI Engineer?"}]

    # Run the pipe with streaming enabled
    try:
        response = lb.pipes.run(name=pipe_name, messages=messages, stream=True)

        # Handle streaming response
        for chunk in response["stream"]:
            if chunk.data == "[DONE]":
                break
            print(chunk.data, end="", flush=True)

        print()  # Add a newline at the end

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
