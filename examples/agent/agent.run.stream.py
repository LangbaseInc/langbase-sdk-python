"""
Run Agent Streaming with get_runner

This example demonstrates how to run an agent with streaming response using get_runner.
"""

import os

from dotenv import load_dotenv

from langbase import Langbase, get_runner

load_dotenv()


def main():
    # Check for required environment variables
    langbase_api_key = os.environ.get("LANGBASE_API_KEY")
    api_key = os.environ.get("LLM_API_KEY")

    if not langbase_api_key:
        print("❌ Missing LANGBASE_API_KEY in environment variables.")
        print("Please set: export LANGBASE_API_KEY='your_langbase_api_key'")
        exit(1)

    # Initialize Langbase client
    langbase = Langbase(api_key=langbase_api_key)

    try:
        # Get readable stream - equivalent to const {stream} = await langbase.agent.run(...)
        response = langbase.agent_run(
            stream=True,
            model="openai:gpt-4.1-mini",
            instructions="You are a helpful assistant that help users summarize text.",
            input=[{"role": "user", "content": "Who is an AI Engineer?"}],
            api_key=api_key,
        )

        # Convert the stream to a stream runner - equivalent to getRunner(stream)
        runner = get_runner(response)

        # Event-like handling in Python
        # Method 1: Using iterator pattern (Python equivalent of event listeners)

        # Equivalent to runner.on('connect', ...)
        print("Stream started.\n")

        try:
            # Equivalent to runner.on('content', content => {...})
            for content in runner.text_generator():
                print(content, end="", flush=True)

            # Equivalent to runner.on('end', ...)
            print("\nStream ended.")

        except Exception as error:
            # Equivalent to runner.on('error', error => {...})
            print(f"Error: {error}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
