"""
Run Agent Streaming

This example demonstrates how to run an agent with streaming response.
"""

import os
import sys

from dotenv import load_dotenv

from langbase import Langbase
from langbase.helper import stream_text

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

    # Run the agent with streaming
    response = langbase.agent_run(
        stream=True,
        model="openai:gpt-4.1-mini",
        api_key=llm_api_key,
        instructions="You are a helpful assistant that help users summarize text.",
        input=[{"role": "user", "content": "Who is an AI Engineer?"}],
    )

    print("Stream started.\n")

    # Process the streaming response
    for line in response.iter_lines():
        if line:
            line_str = line.decode("utf-8")
            if line_str.startswith("data: "):
                data = line_str[6:]  # Remove 'data: ' prefix
                if data.strip() == "[DONE]":
                    print("\nStream ended.")
                    break
                try:
                    import json

                    json_data = json.loads(data)
                    if "choices" in json_data and len(json_data["choices"]) > 0:
                        delta = json_data["choices"][0].get("delta", {})
                        if "content" in delta:
                            sys.stdout.write(delta["content"])
                            sys.stdout.flush()
                except json.JSONDecodeError:
                    # Skip invalid JSON lines
                    continue


if __name__ == "__main__":
    main()
