"""
Example demonstrating how to have a conversation using a pipe in streaming mode.
"""

import os
import sys

from dotenv import load_dotenv

from langbase import Langbase, get_runner


def main():
    load_dotenv()

    langbase = Langbase(api_key=os.getenv("LANGBASE_API_KEY"))

    # Message 1: Tell something to the LLM.
    response1 = langbase.pipes.run(
        name="summary-agent",
        stream=True,
        messages=[{"role": "user", "content": "My company is called Langbase"}],
    )

    runner1 = get_runner(response1)

    # Use text_generator() to stream content
    for content in runner1.text_generator():
        print(content, end="", flush=True)

    print("\n\nStream ended!")  # Add a newline after first response

    # Message 2: Ask something about the first message.
    # Continue the conversation in the same thread by sending
    # `thread_id` from the second message onwards.
    response2 = langbase.pipes.run(
        name="summary-agent",
        stream=True,
        thread_id=response1["thread_id"],
        messages=[{"role": "user", "content": "Tell me the name of my company?"}],
    )

    runner2 = get_runner(response2)

    # Use text_generator() to stream content
    for content in runner2.text_generator():
        print(content, end="", flush=True)

    print("\n\nStream ended!")  # Add a newline after first response


if __name__ == "__main__":
    main()
