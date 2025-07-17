"""
Main client for the Langbase SDK.

This module provides the Langbase class which is the main entry point
for interacting with the Langbase API.
"""

from typing import Optional

from .primitives.agent import Agent
from .primitives.chunker import Chunker
from .primitives.embed import Embed
from .primitives.memories import Memories
from .primitives.parser import Parser
from .primitives.pipes import Pipes
from .primitives.threads import Threads
from .primitives.tools import Tools
from .request import Request


class Langbase:
    """
    Client for the Langbase API.

    This class provides methods for interacting with all aspects of the Langbase API,
    including pipes, memories, tools, threads, and utilities.
    """

    def __init__(self, api_key: str = "", base_url: str = "https://api.langbase.com"):
        """
        Initialize the Langbase client.

        Args:
            api_key: The API key for authentication.
            base_url: The base URL for the API.
        """
        self.base_url = base_url
        self.api_key = api_key

        self.request = Request({"api_key": self.api_key, "base_url": self.base_url})

        # Initialize primitive classes
        self.agent = Agent(self)
        self.chunker_client = Chunker(self)
        self.embed_client = Embed(self)
        self.memories = Memories(self)
        self.parser_client = Parser(self)
        self.pipes = Pipes(self)
        self.threads = Threads(self)
        self.tools = Tools(self)

    def embed(self, chunks, embedding_model=None):
        """Generate embeddings for text chunks."""
        return self.embed_client.embed(chunks, embedding_model)

    def chunker(self, content, chunk_max_length=None, chunk_overlap=None):
        """Split content into chunks."""
        return self.chunker_client.chunker(content, chunk_max_length, chunk_overlap)

    def parser(self, document, document_name, content_type):
        """Parse a document to extract its content."""
        return self.parser_client.parser(document, document_name, content_type)
