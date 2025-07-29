"""
Run Agent

This example demonstrates how to run an agent with a Typed Stream
"""

import os

from dotenv import load_dotenv

from langbase import Langbase, StreamEventType, get_typed_runner

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
    try:
        # Get streaming response
        response = langbase.agent.run(
            stream=True,
            model="openai:gpt-4.1-mini",
            api_key=llm_api_key,
            instructions="You are a helpful assistant that help users summarize text.",
            input=[{"role": "user", "content": "Who is an AI Engineer?"}],
        )

        # Create typed stream processor
        runner = get_typed_runner(response)

        # Register event handlers
        runner.on(
            StreamEventType.CONNECT,
            lambda event: print(f"✓ Connected! Thread ID: {event['threadId']}\n"),
        )

        runner.on(
            StreamEventType.CONTENT,
            lambda event: print(event["content"], end="", flush=True),
        )

        runner.on(
            StreamEventType.TOOL_CALL,
            lambda event: print(
                f"\n🔧 Tool call: {event['toolCall']['function']['name']}"
            ),
        )

        runner.on(
            StreamEventType.COMPLETION,
            lambda event: print(f"\n\n✓ Completed! Reason: {event['reason']}"),
        )

        runner.on(
            StreamEventType.ERROR,
            lambda event: print(f"\n❌ Error: {event['message']}"),
        )

        runner.on(
            StreamEventType.END,
            lambda event: print(f"⏱️  Total duration: {event['duration']:.2f}s"),
        )

        # Process the stream
        runner.process()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
