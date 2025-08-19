"""
Example demonstrating how to run a pipe in non-streaming mode in Langbase.
"""

import json
import os

from dotenv import load_dotenv

from langbase import Langbase
from langbase.errors import APIError, AuthenticationError, NotFoundError, RateLimitError


def main():
    load_dotenv()

    # Get API key from environment variable
    langbase_api_key = os.getenv("LANGBASE_API_KEY")

    # Initialize the client
    lb = Langbase(api_key=langbase_api_key)

    # Run the pipe with explicit stream=False
    try:
        response = lb.pipes.run(
            name="summary-agent",
            messages=[{"role": "user", "content": "Who is an AI Engineer?"}],
            stream=False,
        )

        # Print the entire response as is
        print(json.dumps(response, indent=2))

    except AuthenticationError as e:
        print(f"Authentication Error: Check your API key - {e}")
    except NotFoundError as e:
        print(f"Not Found Error: Pipe doesn't exist - {e}")
    except RateLimitError as e:
        print(f"Rate Limit Error: Too many requests - {e}")
    except APIError as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
