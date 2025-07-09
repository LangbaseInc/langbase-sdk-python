"""
Run Agent

This example demonstrates how to run an agent with a user message.
"""

import os

from dotenv import load_dotenv

from langbase import Langbase

load_dotenv()


def main():
    # Check for required environment variables
    langbase_api_key = os.environ.get("LANGBASE_API_KEY")
    llm_api_key = os.environ.get("LLM_API_KEY")

    if not langbase_api_key:
        print("❌ Missing LANGBASE_API_KEY in environment variables.")
        print("Please set: export LANGBASE_API_KEY='your_langbase_api_key'")
        exit(1)

    if not llm_api_key:
        print("❌ Missing LLM_API_KEY in environment variables.")
        print("Please set: export LLM_API_KEY='your_llm_api_key'")
        exit(1)

    # Initialize Langbase client
    langbase = Langbase(api_key=langbase_api_key)

    # Run the agent
    response = langbase.agent_run(
        stream=False,
        model="openai:gpt-4.1-mini",
        api_key=llm_api_key,
        instructions="You are a helpful assistant that help users summarize text.",
        input=[{"role": "user", "content": "Who is an AI Engineer?"}],
    )

    print("response:", response.get("output"))


if __name__ == "__main__":
    main()
