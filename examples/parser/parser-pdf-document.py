import json
import os
import pathlib

from dotenv import load_dotenv

from langbase import Langbase

load_dotenv()

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
langbase = Langbase(api_key=langbase_api_key)


def main():
    try:
        # Get the path to the PDF document
        document_path = pathlib.Path(__file__).parent / "document.pdf"

        # Read the file
        with open(document_path, "rb") as file:
            document_content = file.read()

        # Parse the document
        results = langbase.parser(
            document=document_content,
            document_name="document.pdf",
            content_type="application/pdf",
        )

        # Print the results
        print(json.dumps(results, indent=2))

    except Exception as e:
        print(f"Error parsing document: {e}")


if __name__ == "__main__":
    main()
