import json
import os

from dotenv import load_dotenv

from langbase import Langbase


def main():
    load_dotenv()

    # Get API key from environment variable
    langbase_api_key = os.getenv("LANGBASE_API_KEY")

    # Initialize the client
    lb = Langbase(api_key=langbase_api_key)
    # Test a basic operation (mock or use a real API key)
    try:
        # For testing purposes, you can use a mock or a real simple call
        # This would depend on your API, for example:
        response = lb.pipes.list()
        print(json.dumps(response, indent=2))

    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main()
