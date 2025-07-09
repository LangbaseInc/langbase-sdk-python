"""
Summarization Workflow

This example demonstrates how to create a workflow that summarizes text input
with parallel processing and retry configuration.
"""

import asyncio
import json
import os

from dotenv import load_dotenv

from langbase import Langbase, Workflow

load_dotenv()


async def process_text(input_text: str):
    """
    Process text input by summarizing it with retry logic and debug mode.

    Args:
        input_text: The text to be summarized

    Returns:
        Dictionary containing the response
    """
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

    # Initialize Langbase
    langbase = Langbase(api_key=langbase_api_key)

    # Create workflow with debug mode
    workflow = Workflow(debug=True)

    try:
        # Define a single step with retries
        async def process_text_step():
            response = langbase.agent_run(
                model="openai:gpt-4o",
                instructions="""Summarize the following text in a 
                single paragraph. Be concise but capture the key information.""",
                api_key=llm_api_key,
                input=[{"role": "user", "content": input_text}],
                stream=False,
            )
            return response.get("output")

        response = await workflow.step(
            {
                "id": "process_text",
                "retries": {"limit": 2, "delay": 1000, "backoff": "exponential"},
                "run": process_text_step,
            }
        )

        # Return the result
        return {"response": response}

    except Exception as error:
        print(f"Workflow step failed: {error}")
        raise error


async def main():
    sample_text = """
    Langbase is the most powerful serverless AI platform for building AI agents with memory.
    Build, deploy, and scale AI agents with tools and memory (RAG). Simple AI primitives 
    with a world-class developer experience without using any frameworks.
    
    Compared to complex AI frameworks, Langbase is serverless and the first composable 
    AI platform. Build AI agents without any bloated frameworks. You write the logic, 
    we handle the logistics.
    
    Langbase offers AI Pipes (serverless agents with tools), AI Memory (serverless RAG), 
    and AI Studio (developer platform). The platform is 30-50x less expensive than 
    competitors, supports 250+ LLM models, and enables collaboration among team members.
    """

    results = await process_text(sample_text)
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
