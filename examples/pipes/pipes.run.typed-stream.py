"""
Example demonstrating the new typed streaming interface for pipes.

This shows how to use event-based streaming with typed events for better developer experience.
"""

import os

from dotenv import load_dotenv

from langbase import Langbase, StreamEventType, get_typed_runner


def main():
    load_dotenv()

    # Get API key from environment variable
    langbase_api_key = os.getenv("LANGBASE_API_KEY")

    # Initialize the client
    lb = Langbase(api_key=langbase_api_key)

    # Name of the pipe to run
    pipe_name = "summary-agent"  # Replace with your pipe name

    try:
        # Get streaming response
        response = lb.pipes.run(
            name=pipe_name,
            messages=[{"role": "user", "content": "What is an AI Engineer?"}],
            stream=True,
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
