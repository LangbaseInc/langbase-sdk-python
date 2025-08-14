"""
Example demonstrating how to have a conversation using a pipe in non-streaming mode.
"""

import json
import os

from dotenv import load_dotenv

from langbase import Langbase


def main():
    load_dotenv()

    langbase = Langbase(api_key=os.getenv("LANGBASE_API_KEY"))

    # Message 1: Tell something to the LLM.
    response1 = langbase.pipes.run(
        stream=False,
        name="summary-agent",
        messages=[{"role": "user", "content": "My company is called Langbase"}],
    )

    print(json.dumps(response1, indent=2))

    # Message 2: Continue the conversation in the same thread
    # Pass the complete conversation history including the new message
    response2 = langbase.pipes.run(
        name="summary-agent",
        stream=False,
        thread_id=response1["threadId"],
        messages=[{"role": "user", "content": "Tell me the name of my company?"}],
    )

    print(json.dumps(response2, indent=2))
    # You'll see any LLM will know the company is `Langbase`
    # since it's the same chat thread. This is how you can
    # continue a conversation in the same thread.


if __name__ == "__main__":
    main()
