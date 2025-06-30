"""
Main client for the Langbase SDK.

This module provides the Langbase class which is the main entry point
for interacting with the Langbase API.
"""
import os
from typing import Dict, List, Optional, Union, Any, BinaryIO, overload
from io import BytesIO
import requests

from .errors import APIError
from .request import Request
from .utils import convert_document_to_request_files, clean_null_values
from .types import (
    EmbeddingModel, ContentType, FileProtocol,
    MemoryRetrieveResponse, MemoryListDocResponse, MemoryCreateResponse,
    MemoryListResponse, MemoryDeleteResponse, MemoryDeleteDocResponse,
    ThreadsBaseResponse, ThreadMessagesBaseResponse
)


class Langbase:
    """
    Client for the Langbase API.

    This class provides methods for interacting with all aspects of the Langbase API,
    including pipes, memories, tools, threads, and utilities.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.langbase.com",
        timeout: int = 30
    ):
        """
        Initialize the Langbase client.

        Args:
            api_key: The API key for authentication. If not provided, it will be read
                    from the LANGBASE_API_KEY environment variable.
            base_url: The base URL for the API.
            timeout: The timeout for API requests in seconds.

        Raises:
            ValueError: If no API key is provided and LANGBASE_API_KEY is not set.
        """
        self.api_key = api_key or os.environ.get("LANGBASE_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "API key must be provided either as a parameter or through the LANGBASE_API_KEY environment variable"
            )

        self.base_url = base_url
        self.timeout = timeout

        self.request = Request({
            "api_key": self.api_key,
            "base_url": self.base_url,
            "timeout": self.timeout
        })

        # Initialize properties and methods
        self._init_pipes()
        self._init_memories()
        self._init_tools()
        self._init_threads()
        self._init_llm()

        # Deprecated property aliases
        self.pipe = self.pipes
        self.memory = self.memories
        self.tool = self.tools

    def _init_pipes(self):
        """Initialize pipes methods."""

        class Pipes:
            def __init__(self, parent):
                self.parent = parent

            def list(self):
                """
                List all pipes.

                Returns:
                    List of pipe objects
                """
                return self.parent.request.get("/v1/pipes")

            def create(self, name: str, description: Optional[str] = None, **kwargs):
                """
                Create a new pipe.

                Args:
                    name: Name of the pipe
                    description: Description of the pipe
                    **kwargs: Additional parameters for the pipe

                Returns:
                    Created pipe object
                """
                options = {
                    "name": name,
                    "description": description,
                    **kwargs
                }
                return self.parent.request.post("/v1/pipes", clean_null_values(options))

            def update(self, name: str, **kwargs):
                """
                Update an existing pipe.

                Args:
                    name: Name of the pipe to update
                    **kwargs: Parameters to update

                Returns:
                    Updated pipe object
                """
                options = {
                    "name": name,
                    **kwargs
                }
                return self.parent.request.post(f"/v1/pipes/{name}", clean_null_values(options))

            def run(
                self,
                name: Optional[str] = None,
                api_key: Optional[str] = None,
                messages: Optional[List[Dict[str, Any]]] = None,
                stream: Optional[bool] = None,  # Changed to Optional[bool] with default None
                **kwargs
            ):
                """
                Run a pipe.

                Args:
                    name: Name of the pipe to run
                    api_key: API key for the pipe
                    messages: List of messages for the conversation
                    stream: Whether to stream the response (None means don't specify)
                    **kwargs: Additional parameters for the run

                Returns:
                    Run response or stream

                Raises:
                    ValueError: If neither name nor API key is provided
                """
                if not name and not api_key:
                    raise ValueError("Either pipe name or API key is required")

                options = {
                    "name": name,
                    "api_key": api_key,
                    "messages": messages or [],
                    **kwargs
                }

                # Only set stream in options if it's explicitly provided
                if stream is not None:
                    options["stream"] = stream

                # Create a new request instance if API key is provided
                request = self.parent.request
                if api_key:
                    request = Request({
                        "api_key": api_key,
                        "base_url": self.parent.base_url,
                        "timeout": self.parent.timeout
                    })

                headers = {}
                if "llm_key" in kwargs:
                    headers["LB-LLM-KEY"] = kwargs.pop("llm_key")

                # Pass the stream parameter to post method (which might be None)
                return request.post("/v1/pipes/run", clean_null_values(options), headers, stream=stream if stream is not None else False)

        self.pipes = Pipes(self)

    def _init_memories(self):
        """Initialize memories methods."""

        class Documents:
            def __init__(self, parent):
                self.parent = parent

            def list(self, memory_name: str) -> List[MemoryListDocResponse]:
                """
                List all documents in a memory.

                Args:
                    memory_name: Name of the memory

                Returns:
                    List of document objects
                """
                return self.parent.request.get(f"/v1/memory/{memory_name}/documents")

            def delete(self, memory_name: str, document_name: str) -> MemoryDeleteDocResponse:
                """
                Delete a document from memory.

                Args:
                    memory_name: Name of the memory
                    document_name: Name of the document to delete

                Returns:
                    Delete response
                """
                return self.parent.request.delete(
                    f"/v1/memory/{memory_name}/documents/{document_name}"
                )

            def upload(
                self,
                memory_name: str,
                document_name: str,
                document: Union[bytes, BytesIO, str, BinaryIO],
                content_type: ContentType,
                meta: Optional[Dict[str, str]] = None
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

                Raises:
                    ValueError: If document type is unsupported
                    APIError: If the upload fails
                """
                try:
                    # Get signed URL for upload
                    response = self.parent.request.post("/v1/memory/documents", {
                        "memoryName": memory_name,
                        "fileName": document_name,
                        "meta": meta or {}
                    })

                    upload_url = response.get("signedUrl")

                    # Convert document to appropriate format
                    if isinstance(document, str) and os.path.isfile(document):
                        with open(document, "rb") as f:
                            file_content = f.read()
                    elif isinstance(document, bytes):
                        file_content = document
                    elif isinstance(document, BytesIO) or hasattr(document, 'read'):
                        file_content = document.read()
                        # Reset file pointer if possible
                        if hasattr(document, 'seek'):
                            document.seek(0)
                    else:
                        raise ValueError(f"Unsupported document type: {type(document)}")

                    # Upload to signed URL
                    upload_response = requests.put(
                        upload_url,
                        headers={
                            "Authorization": f"Bearer {self.parent.api_key}",
                            "Content-Type": content_type
                        },
                        data=file_content
                    )

                    if not upload_response.ok:
                        raise APIError(
                            upload_response.status_code,
                            upload_response.text,
                            "Upload failed",
                            dict(upload_response.headers)
                        )

                    return upload_response

                except Exception as e:
                    if isinstance(e, APIError):
                        raise e
                    raise APIError(
                        None,
                        str(e),
                        "Error during document upload",
                        None
                    ) from e

            class Embeddings:
                def __init__(self, parent):
                    self.parent = parent

                def retry(self, memory_name: str, document_name: str):
                    """
                    Retry embedding generation for a document.

                    Args:
                        memory_name: Name of the memory
                        document_name: Name of the document

                    Returns:
                        Retry response
                    """
                    return self.parent.request.get(
                        f"/v1/memory/{memory_name}/documents/{document_name}/embeddings/retry"
                    )

            def __init__(self, parent):
                self.parent = parent
                self.embeddings = self.Embeddings(parent)

        class Memories:
            def __init__(self, parent):
                self.parent = parent
                self.documents = Documents(parent)

            def create(
                self,
                name: str,
                description: Optional[str] = None,
                embedding_model: Optional[EmbeddingModel] = None
            ) -> MemoryCreateResponse:
                """
                Create a new memory.

                Args:
                    name: Name for the memory
                    description: Description of the memory
                    embedding_model: Model to use for embeddings

                Returns:
                    Created memory object
                """
                options = {
                    "name": name,
                    "description": description,
                    "embedding_model": embedding_model
                }
                return self.parent.request.post("/v1/memory", clean_null_values(options))

            def delete(self, name: str) -> MemoryDeleteResponse:
                """
                Delete a memory.

                Args:
                    name: Name of the memory to delete

                Returns:
                    Delete response
                """
                return self.parent.request.delete(f"/v1/memory/{name}")

            def retrieve(
                self,
                query: str,
                memory: List[Dict[str, Any]],
                top_k: Optional[int] = None
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
                options = {
                    "query": query,
                    "memory": memory
                }

                if top_k is not None:
                    options["topK"] = top_k

                return self.parent.request.post("/v1/memory/retrieve", options)

            def list(self) -> List[MemoryListResponse]:
                """
                List all memories.

                Returns:
                    List of memory objects
                """
                return self.parent.request.get("/v1/memory")

        self.memories = Memories(self)

    def _init_tools(self):
        """Initialize tools methods."""

        class Tools:
            def __init__(self, parent):
                self.parent = parent

            def crawl(
                self,
                url: List[str],
                max_pages: Optional[int] = None,
                api_key: Optional[str] = None
            ):
                """
                Crawl web pages.

                Args:
                    url: List of URLs to crawl
                    max_pages: Maximum number of pages to crawl
                    api_key: API key for crawling service

                Returns:
                    List of crawled content
                """
                options = {"url": url}

                if max_pages is not None:
                    options["maxPages"] = max_pages

                headers = {}
                if api_key:
                    headers["LB-CRAWL-KEY"] = api_key

                return self.parent.request.post("/v1/tools/crawl", options, headers)

            def web_search(
                self,
                query: str,
                service: str = "exa",
                total_results: Optional[int] = None,
                domains: Optional[List[str]] = None,
                api_key: Optional[str] = None
            ):
                """
                Search the web.

                Args:
                    query: Search query
                    service: Search service to use
                    total_results: Number of results to return
                    domains: List of domains to restrict search to
                    api_key: API key for search service

                Returns:
                    List of search results
                """
                options = {
                    "query": query,
                    "service": service
                }

                if total_results is not None:
                    options["totalResults"] = total_results

                if domains is not None:
                    options["domains"] = domains

                headers = {}
                if api_key:
                    headers["LB-WEB-SEARCH-KEY"] = api_key

                return self.parent.request.post("/v1/tools/web-search", options, headers)

        self.tools = Tools(self)

    def _init_threads(self):
        """Initialize threads methods."""

        class Messages:
            def __init__(self, parent):
                self.parent = parent

            def list(self, thread_id: str) -> List[ThreadMessagesBaseResponse]:
                """
                List all messages in a thread.

                Args:
                    thread_id: ID of the thread

                Returns:
                    List of messages
                """
                return self.parent.request.get(f"/v1/threads/{thread_id}/messages")

        class Threads:
            def __init__(self, parent):
                self.parent = parent
                self.messages = Messages(parent)

            def create(
                self,
                thread_id: Optional[str] = None,
                metadata: Optional[Dict[str, str]] = None,
                messages: Optional[List[Dict[str, Any]]] = None
            ) -> ThreadsBaseResponse:
                """
                Create a new thread.

                Args:
                    thread_id: Optional specific ID for the thread
                    metadata: Metadata for the thread
                    messages: Initial messages for the thread

                Returns:
                    Created thread object
                """
                options = {}

                if thread_id:
                    options["threadId"] = thread_id

                if metadata:
                    options["metadata"] = metadata

                if messages:
                    options["messages"] = messages

                return self.parent.request.post("/v1/threads", clean_null_values(options))

            def update(
                self,
                thread_id: str,
                metadata: Dict[str, str]
            ) -> ThreadsBaseResponse:
                """
                Update thread metadata.

                Args:
                    thread_id: ID of the thread to update
                    metadata: New metadata

                Returns:
                    Updated thread object
                """
                options = {
                    "threadId": thread_id,
                    "metadata": metadata
                }
                return self.parent.request.post(f"/v1/threads/{thread_id}", options)

            def get(self, thread_id: str) -> ThreadsBaseResponse:
                """
                Get thread details.

                Args:
                    thread_id: ID of the thread

                Returns:
                    Thread object
                """
                return self.parent.request.get(f"/v1/threads/{thread_id}")

            def delete(self, thread_id: str) -> Dict[str, bool]:
                """
                Delete a thread.

                Args:
                    thread_id: ID of the thread to delete

                Returns:
                    Delete response
                """
                return self.parent.request.delete(f"/v1/threads/{thread_id}")

            def append(
                self,
                thread_id: str,
                messages: List[Dict[str, Any]]
            ) -> List[ThreadMessagesBaseResponse]:
                """
                Append messages to a thread.

                Args:
                    thread_id: ID of the thread
                    messages: Messages to append

                Returns:
                    List of added messages
                """
                return self.parent.request.post(
                    f"/v1/threads/{thread_id}/messages",
                    messages
                )

        self.threads = Threads(self)

    def _init_llm(self):
        """Initialize LLM methods."""

        class LLM:
            def __init__(self, parent):
                self.parent = parent

            def run(
                self,
                messages: List[Dict[str, Any]],
                model: str,
                llm_key: str,
                stream: bool = False,
                **kwargs
            ):
                """
                Run an LLM with the specified parameters.

                Args:
                    messages: List of messages
                    model: Model identifier
                    llm_key: API key for the LLM provider
                    stream: Whether to stream the response
                    **kwargs: Additional parameters for the model

                Returns:
                    LLM response or stream
                """
                options = {
                    "messages": messages,
                    "model": model,
                    "llm_key": llm_key,
                    **kwargs
                }

                if stream:
                    options["stream"] = True

                headers = {"LB-LLM-Key": llm_key}

                return self.parent.request.post("/v1/llm/run", options, headers, stream=stream)

        self.llm = LLM(self)

    def embed(
        self,
        chunks: List[str],
        embedding_model: Optional[EmbeddingModel] = None
    ) -> List[List[float]]:
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

        return self.request.post("/v1/embed", options)

    def chunk(
        self,
        document: Union[bytes, BytesIO, str, BinaryIO],
        document_name: str,
        content_type: ContentType,
        chunk_max_length: Optional[str] = None,
        chunk_overlap: Optional[str] = None,
        separator: Optional[str] = None
    ) -> List[str]:
        """
        Split a document into chunks.

        Args:
            document: Document content (bytes, file-like object, or path)
            document_name: Name for the document
            content_type: MIME type of the document
            chunk_max_length: Maximum length of each chunk
            chunk_overlap: Number of characters to overlap between chunks
            separator: Custom separator for chunking

        Returns:
            List of text chunks

        Raises:
            ValueError: If document type is unsupported
            APIError: If chunking fails
        """
        files = convert_document_to_request_files(document, document_name, content_type)

        if chunk_max_length:
            files["chunkMaxLength"] = (None, chunk_max_length)

        if chunk_overlap:
            files["chunkOverlap"] = (None, chunk_overlap)

        if separator:
            files["separator"] = (None, separator)

        response = requests.post(
            f"{self.base_url}/v1/chunk",
            headers={"Authorization": f"Bearer {self.api_key}"},
            files=files
        )

        if response.ok:
            return response.json()
        else:
            try:
                error_body = response.json()
            except:
                error_body = response.text

            raise APIError.generate(
                response.status_code,
                error_body,
                response.reason,
                dict(response.headers)
            )

    def parse(
        self,
        document: Union[bytes, BytesIO, str, BinaryIO],
        document_name: str,
        content_type: ContentType
    ) -> Dict[str, str]:
        """
        Parse a document to extract its content.

        Args:
            document: Document content (bytes, file-like object, or path)
            document_name: Name for the document
            content_type: MIME type of the document

        Returns:
            Dictionary with document name and extracted content

        Raises:
            ValueError: If document type is unsupported
            APIError: If parsing fails
        """
        files = convert_document_to_request_files(document, document_name, content_type)

        response = requests.post(
            f"{self.base_url}/v1/parse",
            headers={"Authorization": f"Bearer {self.api_key}"},
            files=files
        )

        if response.ok:
            return response.json()
        else:
            try:
                error_body = response.json()
            except:
                error_body = response.text

            raise APIError.generate(
                response.status_code,
                error_body,
                response.reason,
                dict(response.headers)
            )
