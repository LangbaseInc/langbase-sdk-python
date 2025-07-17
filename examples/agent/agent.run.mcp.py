"""
Run Agent with MCP

This example demonstrates how to run an agent with MCP (Model Context Protocol).
"""

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

    # Run the agent with MCP server
    response = langbase.agent.run(
        stream=False,
        model="openai:gpt-4.1-mini",
        api_key=llm_api_key,
        instructions="You are a helpful assistant that help users summarize text.",
        input=[
            {
                "role": "user",
                "content": "What transport protocols does the 2025-03-26 version of the MCP spec (modelcontextprotocol/modelcontextprotocol) support?",
            }
        ],
        mcp_servers=[
            {"type": "url", "name": "deepwiki", "url": "https://mcp.deepwiki.com/sse"}
        ],
    )

    print("response:", response.get("output"))


if __name__ == "__main__":
    main()
