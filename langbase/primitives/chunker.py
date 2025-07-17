"""
Chunker API client for the Langbase SDK.
"""

from typing import Optional

from langbase.constants import CHUNKER_ENDPOINT
from langbase.request import Request
from langbase.types import ChunkResponse


class Chunker:
    """
    Client for text chunking operations.

    This class provides methods for splitting text content into chunks.
    """

    def __init__(self, parent):
        """
        Initialize the Chunker client.

        Args:
            parent: The parent Langbase instance
        """
        self.parent = parent
        self.request: Request = parent.request

    def chunker(
        self,
        content: str,
        chunk_max_length: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> ChunkResponse:
        """
        Split content into chunks.

        Args:
            content: The text content to be chunked
            chunk_max_length: Maximum length for each chunk (1024-30000, default: 1024)
            chunk_overlap: Number of characters to overlap between chunks (>=256, default: 256)

        Returns:
            List of text chunks

        Raises:
            APIError: If chunking fails
        """
        json_data = {"content": content}

        if chunk_max_length is not None:
            json_data["chunkMaxLength"] = chunk_max_length

        if chunk_overlap is not None:
            json_data["chunkOverlap"] = chunk_overlap

        return self.request.post(CHUNKER_ENDPOINT, json_data)
