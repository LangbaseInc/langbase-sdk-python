"""
Example demonstrating how to run a pipe with a pipe API key.
"""

import os

from dotenv import load_dotenv

from langbase import Langbase, get_runner


def main():
    load_dotenv()

    langbase = Langbase(api_key=os.getenv("LANGBASE_API_KEY"))

    user_msg = "Who is an AI Engineer?"

    # Get readable stream
    response = langbase.pipes.run(
        messages=[{"role": "user", "content": user_msg}],
        stream=True,
        raw_response=True,
        api_key=os.getenv("PIPE_API_KEY"),
    )

    runner = get_runner(response)
    print("Stream started.\n")
    # Use text_generator() to stream content
    for content in runner.text_generator():
        print(content, end="", flush=True)

    print("\n\nStream ended!")  # Add a newline after first response


if __name__ == "__main__":
    main()
