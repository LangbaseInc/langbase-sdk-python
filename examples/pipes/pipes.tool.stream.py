"""
Example demonstrating how to use get_tools_from_run_stream to extract tool calls
from a streaming response, similar to the TypeScript version.
"""

import itertools
import json
import os

from dotenv import load_dotenv

from langbase import Langbase
from langbase.helper import get_tools_from_run_stream

# Load environment variables
load_dotenv()


def main():
    # Initialize Langbase client
    langbase = Langbase(api_key=os.getenv("LANGBASE_API_KEY"))

    user_msg = "What's the weather in SF"

    # Run the pipe with streaming enabled and tools
    response = langbase.pipes.run(
        messages=[
            {
                "role": "user",
                "content": user_msg,
            }
        ],
        stream=True,
        name="summary-agent",
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

    # Split the stream into two iterators (similar to TypeScript tee())
    stream_for_response, stream_for_tool_call = itertools.tee(response["stream"], 2)

    # Extract tool calls from the stream
    tool_calls = get_tools_from_run_stream(stream_for_tool_call)
    has_tool_calls = len(tool_calls) > 0

    if has_tool_calls:
        print(json.dumps(tool_calls, indent=2))


if __name__ == "__main__":
    main()
