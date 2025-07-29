"""
Example demonstrating how to run a pipe with an LLM API key in streaming mode.
"""

import os
import sys

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
        name="summary-agent",
        llm_key=os.getenv("LLM_KEY"),  # Your LLM API key
    )

    # Convert the stream to a stream runner.
    runner = get_runner(response)

    # Use text_generator() to stream content
    for content in runner.text_generator():
        print(content, end="", flush=True)


if __name__ == "__main__":
    main()
