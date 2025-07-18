"""
Run Agent with Memory

This example demonstrates how to retrieve and attach memory to an agent call.
"""

import os
from io import BytesIO

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

    create_memory()

    # Step 1: Retrieve memory
    memory_response = langbase.memories.retrieve(
        memory=[{"name": "career-advisor-memory"}],
        query="Who is an AI Engineer?",
        top_k=2,
    )

    # Step 2: Run the agent with the retrieved memory
    response = langbase.agent.run(
        model="openai:gpt-4.1",
        api_key=llm_api_key,
        instructions="You are a career advisor who helps users understand AI job roles.",
        input=[
            {
                "role": "user",
                "content": f"{memory_response}\n\nNow, based on the above, who is an AI Engineer?",
            }
        ],
    )

    # Step 3: Display output
    print("Agent Response:", response.get("output"))


def create_memory():
    langbase_api_key = os.environ.get("LANGBASE_API_KEY")
    langbase = Langbase(api_key=langbase_api_key)

    memories = langbase.memories.list()
    memory_names = [memory["name"] for memory in memories]
    career_advisor_memory_name = "career-advisor-memory"

    if career_advisor_memory_name not in memory_names:
        memory = langbase.memories.create(
            name="career-advisor-memory",
            description="A memory for the career advisor agent",
        )

        print("Memory created: ", memory)

    content = """
    An AI Engineer is a software engineer who specializes in building AI systems.
    """

    content_buffer = BytesIO(content.encode("utf-8"))

    langbase.memories.documents.upload(
        memory_name="career-advisor-memory",
        document_name="career-advisor-document.txt",
        document=content_buffer,
        content_type="text/plain",
    )

    print("Document uploaded")


if __name__ == "__main__":
    main()
