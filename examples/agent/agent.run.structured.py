"""
Run Agent with Structured Output

This example demonstrates how to run an agent with structured output.
"""

import json
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
        exit(1)

    if not llm_api_key:
        print("❌ Missing LLM_API_KEY in environment variables.")
        exit(1)

    # Initialize Langbase client
    langbase = Langbase(api_key=langbase_api_key)

    # Define the structured output JSON schema
    math_reasoning_schema = {
        "type": "object",
        "properties": {
            "steps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "explanation": {"type": "string"},
                        "output": {"type": "string"},
                    },
                    "required": ["explanation", "output"],
                },
            },
            "final_answer": {"type": "string"},
        },
        "required": ["steps", "final_answer"],
    }

    # Run the agent with structured output
    response = langbase.agent_run(
        model="openai:gpt-4.1",
        api_key=llm_api_key,
        instructions="You are a helpful math tutor. Guide the user through the solution step by step.",
        input=[{"role": "user", "content": "How can I solve 8x + 22 = -23?"}],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "math_reasoning", "schema": math_reasoning_schema},
        },
    )

    # Parse and display the structured response
    try:
        solution = json.loads(response.get("output", "{}"))
        print("✅ Structured Output Response:")
        print(json.dumps(solution, indent=2))
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON response: {e}")
        print(f"Raw response: {response.get('output')}")


if __name__ == "__main__":
    main()
