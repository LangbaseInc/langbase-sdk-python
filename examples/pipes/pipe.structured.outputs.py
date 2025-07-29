"""
Example demonstrating how to use structured outputs with a pipe.
"""

import json
import os
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langbase import Langbase


# Define the Strucutred Output JSON schema with Pydantic
class Step(BaseModel):
    explanation: str
    output: str


class MathReasoning(BaseModel):
    steps: List[Step]
    final_answer: str = Field(alias="final_answer")


def create_math_tutor_pipe(langbase: Langbase):
    json_schema = MathReasoning.model_json_schema()

    pipe = langbase.pipes.create(
        name="math-tutor",
        model="openai:gpt-4o",
        upsert=True,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful math tutor. Guide the user through the solution step by step.",
            },
        ],
        json=True,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "math_reasoning",
                "schema": json_schema,
            },
        },
    )

    print("✅ Math Tutor pipe created:", json.dumps(pipe, indent=2))


def run_math_tutor_pipe(langbase: Langbase, question: str):
    response = langbase.pipes.run(
        name="math-tutor",
        messages=[{"role": "user", "content": question}],
        stream=False,
    )

    # Parse and validate the response using Pydantic
    solution = MathReasoning.model_validate_json(response["completion"])

    print("✅ Structured Output Response:")
    print("=" * 50)

    for i, step in enumerate(solution.steps, 1):
        print(f"Step {i}:")
        print(f"  Explanation: {step.explanation}")
        print(f"  Output: {step.output}")
        print()

    print(f"Final Answer: {solution.final_answer}")
    print("=" * 50)


def main():
    load_dotenv()

    if not os.getenv("LANGBASE_API_KEY"):
        print("❌ Missing LANGBASE_API_KEY in environment variables.")
        exit(1)

    langbase = Langbase(api_key=os.getenv("LANGBASE_API_KEY"))

    # Run this only once to create the pipe. Uncomment if it's your first time setting it up.
    create_math_tutor_pipe(langbase)
    run_math_tutor_pipe(langbase, "How can I solve 8x + 22 = -23?")


if __name__ == "__main__":
    main()
