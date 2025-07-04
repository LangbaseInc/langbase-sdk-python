"""
Example demonstrating how to parse a document using Langbase.
"""
import os
import pathlib
import json
from langbase import Langbase
from dotenv import load_dotenv

load_dotenv()

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

def main():
    """
    Parses a document using Langbase.
    """
    try:
        # Get the path to the document
        document_path = pathlib.Path(__file__).parent / "composable-ai.md"

        # Read the file
        with open(document_path, "rb") as file:
            document_content = file.read()

        # Parse the document
        results = lb.parser(
            document=document_content,
            document_name="composable-ai.md",
            content_type="text/markdown"
        )

        # Print the results
        print(json.dumps(results, indent=2))

    except Exception as e:
        print(f"Error parsing document: {e}")

if __name__ == "__main__":
    main()
