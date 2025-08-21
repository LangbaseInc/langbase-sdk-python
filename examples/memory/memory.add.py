"""
Example: Add text directly to memory

1. Run memory.create.py first to create a memory.
2. Add your API key to the environment variables or replace it in the code.
"""

import os

from langbase import Langbase

# Initialize the Langbase client
langbase = Langbase(api_key=os.getenv("LANGBASE_API_KEY"))


def main():
    try:
        # Basic text addition
        print("📝 Adding basic text to memory...")
        basic_result = langbase.memories.add(
            memory_name="my-knowledge-base",
            text="This is important information about machine learning fundamentals. "
            "It covers supervised learning, unsupervised learning, and reinforcement learning concepts.",
        )
        print(f"✅ Basic text added: {basic_result['document_name']}")

        # Text addition with custom name and metadata
        print("\n📝 Adding detailed text with metadata...")
        detailed_result = langbase.memories.add(
            memory_name="my-knowledge-base",
            text="Deep learning is a subset of machine learning that uses artificial neural networks "
            "with multiple layers to model and understand complex patterns in data. It has "
            "revolutionized fields like computer vision, natural language processing, and speech recognition.",
            document_name="deep-learning-intro",
            metadata={
                "category": "machine-learning",
                "topic": "deep-learning",
                "difficulty": "intermediate",
                "source": "manual-entry",
            },
        )
        print(f"✅ Detailed text added: {detailed_result['document_name']}")

        # Multiple text entries
        texts = [
            {
                "text": "Supervised learning uses labeled training data to learn a mapping from inputs to outputs.",
                "document_name": "supervised-learning",
                "metadata": {"type": "definition", "category": "ml-concepts"},
            },
            {
                "text": "Unsupervised learning finds hidden patterns in data without using labeled examples.",
                "document_name": "unsupervised-learning",
                "metadata": {"type": "definition", "category": "ml-concepts"},
            },
            {
                "text": "Reinforcement learning learns optimal actions through trial and error interactions with an environment.",
                "document_name": "reinforcement-learning",
                "metadata": {"type": "definition", "category": "ml-concepts"},
            },
        ]

        print("\n📝 Adding multiple texts...")
        for item in texts:
            result = langbase.memories.add(memory_name="my-knowledge-base", **item)
            print(f"✅ Added: {result['document_name']}")

        print("\n🎉 All texts have been added to the memory!")
        print("You can now query this memory to retrieve relevant information.")

    except Exception as error:
        print(f"❌ Error: {error}")


if __name__ == "__main__":
    main()
