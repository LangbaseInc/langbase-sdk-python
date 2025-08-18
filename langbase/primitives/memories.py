"""
Memories API client for the Langbase SDK.
"""

import json
from io import BytesIO
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Union

import requests

from langbase.constants import (
    MEMORY_DETAIL_ENDPOINT,
    MEMORY_DOCUMENT_DETAIL_ENDPOINT,
    MEMORY_DOCUMENT_EMBEDDINGS_RETRY_ENDPOINT,
    MEMORY_DOCUMENTS_ENDPOINT,
    MEMORY_DOCUMENTS_UPLOAD_ENDPOINT,
    MEMORY_ENDPOINT,
    MEMORY_RETRIEVE_ENDPOINT,
)
from langbase.errors import APIError
from langbase.types import (
    ContentType,
    EmbeddingModel,
    MemoryCreateResponse,
    MemoryDeleteDocResponse,
    MemoryDeleteResponse,
    MemoryListDocResponse,
    MemoryListResponse,
    MemoryRetrieveResponse,
)
from langbase.utils import clean_null_values


class Documents:
    def __init__(self, parent):
        self.parent = parent
        self.request = parent.request
        self.embeddings = self.Embeddings(parent)

    def list(self, memory_name: str) -> List[MemoryListDocResponse]:
        """
        List all documents in a memory.

        Args:
            memory_name: Name of the memory

        Returns:
            List of document objects
        """
        return self.request.get(
            MEMORY_DOCUMENTS_ENDPOINT.format(memory_name=memory_name)
        )

    def delete(self, memory_name: str, document_name: str) -> MemoryDeleteDocResponse:
        """
        Delete a document from memory.

        Args:
            memory_name: Name of the memory
            document_name: Name of the document to delete

        Returns:
            Delete response
        """
        return self.request.delete(
            MEMORY_DOCUMENT_DETAIL_ENDPOINT.format(
                memory_name=memory_name, document_name=document_name
            )
        )

    def upload(
        self,
        memory_name: str,
        document_name: str,
        document: Union[bytes, BytesIO, str, BinaryIO],
        content_type: ContentType,
        meta: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """
        Upload a document to memory.

        Args:
            memory_name: Name of the memory
            document_name: Name for the document
            document: Document content (bytes, file-like object, or path)
            content_type: MIME type of the document
            meta: Metadata for the document

        Returns:
            Upload response
        """
        try:
            # Get signed URL for upload
            response = self.request.post(
                MEMORY_DOCUMENTS_UPLOAD_ENDPOINT,
                {
                    "memoryName": memory_name,
                    "fileName": document_name,
                    "meta": meta or {},
                },
            )

            upload_url = response.get("signedUrl")

            # Convert document to appropriate format
            if isinstance(document, str) and Path(document).is_file():
                with Path(document).open("rb") as f:
                    file_content = f.read()
            elif isinstance(document, bytes):
                file_content = document
            elif isinstance(document, BytesIO) or hasattr(document, "read"):
                file_content = document.read()
                # Reset file pointer if possible
                if hasattr(document, "seek"):
                    document.seek(0)
            else:
                msg = f"Unsupported document type: {type(document)}"
                raise ValueError(msg)

            # Upload to signed URL
            upload_response = requests.put(
                upload_url,
                headers={
                    "Authorization": f"Bearer {self.parent.parent.api_key}",
                    "Content-Type": content_type,
                },
                data=file_content,
            )

            if not upload_response.ok:
                # Use API error response directly
                raise APIError(
                    status_code=upload_response.status_code,
                    response_text=upload_response.text,
                    headers=dict(upload_response.headers),
                )

            return upload_response

        except Exception as e:
            if isinstance(e, APIError):
                raise e
            # Wrap other exceptions as APIError
            raise APIError(message=f"Document upload failed: {str(e)}") from e

    class Embeddings:
        def __init__(self, parent):
            self.parent = parent
            self.request = parent.request

        def retry(self, memory_name: str, document_name: str):
            """
            Retry embedding generation for a document.

            Args:
                memory_name: Name of the memory
                document_name: Name of the document

            Returns:
                Retry response
            """
            return self.request.get(
                MEMORY_DOCUMENT_EMBEDDINGS_RETRY_ENDPOINT.format(
                    memory_name=memory_name, document_name=document_name
                )
            )


class Memories:
    def __init__(self, parent):
        self.parent = parent
        self.request = parent.request
        self.documents = Documents(self)

    def create(
        self,
        name: str,
        description: Optional[str] = None,
        embedding_model: Optional[EmbeddingModel] = None,
        top_k: Optional[int] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> MemoryCreateResponse:
        """
        Create a new memory.

        Args:
            name: Name for the memory
            description: Description of the memory
            embedding_model: Model to use for embeddings
            top_k: Number of results to return
            chunk_size: Size of chunks for document processing
            chunk_overlap: Overlap between chunks

        Returns:
            Created memory object
        """
        options = {
            "name": name,
            "description": description,
            "embedding_model": embedding_model,
            "top_k": top_k,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
        }
        return self.request.post(MEMORY_ENDPOINT, clean_null_values(options))

    def delete(self, name: str) -> MemoryDeleteResponse:
        """
        Delete a memory.

        Args:
            name: Name of the memory to delete

        Returns:
            Delete response
        """
        return self.request.delete(MEMORY_DETAIL_ENDPOINT.format(name=name))

    def retrieve(
        self,
        query: str,
        memory: List[Dict[str, Any]],
        top_k: Optional[int] = None,
    ) -> List[MemoryRetrieveResponse]:
        """
        Retrieve content from memory based on query.

        Args:
            query: Search query
            memory: List of memory configurations
            top_k: Number of results to return

        Returns:
            List of matching content
        """
        options = {"query": query, "memory": memory}

        if top_k is not None:
            options["topK"] = top_k

        return self.request.post(MEMORY_RETRIEVE_ENDPOINT, options)

    def list(self) -> List[MemoryListResponse]:
        """
        List all memories.

        Returns:
            List of memory objects
        """
        return self.request.get(MEMORY_ENDPOINT)
