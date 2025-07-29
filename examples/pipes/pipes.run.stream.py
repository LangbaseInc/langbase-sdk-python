"""
Example demonstrating how to run a pipe in streaming mode using get_runner in Langbase.
"""

import os

from dotenv import load_dotenv

from langbase import Langbase, get_runner


def main():
    load_dotenv()

    # Get API key from environment variable
    langbase_api_key = os.getenv("LANGBASE_API_KEY")

    # Initialize the client
    langbase = Langbase(api_key=langbase_api_key)

    # Name of the pipe to run
    pipe_name = "summary-agent"  # Replace with your pipe name

    try:
        # Message 1: Tell something to the LLM.
        print("Stream started \n\n")
        response1 = langbase.pipes.run(
            name=pipe_name,
            messages=[{"role": "user", "content": "What is an AI Engineer?"}],
            stream=True,
        )

        runner1 = get_runner(response1)

        # Use text_generator() to stream content
        for content in runner1.text_generator():
            print(content, end="", flush=True)

        print("\n\nStream ended!")  # Add a newline after first response

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
