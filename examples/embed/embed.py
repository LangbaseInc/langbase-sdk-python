# Experimental upcoming beta AI primitve.
# Please refer to the documentation for more information: https://langbase.com/docs for more information.
import json
import os

from dotenv import load_dotenv

from langbase import Langbase

load_dotenv()

# Cconfigure the Langbase client with your API key
langbase = Langbase(api_key=os.environ.get("LANGBASE_API_KEY"))


def main():
    """
    Generates embeddings for the given text chunks.
    """
    response = langbase.embed(
        chunks=[
            "Langbase is the most powerful serverless platform for building AI agents with memory. Build, scale, and evaluate AI agents with semantic memory (RAG) and world-class developer experience.",
            "We process billions of AI messages/tokens daily. Built for every developer, not just AI/ML experts.",
        ],
        embedding_model="openai:text-embedding-3-large",
    )
    print(json.dumps(response, indent=2))


if __name__ == "__main__":
    main()
