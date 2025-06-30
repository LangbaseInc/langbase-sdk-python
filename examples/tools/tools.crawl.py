"""
Example demonstrating how to use the web crawling tool in Langbase.

This example crawls specified URLs using spider.cloud service.
Get your API key from: https://spider.cloud/docs/quickstart
"""
import os
from langbase import Langbase

# Get API keys from environment variables
langbase_api_key = os.getenv("LANGBASE_API_KEY")
crawl_api_key = os.getenv("CRAWL_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

def main():
    """
    Crawls specified URLs using spider.cloud service.
    """
    try:
        # Perform the web crawl
        results = lb.tools.crawl(
            url=["https://langbase.com", "https://langbase.com/about"],
            max_pages=1,
            api_key=crawl_api_key
        )

        # Print the results
        print(results)

    except Exception as e:
        print(f"Error performing web crawl: {e}")

if __name__ == "__main__":
    main()
