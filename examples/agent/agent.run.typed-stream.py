"""
Example demonstrating the new typed streaming interface for agent.run.

This shows how to use event-based streaming with typed events for better developer experience.
"""

import os

from dotenv import load_dotenv

from langbase import Langbase, StreamEventType, get_typed_runner

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
        # Get streaming response
        response = langbase.agent_run(
            stream=True,
            model="openai:gpt-4.1-mini",
            instructions="You are a helpful assistant that helps users summarize text.",
            input=[{"role": "user", "content": "Who is an AI Engineer?"}],
            api_key=api_key,
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

