"""
Email Processing Workflow

This example demonstrates how to create a workflow that analyzes an email
and generates a response when needed.
"""

import asyncio
import json
import os

from dotenv import load_dotenv

from langbase import Langbase, Workflow

load_dotenv()


async def process_email(email_content: str):
    """
    Process an email by summarizing, analyzing sentiment, determining if response
    is needed, and generating a response if necessary.

    Args:
        email_content: The content of the email to process

    Returns:
        Dictionary containing summary, sentiment, response_needed, and response
    """
    # Check for required environment variables
    langbase_api_key = os.environ.get("LANGBASE_API_KEY")
    llm_api_key = os.environ.get("LLM_API_KEY")

    if not langbase_api_key:
        print("❌ Missing LANGBASE_API_KEY in environment variables.")
        print("Please set: LANGBASE_API_KEY='your_langbase_api_key' in .env file")
        exit(1)

    if not llm_api_key:
        print("❌ Missing LLM_API_KEY in environment variables.")
        print("Please set: LLM_API_KEY='your_llm_api_key' in .env file")
        exit(1)

    # Initialize Langbase
    langbase = Langbase(api_key=langbase_api_key)

    # Create a new workflow
    workflow = Workflow(debug=True)

    try:
        # Steps 1 & 2: Run summary and sentiment analysis in parallel
        async def summarize_email():
            response = langbase.agent.run(
                model="openai:gpt-4.1-mini",
                instructions="""Create a concise summary of this email. Focus on the main points,
                requests, and any action items mentioned.""",
                api_key=llm_api_key,
                input=[{"role": "user", "content": email_content}],
                stream=False,
            )
            return response.get("output")

        async def analyze_sentiment():
            response = langbase.agent.run(
                model="openai:gpt-4.1-mini",
                instructions="""Analyze the sentiment of this email. Provide a brief analysis
                that includes the overall tone (positive, neutral, or negative) and any notable
                emotional elements.""",
                api_key=llm_api_key,
                input=[{"role": "user", "content": email_content}],
                stream=False,
            )
            return response.get("output")

        # Execute summary and sentiment analysis steps in parallel
        summary = await workflow.step({"id": "summarize_email", "run": summarize_email})

        sentiment = await workflow.step(
            {"id": "analyze_sentiment", "run": analyze_sentiment}
        )

        # Step 3: Determine if response is needed (using the results from previous steps)
        async def determine_response_needed():
            response = langbase.agent.run(
                model="openai:gpt-4.1-mini",
                instructions="""Based on the email summary and sentiment analysis, determine if a
                response is needed. Answer with 'yes' if a response is required, or 'no' if no
                response is needed. Consider factors like: Does the email contain a question?
                Is there an explicit request? Is it urgent?""",
                api_key=llm_api_key,
                input=[
                    {
                        "role": "user",
                        "content": f"""Email: {email_content}

Summary: {summary}

Sentiment: {sentiment}

Does this email require a response?""",
                    }
                ],
                stream=False,
            )
            return "yes" in response.get("output", "").lower()

        response_needed = await workflow.step(
            {"id": "determine_response_needed", "run": determine_response_needed}
        )

        # Step 4: Generate response if needed
        response = None
        if response_needed:

            async def generate_response():
                response = langbase.agent.run(
                    model="openai:gpt-4.1-mini",
                    instructions="""Generate a professional email response. Address all questions
                    and requests from the original email. Be helpful, clear, and maintain a
                    professional tone that matches the original email sentiment.""",
                    api_key=llm_api_key,
                    input=[
                        {
                            "role": "user",
                            "content": f"""Original Email: {email_content}

Summary: {summary}

Sentiment Analysis: {sentiment}

Please draft a response email.""",
                        }
                    ],
                    stream=False,
                )
                return response.get("output")

            response = await workflow.step(
                {"id": "generate_response", "run": generate_response}
            )

        # Return the results
        return {
            "summary": summary,
            "sentiment": sentiment,
            "response_needed": response_needed,
            "response": response,
        }

    except Exception as error:
        print(f"Email processing workflow failed: {error}")
        raise error


async def main():
    sample_email = """
Subject: Pricing Information and Demo Request

Hello,

I came across your platform and I'm interested in learning more about your product
for our growing company. Could you please send me some information on your pricing tiers?

We're particularly interested in the enterprise tier as we now have a team of about
50 people who would need access. Would it be possible to schedule a demo sometime next week?

Thanks in advance for your help!

Best regards,
Jamie
"""

    results = await process_email(sample_email)
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
