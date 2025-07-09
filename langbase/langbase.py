"""
Main client for the Langbase SDK.

This module provides the Langbase class which is the main entry point
for interacting with the Langbase API.
"""

import os
from io import BytesIO
from typing import Any, BinaryIO, Dict, List, Optional, Union, overload

import requests

from .errors import APIError
from .request import Request
from .types import (
    ContentType,
    EmbeddingModel,
    FileProtocol,
    MemoryCreateResponse,
    MemoryDeleteDocResponse,
    MemoryDeleteResponse,
    MemoryListDocResponse,
    MemoryListResponse,
    MemoryRetrieveResponse,
    ThreadMessagesBaseResponse,
    ThreadsBaseResponse,
)
from .utils import clean_null_values, convert_document_to_request_files


class Langbase:
    """
    Client for the Langbase API.

    This class provides methods for interacting with all aspects of the Langbase API,
    including pipes, memories, tools, threads, and utilities.
    """

    def __init__(
        self, api_key: Optional[str] = None, base_url: str = "https://api.langbase.com"
    ):
        """
        Initialize the Langbase client.

        Args:
            api_key: The API key for authentication. If not provided, it will be read
                    from the LANGBASE_API_KEY environment variable.
            base_url: The base URL for the API.

        Raises:
            ValueError: If no API key is provided and LANGBASE_API_KEY is not set.
        """
        self.api_key = api_key or os.environ.get("LANGBASE_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "API key must be provided either as a parameter or through the LANGBASE_API_KEY environment variable"
            )

        self.base_url = base_url

        self.request = Request({"api_key": self.api_key, "base_url": self.base_url})

        # Initialize properties and methods
        self._init_pipes()
        self._init_memories()
        self._init_tools()
        self._init_threads()

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
                options = {"name": name, "description": description, **kwargs}
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
                options = {"name": name, **kwargs}
                return self.parent.request.post(
                    f"/v1/pipes/{name}", clean_null_values(options)
                )

            def run(
                self,
                name: Optional[str] = None,
                api_key: Optional[str] = None,
                messages: Optional[List[Dict[str, Any]]] = None,
                stream: Optional[
                    bool
                ] = None,  # Changed to Optional[bool] with default None
                **kwargs,
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
                    **kwargs,
                }

                # Only set stream in options if it's explicitly provided
                if stream is not None:
                    options["stream"] = stream

                # Create a new request instance if API key is provided
                request = self.parent.request
                if api_key:
                    request = Request(
                        {"api_key": api_key, "base_url": self.parent.base_url}
                    )

                headers = {}
                if "llm_key" in kwargs:
                    headers["LB-LLM-KEY"] = kwargs.pop("llm_key")

                # Pass the stream parameter to post method (which might be None)
                return request.post(
                    "/v1/pipes/run",
                    clean_null_values(options),
                    headers,
                    stream=stream if stream is not None else False,
                )

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

            def delete(
                self, memory_name: str, document_name: str
            ) -> MemoryDeleteDocResponse:
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

                Raises:
                    ValueError: If document type is unsupported
                    APIError: If the upload fails
                """
                try:
                    # Get signed URL for upload
                    response = self.parent.request.post(
                        "/v1/memory/documents",
                        {
                            "memoryName": memory_name,
                            "fileName": document_name,
                            "meta": meta or {},
                        },
                    )

                    upload_url = response.get("signedUrl")

                    # Convert document to appropriate format
                    if isinstance(document, str) and os.path.isfile(document):
                        with open(document, "rb") as f:
                            file_content = f.read()
                    elif isinstance(document, bytes):
                        file_content = document
                    elif isinstance(document, BytesIO) or hasattr(document, "read"):
                        file_content = document.read()
                        # Reset file pointer if possible
                        if hasattr(document, "seek"):
                            document.seek(0)
                    else:
                        raise ValueError(f"Unsupported document type: {type(document)}")

                    # Upload to signed URL
                    upload_response = requests.put(
                        upload_url,
                        headers={
                            "Authorization": f"Bearer {self.parent.api_key}",
                            "Content-Type": content_type,
                        },
                        data=file_content,
                    )

                    if not upload_response.ok:
                        raise APIError(
                            upload_response.status_code,
                            upload_response.text,
                            "Upload failed",
                            dict(upload_response.headers),
                        )

                    return upload_response

                except Exception as e:
                    if isinstance(e, APIError):
                        raise e
                    raise APIError(
                        None, str(e), "Error during document upload", None
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
                embedding_model: Optional[EmbeddingModel] = None,
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
                    "embedding_model": embedding_model,
                }
                return self.parent.request.post(
                    "/v1/memory", clean_null_values(options)
                )

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
                api_key: Optional[str] = None,
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
                api_key: Optional[str] = None,
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
                options = {"query": query, "service": service}

                if total_results is not None:
                    options["totalResults"] = total_results

                if domains is not None:
                    options["domains"] = domains

                headers = {}
                if api_key:
                    headers["LB-WEB-SEARCH-KEY"] = api_key

                return self.parent.request.post(
                    "/v1/tools/web-search", options, headers
                )

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
                messages: Optional[List[Dict[str, Any]]] = None,
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

                return self.parent.request.post(
                    "/v1/threads", clean_null_values(options)
                )

            def update(
                self, thread_id: str, metadata: Dict[str, str]
            ) -> ThreadsBaseResponse:
                """
                Update thread metadata.

                Args:
                    thread_id: ID of the thread to update
                    metadata: New metadata

                Returns:
                    Updated thread object
                """
                options = {"threadId": thread_id, "metadata": metadata}
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
                self, thread_id: str, messages: List[Dict[str, Any]]
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
                    f"/v1/threads/{thread_id}/messages", messages
                )

            def list(self, thread_id: str) -> List[ThreadMessagesBaseResponse]:
                """
                List messages in a thread.

                Args:
                    thread_id: ID of the thread

                Returns:
                    List of messages in the thread
                """
                return self.parent.request.get(f"/v1/threads/{thread_id}/messages")

        self.threads = Threads(self)

    def embed(
        self, chunks: List[str], embedding_model: Optional[EmbeddingModel] = None
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

    def chunker(
        self,
        content: str,
        chunk_max_length: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> List[str]:
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

        return self.request.post("/v1/chunker", json_data)

    def parser(
        self,
        document: Union[bytes, BytesIO, str, BinaryIO],
        document_name: str,
        content_type: ContentType,
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
            f"{self.base_url}/v1/parser",
            headers={"Authorization": f"Bearer {self.api_key}"},
            files=files,
        )

        if not response.ok:
            self.request.handle_error_response(response)

        return response.json()

    def agent_run(
        self,
        input: Union[str, List[Dict[str, Any]]],
        model: str,
        api_key: str,
        instructions: Optional[str] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        parallel_tool_calls: Optional[bool] = None,
        reasoning_effort: Optional[str] = None,
        max_completion_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        custom_model_params: Optional[Dict[str, Any]] = None,
        mcp_servers: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Run an agent with the specified parameters.

        Args:
            input: Either a string prompt or a list of messages
            model: The model to use for the agent
            api_key: API key for the LLM service
            instructions: Optional instructions for the agent
            top_p: Optional top-p sampling parameter
            max_tokens: Optional maximum tokens to generate
            temperature: Optional temperature parameter
            presence_penalty: Optional presence penalty parameter
            frequency_penalty: Optional frequency penalty parameter
            stop: Optional list of stop sequences
            tools: Optional list of tools for the agent
            tool_choice: Optional tool choice configuration ('auto', 'required', or tool spec)
            parallel_tool_calls: Optional flag for parallel tool execution
            reasoning_effort: Optional reasoning effort level
            max_completion_tokens: Optional maximum completion tokens
            response_format: Optional response format configuration
            custom_model_params: Optional custom model parameters
            mcp_servers: Optional list of MCP (Model Context Protocol) servers
            stream: Whether to stream the response (default: False)

        Returns:
            Either a dictionary with the agent's response or a streaming response

        Raises:
            ValueError: If required parameters are missing
            APIError: If the API request fails
        """
        if not api_key:
            raise ValueError("LLM API key is required to run this LLM.")

        options = {
            "input": input,
            "model": model,
            "apiKey": api_key,
            "instructions": instructions,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "stop": stop,
            "tools": tools,
            "tool_choice": tool_choice,
            "parallel_tool_calls": parallel_tool_calls,
            "reasoning_effort": reasoning_effort,
            "max_completion_tokens": max_completion_tokens,
            "response_format": response_format,
            "customModelParams": custom_model_params,
            "mcp_servers": mcp_servers,
        }

        # Only include stream if it's True
        if stream:
            options["stream"] = True

        # Clean null values from options
        options = clean_null_values(options)

        headers = {"LB-LLM-KEY": api_key}

        return self.request.post(
            "/v1/agent/run", options, headers=headers, stream=stream
        )
