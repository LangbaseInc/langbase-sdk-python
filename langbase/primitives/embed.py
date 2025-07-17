"""
Embed API client for the Langbase SDK.
"""

from typing import List, Optional

from langbase.constants import EMBED_ENDPOINT
from langbase.request import Request
from langbase.types import EmbeddingModel, EmbedResponse


class Embed:
    """
    Client for embedding operations.

    This class provides methods for generating embeddings for text chunks.
    """

    def __init__(self, parent):
        """
        Initialize the Embed client.

        Args:
            parent: The parent Langbase instance
        """
        self.parent = parent
        self.request: Request = parent.request

    def embed(
        self, chunks: List[str], embedding_model: Optional[EmbeddingModel] = None
    ) -> EmbedResponse:
        """
        Generate embeddings for text chunks.

        Args:
            chunks: List of text chunks to embed
            embedding_model: Model to use for embeddings

        Returns:
            List of embedding vectors
        """

        options = {"chunks": chunks}

        if embedding_model:
            options["embeddingModel"] = embedding_model

        return self.request.post(EMBED_ENDPOINT, options)
