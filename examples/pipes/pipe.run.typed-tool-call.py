import json
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
            messages=[{"role": "user", "content": "What is the weather in Tokyo?"}],
            stream=True,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "get_current_weather",
                        "description": "Get the current weather of a given location",
                        "parameters": {
                            "type": "object",
                            "required": ["location"],
                            "properties": {
                                "unit": {
                                    "enum": ["celsius", "fahrenheit"],
                                    "type": "string",
                                },
                                "location": {
                                    "type": "string",
                                    "description": "The city and state, e.g. San Francisco, CA",
                                },
                            },
                        },
                    },
                }
            ],
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
                f"\n🔧 Tool call: {json.dumps(event['toolCall'], indent=2)}"
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
