"""
Run Agent with Tool

This example demonstrates how to run an agent that can call a tool —
in this case, a function that sends an email using the Resend API.
"""

import json
import os

import requests
from dotenv import load_dotenv

from langbase import Langbase

load_dotenv()

# Define the tool schema for sending emails
send_email_tool_schema = {
    "type": "function",
    "function": {
        "name": "send_email",
        "description": "Send an email using Resend API",
        "parameters": {
            "type": "object",
            "required": ["from", "to", "subject", "html", "text"],
            "properties": {
                "from": {"type": "string"},
                "to": {"type": "string"},
                "subject": {"type": "string"},
                "html": {"type": "string"},
                "text": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
}


# Actual tool function
def send_email(args):
    """Send an email using the Resend API."""
    from_email = args.get("from")
    to_email = args.get("to")
    subject = args.get("subject")
    html = args.get("html")
    text = args.get("text")

    # response = requests.post(
    #     "https://api.resend.com/emails",
    #     headers={
    #         "Authorization": f"Bearer {os.environ.get('RESEND_API_KEY')}",
    #         "Content-Type": "application/json",
    #     },
    #     json={
    #         "from": from_email,
    #         "to": to_email,
    #         "subject": subject,
    #         "html": html,
    #         "text": text,
    #     },
    # )

    # if not response.ok:
    #     raise Exception("Failed to send email")

    return f"✅ Email sent successfully to {to_email}!"


def main():
    # Check for required environment variables
    langbase_api_key = os.environ.get("LANGBASE_API_KEY")
    llm_api_key = os.environ.get("LLM_API_KEY")
    # resend_api_key = os.environ.get("RESEND_API_KEY")

    if not langbase_api_key:
        print("❌ Missing LANGBASE_API_KEY in environment variables.")
        exit(1)

    if not llm_api_key:
        print("❌ Missing LLM_API_KEY in environment variables.")
        exit(1)

    # if not resend_api_key:
    #     print("❌ Missing RESEND_API_KEY in environment variables.")
    #     exit(1)

    # Initialize Langbase client
    langbase = Langbase(api_key=langbase_api_key)

    recipient_info = {"email": "sam@example.com"}

    email = {
        "subject": "Welcome to Langbase!",
        "html_email": "Hello Sam! Welcome to Langbase.",
        "full_email": "Hello Sam! Welcome to Langbase.",
    }

    input_messages = [{"role": "user", "content": "Send a welcome email to Sam."}]

    # Initial run with tool
    response = langbase.agent.run(
        model="openai:gpt-4.1-mini",
        api_key=llm_api_key,
        instructions="You are an email agent. You are given a task to send an email to a recipient. You have the ability to send an email using the send_email tool.",
        input=input_messages,
        tools=[send_email_tool_schema],
        stream=False,
    )

    # Check if response contains choices (for tool calls)
    choices = response.get("choices", [])

    print("\n📨 Initial Response:")
    print(
        f"Output: {response.get('output', 'No direct output - checking for tool calls...')}"
    )

    if not choices:
        print("❌ No choices found in response")
        return

    # Push agent tool call to messages
    input_messages.append(choices[0].get("message", {}))

    # Detect tool call
    tool_calls = choices[0].get("message", {}).get("tool_calls", [])
    has_tool_calls = tool_calls and len(tool_calls) > 0

    if has_tool_calls:
        print(f"\n🔧 Tool calls detected: {len(tool_calls)}")

        for i, tool_call in enumerate(tool_calls, 1):
            # Process each tool call
            function = tool_call.get("function", {})
            name = function.get("name")
            args = function.get("arguments")

            print(f"\n  Tool Call #{i}:")
            print(f"  - Name: {name}")
            print(f"  - Raw Arguments: {args}")

            try:
                parsed_args = json.loads(args)
                print(f"  - Parsed Arguments: {json.dumps(parsed_args, indent=4)}")
            except json.JSONDecodeError:
                print(f"  ❌ Error parsing tool call arguments: {args}")
                continue

            # Set email parameters
            print("\n  📧 Preparing email with full details...")
            parsed_args["from"] = "onboarding@resend.dev"
            parsed_args["to"] = recipient_info["email"]
            parsed_args["subject"] = email["subject"]
            parsed_args["html"] = email["html_email"]
            parsed_args["text"] = email["full_email"]

            print(f"  - From: {parsed_args['from']}")
            print(f"  - To: {parsed_args['to']}")
            print(f"  - Subject: {parsed_args['subject']}")

            # Execute the tool
            try:
                print(f"\n  ⚡ Executing {name}...")
                result = send_email(parsed_args)
                print(f"  ✅ Tool result: {result}")

                # Add tool result to messages
                input_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.get("id"),
                        "name": name,
                        "content": result,
                    }
                )
            except Exception as e:
                print(f"  ❌ Error executing tool: {e}")
                continue

    print("\n🤖 Sending tool results back to agent for final response...")

    # Final agent response with tool result
    final_response = langbase.agent.run(
        model="openai:gpt-4.1-mini",
        api_key=llm_api_key,
        instructions="You are an email sending assistant. Confirm the email has been sent successfully.",
        input=input_messages,
        stream=False,
    )

    print("\n✨ Final Response:")
    print(f"Agent: {final_response.get('output')}")
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
