"""
Experimental upcoming beta AI primitive.
Please refer to the documentation for more information: https://langbase.com/docs for more information.
"""

import asyncio
import os

from dotenv import load_dotenv

from langbase import Langbase, Workflow

load_dotenv()


async def main():
    # Initialize Langbase client
    langbase = Langbase(api_key=os.environ.get("LANGBASE_API_KEY"))

    # Create workflow with debug mode
    workflow = Workflow(debug=True)

    # Define and execute a workflow step
    async def summarize_step():
        return langbase.agent.run(
            model="openai:gpt-4o-mini",
            api_key=os.environ.get("LLM_API_KEY"),
            input=[
                {
                    "role": "system",
                    "content": "You are an expert summarizer. Summarize the user input.",
                },
                {
                    "role": "user",
                    "content": "I am testing workflows. I just created an example of summarize workflow. Can you summarize this?",
                },
            ],
            stream=False,
        )

    result = await workflow.step({"id": "summarize", "run": summarize_step})

    print(result["output"])


if __name__ == "__main__":
    asyncio.run(main())
